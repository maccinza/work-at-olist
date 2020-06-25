from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError

from books.models import Book
from books.tests.base import BaseBooksTests, get_unique_from_sequence
from books.tests.factories import BookFactory


class TestBook(BaseBooksTests):
    def test_create_book(self):
        """It is possible to create a Book and insert it into the database"""
        self.assertEqual(Book.objects.count(), 0)

        authors = get_unique_from_sequence(self.authors, 2)
        book = BookFactory.create(authors=authors)
        retrieved_book = Book.objects.first()

        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(retrieved_book, book)
        self.assertEqual(retrieved_book.authors.count(), len(authors))
        for author in retrieved_book.authors.all():
            self.assertIn(author, authors)

    def test_create_book_invalid_edition(self):
        """
        It is not possible to create a Book with a edition value below
        the permitted values
        """
        expected_errors = {
            "edition": [
                f"Ensure this value is greater than or equal to "
                f"{settings.MIN_EDITION}."
            ]
        }

        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        with self.assertRaises(ValidationError) as raised:
            BookFactory.create(authors=authors, edition=0)
        self.assertEqual(raised.exception.message_dict, expected_errors)
        self.assertEqual(Book.objects.count(), 0)

    def test_create_book_invalid_publication_year(self):
        """
        It is not possible to create a book with a publication year either
        below or above the permitted values
        """
        expected_errors = {
            "publication_year": [
                f"Ensure this value is greater than or equal to "
                f"{settings.MIN_PUBLICATION_YEAR}."
            ]
        }

        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        with self.assertRaises(ValidationError) as raised:
            BookFactory.create(authors=authors, publication_year=1200)
        self.assertEqual(raised.exception.message_dict, expected_errors)
        self.assertEqual(Book.objects.count(), 0)

        expected_errors = {
            "publication_year": [
                f"Ensure this value is less than or equal to "
                f"{date.today().year + 1}."
            ]
        }

        with self.assertRaises(ValidationError) as raised:
            BookFactory.create(
                authors=authors, publication_year=date.today().year + 10
            )
        self.assertEqual(raised.exception.message_dict, expected_errors)

    def test_create_duplicate_book(self):
        """
        It is not possible to create a duplicate Book, with the same name,
        edition, and publication_year
        """
        expected_errors = {
            "__all__": [
                "Book with this Name, Edition and Publication year "
                "already exists."
            ]
        }

        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        book_parameters = {
            "name": "Duplicate Book",
            "edition": 1,
            "publication_year": 2000,
            "authors": authors,
        }
        BookFactory.create(**book_parameters)
        self.assertEqual(Book.objects.count(), 1)
        with self.assertRaises(ValidationError) as raised:
            BookFactory.create(**book_parameters)

        self.assertEqual(raised.exception.message_dict, expected_errors)
        self.assertEqual(Book.objects.count(), 1)
