from contextlib import closing
from typing import IO, Set

from django.db import connection

from authors.models import Author


def import_authors(names_set: Set) -> None:
    """Helper function for importing authors into database"""
    authors = [Author(name=name) for name in names_set]
    
    Author.objects.bulk_create(authors, ignore_conflicts=True)


def import_authors_faster(data: IO) -> None:
    """
    Helper function for importing authors into database using postgres 
    'copy_from' utility function for a faster performance
    """
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=data,
            table="authors_author",
            columns=("name",)
        )
