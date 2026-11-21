from django.core.validators import URLValidator
from django.db import models
from django.utils.text import slugify


class Company(models.Model):

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    industry = models.CharField(
        max_length=100,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "companies"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["name"],
                name="company_name_idx",
            ),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            counter = 1

            while Company.objects.filter(
                slug=candidate
            ).exclude(pk=self.pk).exists():

                candidate = f"{base_slug}-{counter}"
                counter += 1

            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name