import pytest
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
        self.pbd = Work.objects.create(title="Pale Blue Dot", author=sagan)
        self.contact = Work.objects.create(title="Contact", author=sagan)
        self.cosmos = Work.objects.create(title="Cosmos", author=sagan)

        self.seveneves = Work.objects.create(title="Seveneves", author=stephenson)
        self.diamond_age = Work.objects.create(title="The Diamond Age", author=stephenson)
        self.snow_crash = Work.objects.create(title="Snow Crash", author=stephenson)

        self.emma = Work.objects.create(title="Emma", author=austen)
        self.pride = Work.objects.create(title="Pride and Prejudice", author=austen)
        self.sense = Work.objects.create(title="Sense and Sensibility", author=austen)

        self.illiad = Work.objects.create(title="The Illiad", author=homer)
        self.odyssey = Work.objects.create(title="The Odyssey", author=homer)

        self.divine = Work.objects.create(title="The Divine Comedy", author=dante)
        self.purgatory = Work.objects.create(title="Purgatory", author=dante)
        self.purgatorio = Work.objects.create(title="Purgatorio", author=dante)
        self.inferno = Work.objects.create(title="Inferno", author=dante)

        self.sun = Work.objects.create(title="The Sun Also Rises", author=hemingway)
        self.bell = Work.objects.create(title="For Whom the Bell Tolls", author=hemingway)

    def test_search_exact_title_author(self):
        self.assertEqual(list(db.search("Contact", "Carl Sagan")),
                         [self.contact])

    def test_search_nearly_exact_title_author(self):
        self.assertEqual(list(db.search("infern", "Dante Aligiery")),
                         [self.inferno])

    def test_search_last_name_only(self):
        self.assertEqual(list(db.search("emma", "austen")),
                         [self.emma])

    def test_search_title_only(self):  # todo add two books with teh same/similar title; confirm you get both.
        self.assertEqual(list(db.search("purgatory", "")),
                         [self.purgatory, self.purgatorio])

    def test_search_author_only(self):
        self.assertEqual(list(db.search("", "Austen")),
                         [self.emma, self.pride, self.sense])

    def test_garbled_title(self):
        self.assertEqual(list(db.search("Scent Servility", "Jane Austen")),
                         [])


class IsbnValidationTestCase(TestCase):
    def setUp(self):
        mc = Author.objects.create(first_name="Anne", last_name="McCaffrey")
        self.dr = Work.objects.create(title="Dragon Riders of Pern", author=mc)

    def test_invalid_isbn(self):
        # Test an ISBN that has a number of digits neither 13 nor 10.
        with pytest.raises(AttributeError):
            Isbn.new(123456, self.dr)

    def test_convert_isbn_10(self):
        # Should convert isbn10 format to isbn13.
        isbn = Isbn.new(1234567890, self.dr)
        self.assertEqual(isbn.isbn, 9781234567890)

    def test_isbn_13(self):
        # Should leave the input isbn intact.
        isbn = Isbn.new(1234567890123, self.dr)
        self.assertEqual(isbn.isbn, 1234567890123)
