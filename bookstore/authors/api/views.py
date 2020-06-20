from authors.api.filters import AuthorFilter
from authors.api.serializers import AuthorSerializer
from authors.models import Author
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet


class AuthorViewSet(ListModelMixin, GenericViewSet):
    """ViewSet for Authors' list endpoint"""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filter_class = AuthorFilter
    filterset_fields = ["name"]
