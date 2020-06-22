from books.api.views import BookViewSet
from books.apps import BooksConfig
from rest_framework.routers import DefaultRouter

app_name = BooksConfig.name

router = DefaultRouter(trailing_slash=False)
router.register("books", BookViewSet, basename="books")
