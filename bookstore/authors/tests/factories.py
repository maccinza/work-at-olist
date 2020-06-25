from authors.models import Author
from factory import Faker
from factory.django import DjangoModelFactory


class AuthorFactory(DjangoModelFactory):
    name = Faker("name")

    class Meta:
        model = Author
