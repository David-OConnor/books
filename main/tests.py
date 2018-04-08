import unittest
from django.test import TestCase
import saturn

from main.src.gutenberg import GbBook
from .models import Work, Author, Isbn, GutenbergWork, Source, WorkSource
from .src import db, google, gutenberg, goodreads, adelaide, kobo


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
        self.assertRaises(AttributeError, Isbn.new(123456, self.dr))

    def test_convert_isbn_10(self):
        # Should convert isbn10 format to isbn13.
        isbn = Isbn.new(1234567890, self.dr)
        self.assertEqual(isbn.isbn, 9781234567890)

    def test_isbn_13(self):
        # Should leave the input isbn intact.
        isbn = Isbn.new(1234567890123, self.dr)
        self.assertEqual(1234567890123, isbn.isbn)


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
        self.assertEqual(61535, goodreads.search(self.selfish))
        self.assertEqual(22463, goodreads.search(self.origin))
        self.assertEqual(18254, goodreads.search(self.oliver))
        self.assertNotEqual(22463, goodreads.search(self.wrong_author_origin))

    def test_librarything(self):
        self.assertEqual(23538, goodreads.search(self.selfish))
        self.assertEqual(23533, goodreads.search(self.origin))
        self.assertEqual(2215, goodreads.search(self.oliver))
        self.assertNotEqual(23533, goodreads.search(self.wrong_author_origin))

    def test_kobo(self):
        self.assertEqual(
            'https://www.kobo.com/us/en/ebook/the-selfish-gene-1',
            kobo.scrape(self.selfish)[0]
        )
        self.assertEqual(
            'https://www.kobo.com/us/en/ebook/the-origin-of-species-by-natural-selection-6th-edition',
            kobo.scrape(self.origin[0])
        )
        self.assertEqual(
            'https://www.kobo.com/us/en/ebook/oliver-twist-64',
            kobo.scrape(self.oliver[0])
        )
        self.assertNotEqual(
            'https://www.kobo.com/us/en/ebook/the-origin-of-species-by-natural-selection-6th-edition',
            kobo.scrape(self.wrong_author_origin[0])
        )




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

        self.assertEqual(expected, queried)

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


class ParsersTestCase(unittest.TestCase):
    # No need to involve Django's test case, setting up a db.
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

        ronan_link = ('Saint Ronan’s Well / Walter Scott [1824]',
                      's/scott/walter/ronan/')
        ronan_expected = adelaide.ABook(
            title='Saint Ronan\'s Well',
            author_first='Walter',
            author_last='Scott',
            publication_year=1824,
            translator=None,
            url='https://ebooks.adelaide.edu.au/l/literature/english-men-of-letters/keats/'
        )

        self.assertEqual(adelaide.parse_link(*abbot_link), abbot_expected)
        self.assertEqual(adelaide.parse_link(*keats_link), keats_expected)
        self.assertEqual(adelaide.parse_link(*ronan_link), ronan_expected)

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
            title='Verner\'s Pride',
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

        self.assertEqual(poems_expected, adelaide.parse_link(*poems_link))
        self.assertEqual(verner_expected, adelaide.parse_link(*verner_link))
        self.assertEqual(peace_expected, adelaide.parse_link(*peace_link))

    def test_gutenberg_index_parser_basic(self):
        victories_text = '''Victories of Wellington and the British Armies,                          56689
 by William Hamilton Maxwell'''
        victories_expected = GbBook(
            internal_id=56689,
            title="Victories of Wellington and the British Armies",
            author_first="William Hamilton",
            author_last="Maxwell",
            language=None,
            illustrator=None,
            subtitle=None,
            editor=None
        )

        turngenev_text = '''Turgenev, by Edward Garnett                                              56809
 [Subtitle: A Study]'''
        turngenev_expected = GbBook(
            internal_id=56809,
            title="Turgenev",
            author_first="Edward",
            author_last="Garnett",
            language=None,
            illustrator=None,
            subtitle="A Study",
            editor=None
        )

        rim_text = '''Within the Rim and Other Essays, by Henry James                          37425'''
        rim_expected = GbBook(
            internal_id=37425,
            title="Within the Rim and Other Essays",
            author_first="Henry",
            author_last="James",
            language=None,
            illustrator=None,
            subtitle=None,
            editor=None
        )

        self.assertEqual(victories_expected, gutenberg.parse_entry(victories_text))
        self.assertEqual(turngenev_expected, gutenberg.parse_entry(turngenev_text))
        self.assertEqual(rim_expected, gutenberg.parse_entry(rim_text))

    def test_gutenberg_index_parser_advanced(self):
        hol_text = '''In het Hol van den Leeuw, door J. Fabius                                 56561
 [Subtitle: Reisschetsen uit Sovjet-Rusland]
 [Illustrator: Piet C. Wagner]
 [Language: Dutch]'''
        hol_expected = GbBook(
            internal_id=56561,
            title="In het Hol van den Leeuw",
            author_first="J.",
            author_last="Fabius",
            language="Dutch",
            illustrator="Piet C. Wagner",
            subtitle="Reisschetsen uit Sovjet-Rusland",
            editor=None
        )

        rising_text = '''The Rising Tide of Color Against White World-Supremacy,                  37408
 by Theodore Lothrop Stoddard'''
        rising_expected = GbBook(
            internal_id=37408,
            title="The Rising Tide of Color Against White World-Supremacy",
            author_first="Theodore Lothrop",
            author_last="Stoddard",
            language=None,
            illustrator=None,
            subtitle=None,
            editor=None
        )

        turandot_text = '''Turandot, Prinzessin von China,                                           6505
 by Johann Christoph Friedrich von Schiller 
 [Author a.k.a. Friedrich Schiller]
 [Subtitle: Ein tragikomisches Maerchen nach Gozzi]
 [Language: German]'''
        turandot_expected = GbBook(
            internal_id=6505,
            title="Turandot, Prinzessin von China",
            author_first="Johann Christoph Friedrich",
            author_last="Schiller",
            language="German",
            illustrator=None,
            subtitle="Ein tragikomisches Maerchen nach Gozzi",
            editor=None
        )

        # self.assertEqual(gutenberg.parse_entry(hol_text), hol_expected)
        self.assertEqual(gutenberg.parse_entry(rising_text), rising_expected)
        self.assertEqual(gutenberg.parse_entry(turandot_text), turandot_expected)


