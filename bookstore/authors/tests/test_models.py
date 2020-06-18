from django.db import IntegrityError, transaction
from django.test import TestCase

from authors.models import Author


class TestAuthor(TestCase):
    def test_create_author(self):
        """It is possible to create an author inserting it into the db"""

        self.assertEqual(Author.objects.count(), 0)

        author_name = "John Doe"
        author = Author(name=author_name)
        author.save()

        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(Author.objects.first().name, author_name)

    def test_delete_author(self):
        """It is possible to delete an author by their id"""

        author = Author.objects.create(name="John Doe")
        self.assertEqual(Author.objects.count(), 1)
        Author.objects.filter(id=author.id).delete()
        self.assertEqual(Author.objects.count(), 0)

    def test_update_author(self):
        """It is possible to update an author name"""

        author_name = "Jane Doe"
        author = Author.objects.create(name="John Doe")
        self.assertEqual(Author.objects.count(), 1)
        author.name = author_name
        author.save()
        self.assertEqual(Author.objects.count(), 1)
        self.assertEqual(Author.objects.first().name, author_name)

    def test_filter_author_by_name(self):
        """It is possible to filter author by their name"""

        author_name = "Jane Doe"
        Author.objects.create(name="John Doe")
        Author.objects.create(name=author_name)
        self.assertEqual(Author.objects.count(), 2)
        filtered_author = Author.objects.filter(name=author_name)
        self.assertEqual(len(filtered_author), 1)
        self.assertEqual(filtered_author.first().name, author_name)

    def test_duplicated_author_error(self):
        """Trying to create authors with the same name raises an IntegrityError"""

        author_name = "John Doe"
        expected_message = (
            f"duplicate key value violates unique constraint "
            f'"authors_author_name_key"\nDETAIL:  Key (name)='
            f"({author_name}) already exists.\n"
        )

        Author.objects.create(name=author_name)
        self.assertEqual(Author.objects.count(), 1)
        author = Author(name=author_name)

        with self.assertRaises(IntegrityError) as raised:
            with transaction.atomic():
                author.save()
        self.assertEqual(str(raised.exception), expected_message)
        self.assertEqual(Author.objects.count(), 1)
