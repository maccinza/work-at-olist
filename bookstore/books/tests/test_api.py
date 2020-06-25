import json

from django.conf import settings
from django.urls import reverse

from books.models import Book
from books.tests.base import BaseBooksTests, get_unique_from_sequence
from books.tests.factories import BookFactory
from rest_framework import status
from rest_framework.test import APITestCase


class BooksAPITests(BaseBooksTests, APITestCase):
    def test_create_book(self):
        """
        It creates a Book with the given parameter values through the
        API endpoint
        """
        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        url = reverse("books-list")
        parameters = {
            "name": "Book Test I",
            "edition": 1,
            "publication_year": 2000,
            "authors": sorted([author.pk for author in authors]),
        }

        response = self.client.post(
            url, data=json.dumps(parameters), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        response_data = response.json()
        self.assertIn("id", response_data)
        response_data.pop("id")
        self.assertEqual(response_data, parameters)

    def test_create_book_invalid_edition(self):
        """
        It returns an error when trying to create a Book through the API
        endpoint with an invalid edition within the given parameters values
        """
        expected_errors = {
            "code": "1000",
            "errors": [
                {
                    "code": "2071",
                    "field": "edition",
                    "message": (
                        f"Ensure this value is greater than or equal to "
                        f"{settings.MIN_EDITION}."
                    ),
                }
            ],
            "message": "Validation Failed",
        }

        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        url = reverse("books-list")
        parameters = {
            "name": "Book Test I",
            "edition": 0,
            "publication_year": 2000,
            "authors": sorted([author.pk for author in authors]),
        }

        response = self.client.post(
            url, data=json.dumps(parameters), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

        response_data = response.json()
        self.assertEqual(response_data, expected_errors)

    def test_create_book_invalid_publication_year(self):
        """
        It returns an error when trying to create a Book through the API
        endpoint with an invalid publication_year within the given parameters
        values
        """
        expected_errors = {
            "code": "1000",
            "errors": [
                {
                    "code": "2071",
                    "field": "publication_year",
                    "message": (
                        f"Ensure this value is greater than or equal to "
                        f"{settings.MIN_PUBLICATION_YEAR}."
                    ),
                }
            ],
            "message": "Validation Failed",
        }
        self.assertEqual(Book.objects.count(), 0)
        authors = get_unique_from_sequence(self.authors, 2)
        url = reverse("books-list")
        parameters = {
            "name": "Book Test I",
            "edition": 1,
            "publication_year": settings.MIN_PUBLICATION_YEAR - 10,
            "authors": sorted([author.pk for author in authors]),
        }

        response = self.client.post(
            url, data=json.dumps(parameters), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

        response_data = response.json()
        self.assertEqual(response_data, expected_errors)

    def test_create_book_without_authors(self):
        """
        It returns an error when trying to create a Book through the API
        endpoint without any authors within the given parameters
        values
        """
        expected_errors = {
            "code": None,
            "message": "Please provide at least one author id",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

        self.assertEqual(Book.objects.count(), 0)
        url = reverse("books-list")
        parameters = {
            "name": "Book Test I",
            "edition": 1,
            "publication_year": 2000,
            "authors": [],
        }

        response = self.client.post(
            url, data=json.dumps(parameters), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)

        response_data = response.json()
        self.assertEqual(response_data, expected_errors)

    def test_create_duplicated_book(self):
        """
        It returns an error when trying to create a Book through the API
        endpoint without any authors within the given parameters
        values
        """
        authors = get_unique_from_sequence(self.authors, 2)
        book_name = "Book Test I"
        edition = 1
        publication_year = 2000

        BookFactory.create(
            name=book_name,
            edition=edition,
            publication_year=publication_year,
            authors=authors,
        )

        parameters = {
            "name": book_name,
            "edition": edition,
            "publication_year": publication_year,
            "authors": sorted([author.pk for author in authors]),
        }

        expected_errors = {
            "code": "1000",
            "errors": [
                {
                    "code": "None",
                    "field": "None",
                    "message": (
                        "The fields name, edition, publication_year must "
                        "make a unique set."
                    ),
                }
            ],
            "message": "Validation Failed",
        }

        self.assertEqual(Book.objects.count(), 1)
        url = reverse("books-list")
        response = self.client.post(
            url, data=json.dumps(parameters), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 1)

        response_data = response.json()
        self.assertEqual(response_data, expected_errors)
