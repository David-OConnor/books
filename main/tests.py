from django.test import TestCase

from .models import Work, Author, Isbn
from .src import db


class SearchTestCase(TestCase):
    def setUp(self):
        """Setup example database objects for use in tests"""
        sagan = Author.objects.create(first_name="Carl", last_name="Sagan")
        stephenson = Author.objects.create(first_name="Neal", last_name="Stephenson")
        austen = Author.objects.create(first_name="Jane", last_name="Austen")
        homer = Author.objects.create(first_name="Homer", last_name="")
        dante = Author.objects.create(first_name="Dante", last_name="Alighieri")
        hemingway = Author.objects.create(first_name="Ernest", last_name="Hemingway")

        # todo add similar names/authors etc to see how search handles it.
        Work.objects.create(title="Pale Blue Dot", author=sagan)
        Work.objects.create(title="Contact", author=sagan)
        Work.objects.create(title="Cosmos", author=sagan)

        Work.objects.create(title="Seveneves", author=stephenson)
        Work.objects.create(title="The Diamond Age", author=stephenson)
        Work.objects.create(title="Snow Crash", author=stephenson)

        Work.objects.create(title="Emma", author=austen)
        Work.objects.create(title="Pride and Prejudice", author=austen)
        Work.objects.create(title="Sense and Sensibility", author=austen)

        Work.objects.create(title="The Illiad", author=homer)
        Work.objects.create(title="The Odyssey", author=homer)

        Work.objects.create(title="The Divine Comedy", author=dante)
        Work.objects.create(title="Purgatory", author=dante)
        Work.objects.create(title="Purgatorio", author=dante)
        Work.objects.create(title="Inferno", author=dante)

        Work.objects.create(title="The Sun Also Rises", author=hemingway)
        Work.objects.create(title="For Whom the Bell Tolls", author=hemingway)

    def test_search_title(self):
        pass

    def test_search_author(self):
        pass

    def test_search_both_1(self):
        pass