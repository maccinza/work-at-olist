from enum import Enum

from django.db import transaction

from authors.models import Author
from books.models import Book
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.serializers import (
    CharField,
    ListSerializer,
    ModelSerializer,
)


class Operation(Enum):
    CREATE = "create"
    UPDATE = "update"


class BookSerializer(ModelSerializer):
    """Serializer for Book data model"""

    authors = ListSerializer(child=CharField())

    class Meta:
        model = Book
        fields = ["id", "name", "edition", "publication_year", "authors"]

    def _raise_validation_error(self, message=None):
        """
        Helper method for raising ValidationError when handling a Bad Request
        It defaults to handling an empty list of authors
        """
        if not message:
            message = "Please provide at least one author name"
        raise ValidationError({"detail": message})

    def _raise_not_found_error(self, missing_names):
        """
        Helper method for raising NotFound error when given authors
        are not found"""
        message = (
            f"Failed to find some authors: " f"{', '.join(missing_names)}"
        )
        raise NotFound(detail=message)

    @transaction.atomic
    def _update_authors(self, book, authors_names, operation=Operation.CREATE):
        """Helper method for updating authors relations on a given book"""
        authors = Author.objects.filter(name__in=authors_names)
        if authors.count() == len(authors_names):
            if operation == Operation.UPDATE:
                book.authors.clear()
            for author in authors:
                book.authors.add(author)
            book.save()
        else:
            existing_names = {author.name for author in authors}
            missing_names = set(authors_names) - existing_names
            self._raise_not_found_error(missing_names)

        return book

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates a Book record with given attributes and authors if
        given authors exist in the database
        """
        authors_names = validated_data.pop("authors")
        if not authors_names:
            self._raise_validation_error()

        book = Book.objects.create(**validated_data)
        return self._update_authors(book, authors_names)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates or partially updates a Book record with given
        attributes and authors
        """
        authors_names = validated_data.pop("authors", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()

        if isinstance(authors_names, list):
            if not authors_names:
                self._raise_validation_error()
            else:
                return self._update_authors(
                    instance, authors_names, Operation.UPDATE
                )

        return instance
