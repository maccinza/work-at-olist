import random

from django.test import TestCase

from authors.models import Author
from authors.tests.factories import AuthorFactory


class BaseBooksTests(TestCase):
    def setUp(self, *args, **kwargs):
        self.authors = AuthorFactory.create_batch(15)
        super().setUp(*args, **kwargs)

    def tearDown(self, *args, **kwargs):
        self.authors = []
        Author.objects.all().delete()
        super().tearDown(*args, **kwargs)


def get_unique_from_sequence(sequence, quantity):
    selected = []

    while len(selected) < quantity:
        author = random.choice(sequence)
        if author not in selected:
            selected.append(author)

    return selected
