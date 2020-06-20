from authors.api.views import AuthorViewSet
from authors.apps import AuthorsConfig
from rest_framework.routers import DefaultRouter

app_name = AuthorsConfig.name

router = DefaultRouter(trailing_slash=False)
router.register("authors", AuthorViewSet, basename="authors")
