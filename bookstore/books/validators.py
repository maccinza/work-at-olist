from django.core.validators import MaxValueValidator

from bookstore.common import current_year


def max_value_year_validation(value):
    return MaxValueValidator(current_year() + 1)(value)
