from enum import Enum

from django.db import models, transaction

from authors.models import Author
from books.models import Book
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.serializers import (
    IntegerField,
    ListSerializer,
    ModelSerializer,
)


class Operation(Enum):
    CREATE = "create"
    UPDATE = "update"


class CustomListSerializer(ListSerializer):
    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        iterable = data.all() if isinstance(data, models.Manager) else data
        if len(iterable) > 0 and isinstance(iterable[0], Author):
            return [self.child.to_representation(item.pk) for item in iterable]

        return [self.child.to_representation(item) for item in iterable]


class BookSerializer(ModelSerializer):
    """Serializer for Book data model"""

    authors = CustomListSerializer(child=IntegerField())

    class Meta:
        model = Book
        fields = ["id", "name", "edition", "publication_year", "authors"]

    def _raise_validation_error(self, message=None):
        """
        Helper method for raising ValidationError when handling a Bad Request
        It defaults to handling an empty list of authors
        """
        if not message:
            message = "Please provide at least one author id"
        raise ValidationError({"detail": message})

    def _raise_not_found_error(self, missing_ids):
        """
        Helper method for raising NotFound error when given authors
        are not found"""
        message = (
            f"Failed to find authors with the following ids: "
            f"{', '.join([str(_id) for _id in missing_ids])}"
        )
        raise NotFound(detail=message)

    @transaction.atomic
    def _update_authors(self, book, authors_ids, operation=Operation.CREATE):
        """Helper method for updating authors relations on a given book"""
        authors = Author.objects.filter(pk__in=authors_ids)
        if authors.count() == len(authors_ids):
            if operation == Operation.UPDATE:
                book.authors.clear()
            for author in authors:
                book.authors.add(author)
            book.save()
        else:
            existing_authors = {author.pk for author in authors}
            missing_authors = set(authors_ids) - existing_authors
            self._raise_not_found_error(missing_authors)

        return book

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates a Book record with given attributes and authors if
        given authors exist in the database
        """
        authors_ids = validated_data.pop("authors")
        if not authors_ids:
            self._raise_validation_error()

        book = Book.objects.create(**validated_data)
        return self._update_authors(book, authors_ids)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates or partially updates a Book record with given
        attributes and authors
        """
        authors_ids = validated_data.pop("authors", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()

        if isinstance(authors_ids, list):
            if not authors_ids:
                self._raise_validation_error()
            else:
                return self._update_authors(
                    instance, authors_ids, Operation.UPDATE
                )

        return instance
