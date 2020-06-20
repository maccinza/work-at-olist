from unittest.mock import patch

from django.urls import reverse

from authors.tests.base import EXPECTED_NAMES, TestAuthorsBase
from authors.utils import import_authors
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.test import APITestCase

TEST_SERVER = "http://testserver"


class AuthorsAPITests(TestAuthorsBase, APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import_authors(EXPECTED_NAMES)

    def test_authors_list(self):
        """
        It retrieves all authors listing them in alphabetical order
        on a single page
        """
        url = reverse("authors-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], len(EXPECTED_NAMES))
        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)
        self.assertIn("results", response_data)

        authors = [author["name"] for author in response_data["results"]]
        self.assertEqual(authors, sorted(EXPECTED_NAMES))

    def test_paginated_authors_list(self):
        """
        It retrieves all authors listing them in alphabetical order
        on a paginated response
        """
        url = reverse("authors-list")
        with patch.object(PageNumberPagination, "page_size", new=20):
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], len(EXPECTED_NAMES))

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], f"{TEST_SERVER}{url}?page=2")
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)

        authors = [author["name"] for author in response_data["results"]]
        self.assertEqual(authors, sorted(EXPECTED_NAMES)[:20])

        next_url = response_data["next"]
        with patch.object(PageNumberPagination, "page_size", new=20):
            response = self.client.get(next_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], len(EXPECTED_NAMES))

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], f"{TEST_SERVER}{url}")

        authors = [author["name"] for author in response_data["results"]]
        self.assertEqual(authors, sorted(EXPECTED_NAMES)[20:])

    def test_authors_exact_match(self):
        """
        It returns an author when the search is an exact match of the
        author's name
        """
        author_name = "Sarah Carter"
        url = reverse("authors-list")
        response = self.client.get(url, {"name": author_name})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 1)

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)
        self.assertIn("results", response_data)
        self.assertEqual(response_data["results"][0]["name"], author_name)

    def test_authors_partial_match(self):
        """
        It returns authors when the search is a partial match of their names
        """
        author_search = "sarah"
        expected_authors = ["Sarah Carter", "Sarah Morgan"]
        url = reverse("authors-list")
        response = self.client.get(url, {"name": author_search})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 2)

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)
        self.assertIn("results", response_data)

        self.assertEqual(
            [author["name"] for author in response_data["results"]],
            expected_authors,
        )

    def test_authors_paginated_partial_match(self):
        """
        It returns paginated response with authors when the search is a
        partial match of their names
        """
        author_search = "sarah"
        expected_authors = ["Sarah Carter", "Sarah Morgan"]
        url = reverse("authors-list")
        with patch.object(PageNumberPagination, "page_size", new=1):
            response = self.client.get(url, {"name": author_search})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 2)

        self.assertIn("next", response_data)
        self.assertEqual(
            response_data["next"],
            f"{TEST_SERVER}{url}?name={author_search}&page=2",
        )
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)

        authors = [author["name"] for author in response_data["results"]]
        self.assertEqual(authors, [expected_authors[0]])

        next_url = response_data["next"]
        with patch.object(PageNumberPagination, "page_size", new=1):
            response = self.client.get(next_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 2)

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(
            response_data["previous"],
            f"{TEST_SERVER}{url}?name={author_search}",
        )

        authors = [author["name"] for author in response_data["results"]]
        self.assertEqual(authors, [expected_authors[1]])

    def test_authors_search_no_match(self):
        """
        It returns empty results when the name search does not match any
        authors
        """
        author_search = "lucas"
        url = reverse("authors-list")
        response = self.client.get(url, {"name": author_search})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertIn("count", response_data)
        self.assertEqual(response_data["count"], 0)

        self.assertIn("next", response_data)
        self.assertEqual(response_data["next"], None)
        self.assertIn("previous", response_data)
        self.assertEqual(response_data["previous"], None)
        self.assertIn("results", response_data)
        self.assertEqual(response_data["results"], [])
