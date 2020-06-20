import os

from django.test import TestCase

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(APP_DIR, "tests/fixtures")
EXPECTED_NAMES = set()


class TestAuthorsBase(TestCase):
    """Common base class for testing authors related cases"""

    @classmethod
    def setUpClass(cls):
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        with open(filepath, "r", encoding="utf-8") as csv_file:
            next(csv_file, None)
            for line in csv_file:
                EXPECTED_NAMES.add(line.rstrip())
        super().setUpClass()
