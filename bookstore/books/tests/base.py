from django.test import TestCase

from authors.models import Author
from authors.tests.factories import AuthorFactory


class BaseBooksTests(TestCase):
    def setUp(self, *args, **kwargs):
        self.authors = AuthorFactory.create_batch(10)
        super().setUp(*args, **kwargs)

    def tearDown(self, *args, **kwargs):
        Author.objects.all().delete()
        super().setUp(*args, **kwargs)
