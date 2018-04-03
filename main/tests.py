import pytest
from django.test import TestCase
import saturn

from .models import Work, Author, Isbn, GutenbergWork, Source, WorkSource
from .src import db, google, gutenberg, goodreads, adelaide


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
        self.assertEqual(list(db.search_local("Contact", "Carl Sagan")),
                         [self.contact])

    def test_search_nearly_exact_title_author(self):
        self.assertEqual(list(db.search_local("infern", "Dante Aligiery")),
                         [self.inferno])

    def test_search_last_name_only(self):
        self.assertEqual(list(db.search_local("emma", "austen")),
                         [self.emma])

    def test_search_title_only(self):  # todo add two books with teh same/similar title; confirm you get both.
        self.assertEqual(list(db.search_local("purgatory", "")),
                         [self.purgatory, self.purgatorio])

    def test_search_author_only(self):
        self.assertEqual(list(db.search_local("", "Austen")),
                         [self.emma, self.pride, self.sense])

    def test_garbled_title(self):
        self.assertEqual(list(db.search_local("Scent Servility", "Jane Austen")),
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


class SourceUpdateTestCase(TestCase):
    # Note that these won't verify that correct URLs exist.
    def setUp(self):
        dawkins = Author.objects.create(first_name="Richard", last_name="Dawkins")
        self.selfish = Work.objects.create(title="The Selfish Gene", author=dawkins)

        darwin = Author.objects.create(first_name="Charles", last_name="Darwin")
        self.origin = Work.objects.create(title="The Origin of Species", author=darwin)
        self.wrong_author_origin = Work.objects.create(
            title="The Origin of Species",
            author=dawkins
        )

        dickens = Author.objects.create(first_name="Charles", last_name="Dickens")
        self.oliver = Work.objects.create(title="Oliver Twist", author=dickens)

    def test_goodreads(self):
        # Import here, since importing these modules adds their source to the db.
        from .src import goodreads

        self.assertEqual(goodreads.search(self.selfish), 61535)
        self.assertEqual(goodreads.search(self.origin), 22463)
        self.assertEqual(goodreads.search(self.oliver), 18254)
        self.assertNotEqual(goodreads.search(self.wrong_author_origin), 22463)


class AddWorksTestCase(TestCase):
    def setUp(self):
        dawkins = Author.objects.create(first_name="Richard", last_name="Dawkins")
        self.selfish = Work.objects.create(title="The Selfish Gene", author=dawkins)
        self.selfish_isbn = Isbn.new(9780192860927, self.selfish)

    def test_google_query(self):
        description = ("An ethologist shows man to be a gene machine whose "
                       "world is one of savage competition and deceit")
        expected = google.GBook(
            title='The Selfish Gene',
            authors=['Richard Dawkins'],
            isbns=[9780192860927],
            internal_id='WkHO9HI7koEC',
            description=description,
            language='en',
            publisher='Oxford University Press, USA',
            publication_date=saturn.date(1989, 1, 1),
            categories=['Literary Criticism'],
            book_url='http://books.google.jo/books?id=WkHO9HI7koEC&dq=intitle:%22selfish+gene%22inauthor:%22dawkins%22&hl=&as_pt=BOOKS&source=gbs_api',
            epub_url=None,
            pdf_url=None,
            purchase_url=None,
            price=None,
        )

        def test_goodreads_query(self):
            description = (
            "An ethologist shows man to be a gene machine whose "
            "world is one of savage competition and deceit")
            expected = goodreads.GrBook(
                title='The Selfish Gene',
                authors=['Richard Dawkins'],
                isbn=9780192860927,
                description=description,
                language='en',
                publication_date=saturn.date(1989, 1, 1),
                categories=['Literary Criticism'],
                book_url='http://books.google.jo/books?id=WkHO9HI7koEC&dq=intitle:%22selfish+gene%22inauthor:%22dawkins%22&hl=&as_pt=BOOKS&source=gbs_api',
                epub_url=None,
                pdf_url=None,
                purchase_url=None,
                price=None,
            )

        # top result here
        queried = next(google.search_title_author('selfish gene', 'dawkins'))

        self.assertEqual(queried, expected)

    def test_goodreads_query(self):
        pass


class CachedAPIsTestCase(TestCase):
    def setUp(self):
        austen = Author.objects.create(first_name='Jane', last_name='Austen')
        self.emma = Work.objects.create(title="Emma", author=austen)
        self.sense = Work.objects.create(title="Sense and Sensibility", author=austen)

        saunders = Author.objects.create(first_name='Marshall', last_name='Saunders')
        self.the_king = Work.objects.create(title='The King of the Park', author=saunders)

        emerson = Author.objects.create(first_name='P. H.', last_name='Emerson')
        self.np = Work.objects.create(title='Naturalistic Photography', author=emerson)

        rowe = Author.objects.create(first_name='Richard', last_name='Rowe')
        self.boy = Work.objects.create(title='The Boy in the Bush', author=rowe)

        self.gutenberg = Source.objects.create(
            name='Project Gutenberg',
            url='http://www.gutenberg.org/',
            free_downloads=True
        )

        self.adelaide = Source.objects.create(
            name='University of Adelaide Library',
            url='https://ebooks.adelaide.edu.au/',
            free_downloads=True
        )

    def test_gutindex_parse(self):
        """Test parsing of a gutenberg plain text index file"""
        gutenberg.populate_from_index('GUTINDEX_TEST.ALL')

        # expected1 = GutenbergWork(
        #     title='',
        #     author='',
        #     url='',
        # )

    def test_update_adelaide_source(self):
        for work in Work.objects.all():
            db.update_sources_adelaide_gutenberg(work, True)

    def test_update_gutenberg_source(self):
        for work in Work.objects.all():
            db.update_sources_adelaide_gutenberg(work, False)

        the_king_url = 'http://www.gutenberg.org/ebooks/56831'
        np_url = 'http://www.gutenberg.org/ebooks/56833'
        boy_url = 'http://www.gutenberg.org/ebooks/56695'

        the_king = WorkSource(
            work=self.the_king,
            source=self.gutenberg,
            epub_url=the_king_url,
            kindle_url=the_king_url
        )

        np = WorkSource(
            work=self.np,
            source=self.gutenberg,
            epub_url=np_url,
            kindle_url=np_url
        )

        boy = WorkSource(
            work=self.boy,
            source=self.gutenberg,
            epub_url=boy_url,
            kindle_url=boy_url
        )

        query = list(WorkSource.objects.all())

        self.assertIn(the_king, query)
        self.assertIn(np, query)
        self.assertIn(boy, query)


class ParsersTestCase(TestCase):
    def test_adelaide_link_parser_basic(self):
        abbot_link = ('The Abbot / Walter Scott [1820]', 's/scott/walter/abbot/')
        abbot_expected = adelaide.ABook(
            title='The Abbot',
            author_first='Walter',
            author_last='Scott',
            publication_year=1820,
            translator=None,
            url='https://ebooks.adelaide.edu.au/s/scott/walter/abbot/'
        )

        keats_link = ('Keats / Sidney Colvin [1887]',
                      'l/literature/english-men-of-letters/keats/')
        keats_expected = adelaide.ABook(
            title='Keats',
            author_first='Sidney',
            author_last='Colvin',
            publication_year=1887,
            translator=None,
            url='https://ebooks.adelaide.edu.au/l/literature/english-men-of-letters/keats/'
        )

        self.assertEqual(adelaide.parse_link(*abbot_link), abbot_expected)
        self.assertEqual(adelaide.parse_link(*keats_link), keats_expected)

    def test_adelaide_link_parser_advanced(self):
        """This test includes difficult-to-parse author names, etc"""
        poems_link = (
            'Poems Before Congress / Elizabeth Barrett Browning [1860]',
            'b/browning/elizabeth_barrett/poems-before-congress/'
        )
        poems_expected = adelaide.ABook(
            title='Poems Before Congress',
            author_first='Elizabeth Barrett',
            author_last='Browning',
            publication_year=1860,
            translator=None,
            url='https://ebooks.adelaide.edu.au/b/browning/elizabeth_barrett/poems-before-congress/'
        )

        verner_link = (
            'Verner’s Pride / Ellen Wood ; illustrated by Harold Piffard [1863]',
            'w/wood/ellen/verner-s-pride/'
        )
        verner_expected = adelaide.ABook(
            title='Verner’s Pride',
            author_first='Ellen',
            author_last='Wood',
            publication_year=1863,
            translator=None,
            url='https://ebooks.adelaide.edu.au/w/wood/ellen/verner-s-pride/'
        )

        peace_link = ('Peace / Aristophanes', 'a/aristophanes/peace/')
        peace_expected = adelaide.ABook(
            title='Peace',
            author_first=None,
            author_last='Aristophanes',
            publication_year=None,
            translator=None,
            url='https://ebooks.adelaide.edu.au/a/aristophanes/peace/'
        )

        actual = adelaide.parse_link(*verner_link)

        self.assertEqual(adelaide.parse_link(*poems_link), poems_expected)
        self.assertEqual(adelaide.parse_link(*verner_link), verner_expected)
        self.assertEqual(adelaide.parse_link(*peace_link), peace_expected)



