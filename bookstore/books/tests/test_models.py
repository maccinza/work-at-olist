import random

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from authors.tests.factories import AuthorFactory
from books.models import Book
from books.tests.factories import BookFactory


class TestBook(TestCase):
    def setUp(self, *args, **kwargs):
        self.authors = AuthorFactory.create_batch(10)
        super().setUp(*args, **kwargs)

    def test_create_book(self):
        """It is possible to create a Book and insert it into the database"""
        self.assertEqual(Book.objects.count(), 0)
        authors = random.choices(self.authors, k=2)
        book = BookFactory.create(authors=authors)
        retrieved_book = Book.objects.first()
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(retrieved_book, book)
        self.assertEqual(retrieved_book.authors.all().count(), len(authors))
        for author in retrieved_book.authors.all():
            self.assertIn(author, authors)

    def test_create_book_invalid_edition(self):
        """
        It is not possible to create a Book with a edition value below
        the expected
        """
        expected_errors = {
            "edition": [
                f"Ensure this value is greater than or equal to "
                f"{settings.MIN_EDITION}."
            ]
        }

        self.assertEqual(Book.objects.count(), 0)
        authors = random.choices(self.authors, k=2)
        with self.assertRaises(ValidationError) as raised:
            BookFactory.create(authors=authors, edition=0)
        self.assertEqual(raised.exception.message_dict, expected_errors)
