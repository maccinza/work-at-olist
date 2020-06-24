from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from books.validators import max_value_year_validation


class Book(models.Model):
    """Model definition for Book"""

    name = models.CharField(max_length=255, null=False, blank=False)
    edition = models.PositiveIntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(settings.MIN_EDITION)],
    )
    publication_year = models.PositiveIntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(settings.MIN_PUBLICATION_YEAR),
            max_value_year_validation,
        ],
    )
    authors = models.ManyToManyField("authors.Author", related_name="books")

    def __str__(self):
        """Unicode representation of Book"""
        return f"{self.name} ({self.edition} - {self.publication_year})"

    def save(self, *args, **kwargs):
        """Custom save method to enforce validation"""
        self.full_clean()
        return super().save(*args, **kwargs)
