from authors.models import Author
from factory import Faker
from factory.django import DjangoModelFactory


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    name = Faker("name")
