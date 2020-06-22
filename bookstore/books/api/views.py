from books.api.serializers import BookSerializer
from books.models import Book
from rest_framework.viewsets import ModelViewSet


class BookViewSet(ModelViewSet):
    """ViewSet for Book endpoints"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
