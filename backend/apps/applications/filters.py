import django_filters

from apps.applications.models import JobApplication


class JobApplicationFilter(django_filters.FilterSet):

    company = django_filters.NumberFilter(
        field_name="company_id",
    )

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="iexact",
    )

    employment_type = django_filters.CharFilter(
        field_name="employment_type",
        lookup_expr="iexact",
    )

    work_mode = django_filters.CharFilter(
        field_name="work_mode",
        lookup_expr="iexact",
    )

    location = django_filters.CharFilter(
        field_name="location",
        lookup_expr="icontains",
    )

    applied_after = django_filters.DateFilter(
        field_name="applied_date",
        lookup_expr="gte",
    )

    applied_before = django_filters.DateFilter(
        field_name="applied_date",
        lookup_expr="lte",
    )

    deadline_after = django_filters.DateFilter(
        field_name="deadline",
        lookup_expr="gte",
    )

    deadline_before = django_filters.DateFilter(
        field_name="deadline",
        lookup_expr="lte",
    )

    minimum_salary = django_filters.NumberFilter(
        field_name="salary_max",
        lookup_expr="gte",
    )

    maximum_salary = django_filters.NumberFilter(
        field_name="salary_min",
        lookup_expr="lte",
    )

    class Meta:
        model = JobApplication
        fields = [
            "company",
            "status",
            "employment_type",
            "work_mode",
            "location",
            "applied_after",
            "applied_before",
            "deadline_after",
            "deadline_before",
            "minimum_salary",
            "maximum_salary",
        ]