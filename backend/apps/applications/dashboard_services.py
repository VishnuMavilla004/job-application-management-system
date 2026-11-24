from datetime import date

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from apps.applications.models import JobApplication

from django.utils import timezone


ACTIVE_STATUSES = [
    "applied",
    "assessment",
    "interview",
]

STATUS_VALUES = [
    "applied",
    "assessment",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
]


def get_month_start(months_ago=0):
    """
    Return the first day of the month, months_ago months in the past.
    """

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
            "id",
            filter=Q(status__in=ACTIVE_STATUSES),
        ),
        interviews=Count(
            "id",
            filter=Q(status__in=["interview", "offer"]),
        ),
        offers=Count(
            "id",
            filter=Q(status="offer"),
        ),
        rejections=Count(
            "id",
            filter=Q(status="rejected"),
        ),
        withdrawals=Count(
            "id",
            filter=Q(status="withdrawn"),
        ),
    )

    total = metrics["total_applications"]

    metrics["interview_conversion_rate"] = round(
        metrics["interviews"] / total * 100,
        2,
    ) if total else 0.0

    metrics["offer_conversion_rate"] = round(
        metrics["offers"] / total * 100,
        2,
    ) if total else 0.0

    return metrics


def get_status_distribution(user):
    queryset = JobApplication.objects.filter(user=user)

    counts = {
        item["status"]: item["count"]
        for item in (
            queryset.values("status")
            .annotate(count=Count("id"))
        )
    }

    return [
        {
            "status": status,
            "count": counts.get(status, 0),
        }
        for status in STATUS_VALUES
    ]


def get_employment_type_distribution(user):
    queryset = JobApplication.objects.filter(user=user)

    return list(
        queryset.values("employment_type")
        .annotate(count=Count("id"))
        .order_by("employment_type")
    )


def get_monthly_application_trends(user, months=6):
    """
    Return monthly application counts, including months with zero records.
    """

    start_date = get_month_start(months - 1)

    rows = (
        JobApplication.objects
        .filter(
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