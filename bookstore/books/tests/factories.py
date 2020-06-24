from datetime import date

from books.models import Book
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger, FuzzyText


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    name = FuzzyText()
    edition = FuzzyInteger(1, 40)
    publication_year = FuzzyInteger(1800, date.today().year)

    @post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for author in extracted:
                self.authors.add(author)
            self.save()
