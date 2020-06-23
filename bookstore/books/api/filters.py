from books.models import Book
from django_filters import CharFilter, FilterSet, NumberFilter
from rest_framework.serializers import ValidationError


class BookFilter(FilterSet):
    """Filtering implementation for Book data"""

    name = CharFilter(method="name_filter")
    edition = NumberFilter(method="edition_filter")
    publication_year = NumberFilter(method="publication_year_filter")
    authors = CharFilter(method="authors_filter")

    class Meta:
        model = Book
        fields = ["name", "edition", "publication_year", "authors"]

    def name_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(name__icontains=value)
        return queryset

    def edition_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(edition__exact=value)
        return queryset

    def publication_year_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(publication_year__exact=value)
        return queryset

    def authors_filter(self, queryset, field_name, value):
        if value:
            pks = value.split(",")
            if not all(item.isdigit() for item in pks):
                raise ValidationError(
                    {"detail": f"Not all values in [{value}] are integers"}
                )
            pks = [int(pk) for pk in pks]
            return queryset.filter(authors__in=pks)
        return queryset
