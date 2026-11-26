from datetime import date, timedelta
from calendar import monthrange

from django.db.models import Count, Q, Min
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone

from apps.applications.models import JobApplication


ACTIVE_STATUSES = ["applied", "assessment", "interview"]

STATUS_VALUES = [
    "applied",
    "assessment",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
]

FUNNEL_STATUSES = ["applied", "assessment", "interview", "offer"]


def get_month_start(months_ago=0):
    today = timezone.localdate()
    month_index = today.year * 12 + today.month - 1 - months_ago
    year = month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def get_dashboard_summary(user):
    queryset = JobApplication.objects.filter(user=user)

    metrics = queryset.aggregate(
        total_applications=Count("id"),
        active_applications=Count(
            "id", filter=Q(status__in=ACTIVE_STATUSES)
        ),
        interviews=Count(
            "id", filter=Q(status__in=["interview", "offer"])
        ),
        offers=Count("id", filter=Q(status="offer")),
        rejections=Count("id", filter=Q(status="rejected")),
        withdrawals=Count("id", filter=Q(status="withdrawn")),
    )

    total = metrics["total_applications"]

    metrics["interview_conversion_rate"] = (
        round(metrics["interviews"] / total * 100, 2)
        if total else 0.0
    )
    metrics["offer_conversion_rate"] = (
        round(metrics["offers"] / total * 100, 2)
        if total else 0.0
    )

    return metrics


def get_status_distribution(user):
    queryset = JobApplication.objects.filter(user=user)

    counts = {
        item["status"]: item["count"]
        for item in queryset.values("status").annotate(
            count=Count("id")
        )
    }

    return [
        {"status": status, "count": counts.get(status, 0)}
        for status in STATUS_VALUES
    ]


def get_employment_type_distribution(user):
    return list(
        JobApplication.objects.filter(user=user)
        .values("employment_type")
        .annotate(count=Count("id"))
        .order_by("employment_type")
    )


def get_monthly_application_trends(user, months=6):
    start_date = get_month_start(months - 1)

    rows = (
        JobApplication.objects.filter(
            user=user,
            applied_date__gte=start_date,
        )
        .annotate(month=TruncMonth("applied_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    counts = {
        row["month"].strftime("%Y-%m"): row["count"]
        for row in rows
        if row["month"] is not None
    }

    results = []

    for months_ago in reversed(range(months)):
        month = get_month_start(months_ago)
        key = month.strftime("%Y-%m")
        results.append({
            "month": key,
            "count": counts.get(key, 0),
        })

    return results


def _base_analytics_queryset(user, start_date, end_date):
    return JobApplication.objects.filter(
        user=user,
        applied_date__gte=start_date,
        applied_date__lte=end_date,
    )


def _count_reached_stage(queryset, stage):
    """
    Count unique applications that have reached a stage.

    Current status is included because older applications may not have
    complete status-history records.
    """
    return queryset.filter(
        Q(status=stage) |
        Q(status_history__new_status=stage)
    ).distinct().count()


def _get_funnel(queryset):
    applied = queryset.count()
    assessment = _count_reached_stage(queryset, "assessment")
    interview = _count_reached_stage(queryset, "interview")
    offer = _count_reached_stage(queryset, "offer")

    stages = [
        ("applied", applied),
        ("assessment", assessment),
        ("interview", interview),
        ("offer", offer),
    ]

    results = []

    previous_count = None

    for stage, count in stages:
        results.append({
            "stage": stage,
            "count": count,
            "conversion_from_previous": (
                round(count / previous_count * 100, 2)
                if previous_count else 0.0
            ),
        })
        previous_count = count

    return results


def _normalize_period(value):
    if hasattr(value, "date"):
        return value.date()
    return value


def _get_trend_queryset(queryset, granularity):
    if granularity == "daily":
        trunc_function = TruncDate("applied_date")
    elif granularity == "weekly":
        trunc_function = TruncWeek("applied_date")
    else:
        trunc_function = TruncMonth("applied_date")

    return (
        queryset.annotate(period=trunc_function)
        .values("period")
        .annotate(count=Count("id"))
        .order_by("period")
    )


def _get_period_start(value, granularity):
    if granularity == "daily":
        return value
    if granularity == "weekly":
        return value - timedelta(days=value.weekday())
    return date(value.year, value.month, 1)


def _next_period(value, granularity):
    if granularity == "daily":
        return value + timedelta(days=1)

    if granularity == "weekly":
        return value + timedelta(days=7)

    year = value.year + (1 if value.month == 12 else 0)
    month = 1 if value.month == 12 else value.month + 1
    return date(year, month, 1)


def _get_trends(queryset, start_date, end_date, granularity):
    rows = _get_trend_queryset(queryset, granularity)

    counts = {
        _normalize_period(row["period"]): row["count"]
        for row in rows
        if row["period"] is not None
    }

    current = _get_period_start(start_date, granularity)
    final_period = _get_period_start(end_date, granularity)

    results = []

    while current <= final_period:
        results.append({
            "period": current.isoformat(),
            "count": counts.get(current, 0),
        })
        current = _next_period(current, granularity)

    return results


def _get_company_analytics(queryset):
    return list(
        queryset.values("company_id", "company__name")
        .annotate(count=Count("id"))
        .order_by("-count", "company__name")[:10]
    )

def _get_response_metrics(queryset):
    total = queryset.count()

    current_outcomes = queryset.aggregate(
        interviews=Count(
            "id",
            filter=Q(status__in=["interview", "offer"]),
        ),
        offers=Count("id", filter=Q(status="offer")),
        rejections=Count("id", filter=Q(status="rejected")),
        withdrawals=Count("id", filter=Q(status="withdrawn")),
    )

    response_rows = (
        queryset.filter(
            status_history__new_status__in=[
                "assessment",
                "interview",
                "offer",
                "rejected",
            ]
        )
        .values("id", "applied_date")
        .annotate(first_response=Min("status_history__changed_at"))
    )

    response_days = []

    for row in response_rows:
        if row["first_response"]:
            response_date = timezone.localtime(
                row["first_response"]
            ).date()

            days = (response_date - row["applied_date"]).days

            if days >= 0:
                response_days.append(days)

    average_response_days = (
        round(sum(response_days) / len(response_days), 2)
        if response_days
        else None
    )

    return {
        "total_applications": total,
        "interviews": current_outcomes["interviews"],
        "offers": current_outcomes["offers"],
        "rejections": current_outcomes["rejections"],
        "withdrawals": current_outcomes["withdrawals"],
        "interview_rate": (
            round(current_outcomes["interviews"] / total * 100, 2)
            if total else 0.0
        ),
        "offer_rate": (
            round(current_outcomes["offers"] / total * 100, 2)
            if total else 0.0
        ),
        "rejection_rate": (
            round(current_outcomes["rejections"] / total * 100, 2)
            if total else 0.0
        ),
        "average_response_days": average_response_days,
        "applications_with_response": len(response_days),
    }


def get_advanced_analytics(
    user,
    start_date,
    end_date,
    granularity="weekly",
):
    queryset = _base_analytics_queryset(
        user, start_date, end_date
    )

    status_distribution = list(
        queryset.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    employment_distribution = list(
        queryset.values("employment_type")
        .annotate(count=Count("id"))
        .order_by("employment_type")
    )

    return {
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "granularity": granularity,
        "overview": _get_response_metrics(queryset),
        "funnel": _get_funnel(queryset),
        "trends": _get_trends(
            queryset, start_date, end_date, granularity
        ),
        "company_analytics": _get_company_analytics(queryset),
        "status_distribution": status_distribution,
        "employment_type_distribution": employment_distribution,
    }


def get_analytics_export_queryset(user, start_date, end_date):
    return (
        _base_analytics_queryset(user, start_date, end_date)
        .select_related("company")
        .order_by("-applied_date", "-created_at")
    )