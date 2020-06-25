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
    """
    Best effort helper function to select `quantity` unique elements
    from `sequence`. If it fails to select the given quantity, returns
    after 5 retries
    """
    selected = []
    max_retries = 5

    retries = 0
    while len(selected) < quantity and retries < max_retries:
        author = random.choice(sequence)
        if author not in selected:
            selected.append(author)
        else:
            retries += 1

    return selected
