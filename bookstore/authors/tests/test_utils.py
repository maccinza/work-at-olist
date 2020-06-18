from io import StringIO

from django.test import TestCase

from authors.models import Author
from authors.utils import import_authors, import_authors_faster

AUTHORS_NAMES = {"John Doe", "Jane Doe"}


class TestImportAuthorUtils(TestCase):
    def test_import_authors(self):
        """It is able to import the given authors into the database"""
        self.assertEqual(Author.objects.count(), 0)
        import_authors(AUTHORS_NAMES)
        self.assertEqual(Author.objects.count(), len(AUTHORS_NAMES))
        for author in Author.objects.all():
            self.assertIn(author.name, AUTHORS_NAMES)

    def test_import_authors_faster(self):
        """
        It is able to import the given authors into the database using
        postgres 'copy_from' utility function
        """
        data = StringIO("\n".join(AUTHORS_NAMES))
        self.assertEqual(Author.objects.count(), 0)
        import_authors_faster(data)
        self.assertEqual(Author.objects.count(), len(AUTHORS_NAMES))
        for author in Author.objects.all():
            self.assertIn(author.name, AUTHORS_NAMES)
