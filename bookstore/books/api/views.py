from books.api.filters import BookFilter
from books.api.serializers import BookSerializer
from books.models import Book
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet


class BookViewSet(ModelViewSet):
    """ViewSet for Book endpoints"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = BookFilter
    filterset_fields = ["name", "edition", "publication_year", "authors"]
