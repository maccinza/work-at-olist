from django.db import models


class Author(models.Model):
    """Model definition for Author"""

    name = models.CharField(
        max_length=200, null=False, blank=False, unique=True
    )

    class Meta:
        """Meta definition for Author"""

        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        """Unicode representation of Author"""
        return self.name
