import pytest

from apps.companies.models import Company


@pytest.mark.django_db
class TestCompanyModel:

    def test_create_company(self):

        company = Company.objects.create(
            name="Google",
            industry="Technology",
            location="Bangalore",
        )

        assert company.id is not None
        assert company.name == "Google"
        assert company.slug == "google"

    def test_duplicate_company_names_get_unique_slugs(self):

        first = Company.objects.create(
            name="Microsoft",
        )

        second = Company.objects.create(
            name="Microsoft",
        )

        assert first.slug == "microsoft"
        assert second.slug == "microsoft-1"

    def test_company_string_representation(self):

        company = Company.objects.create(
            name="Amazon",
        )

        assert str(company) == "Amazon"