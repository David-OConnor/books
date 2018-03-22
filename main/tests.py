from django.test import TestCase
from main.models import Book, Author, ISBN


def test_search_title():
    assert 1 == 1


class SearchTestCase(TestCase):
    def setup(self):
        carl_sagan = Author(first_name="Carl", last_name="Sagan")

        Book.objects.create(title="Pale Blue Dot", author=carl_sagan)
        self.assertEqual(1, 1)
