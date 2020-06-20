from authors.models import Author
from django_filters import CharFilter, FilterSet


class AuthorFilter(FilterSet):
    name = CharFilter(method="name_filter")

    class Meta:
        model = Author
        fields = ["name"]

    def name_filter(self, queryset, name, value):
        if value:
            return queryset.filter(name__icontains=value)
        return queryset
