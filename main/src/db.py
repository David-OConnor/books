from typing import List

from django.contrib.postgres.search import SearchVector
from django.db import IntegrityError

from . import goodreads
from ..models import Work, Isbn, Author, WorkSource, Source, AdelaideWork, \
    GutenbergWork
from . import google, adelaide, gutenberg, kobo, openlibrary, librarything, util


# Try to keep database modifications from APIs in this file.

def update_db_from_gutenberg() -> None:
    """
    Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally.
    """
    pass


def update_all_worksources() -> None:
    for work in Work.objects.all():
        update_worksources(
            work,
            adelaide_source=Source.objects.get(name='University of Adelaide'),
            gutenberg_source=Source.objects.get(name='Project Gutenberg'),
            google_source=Source.objects.get(name='Google'),
            kobo_source=Source.objects.get(name='Kobo'),
            goodreads_source=Source.objects.get(name='GoodReads'),
            librarything_source=Source.objects.get(name='LibraryThing'),
            openlibrary_source=Source.objects.get(name='OpenLibrary'),
        )


def _work_from_adelaide(a_work: AdelaideWork) -> None:
    """Update the database with a Work, from an Adelaide work."""
    if len(a_work.title) > 100 or len(a_work.author_last) > 50:
        return
    if a_work.author_first and len(a_work.author_first) > 50:
        return
    author, _ = Author.objects.get_or_create(
        first_name=a_work.author_first,
        last_name=a_work.author_last
    )

    work, _ = Work.objects.update_or_create(
        title=a_work.title,
        author=author,
        defaults={
            'translator': a_work.translator
        }
    )


def _work_from_gutenberg(gb_work: GutenbergWork) -> None:
    """Update the database with a Work, from an Adelaide work."""
    # todo dry with adelaide
    if len(gb_work.title) > 100 or len(gb_work.author_last) > 50:
        return
    if gb_work.author_first and len(gb_work.author_first) > 50:
        return
    author, _ = Author.objects.get_or_create(
        first_name=gb_work.author_first,
        last_name=gb_work.author_last
    )

    work, _ = Work.objects.update_or_create(
        title=gb_work.title,
        author=author,
        defaults={
            'language': gb_work.language
        }
    )


def create_works_from_adelaide_gutenberg() -> None:
    """
    Populate works from Adelaide and Gutenberg; mostly for initial setup.
    Note that this can take quite a long time.
    """
    for awork in AdelaideWork.objects.all():
        _work_from_adelaide(awork)

    for gwork in GutenbergWork.objects.all():
        _work_from_gutenberg(gwork)

    adelaide_source = Source.objects.get(name='University of Adelaide')
    gutenberg_source = Source.objects.get(name='Project Gutenberg')
    google_source = Source.objects.get(name='Google')
    kobo_source = Source.objects.get(name='GoodReads')
    goodreads_source = Source.objects.get(name='GoodReads')
    librarything_source = Source.objects.get(name='LibraryThing')
    openlibrary_source = Source.objects.get(name='OpenLibrary')

    # The above code is local, and still slow; the below requires multiple API calls.
    for work in Work.objects.all():
        update_worksources(
            work,
            adelaide_source=adelaide_source,
            gutenberg_source=gutenberg_source,
            google_source=google_source,
            kobo_source=kobo_source,
            goodreads_source=goodreads_source,
            librarything_source=librarything_source,
            openlibrary_source=openlibrary_source
        )

        print(f"Added work: {work.title}")


def update_sources_adelaide_gutenberg(work: Work, adelaide_: bool, source=None) -> None:
    """
    Update worksources from the University of Adelaide or Project Gutenberg,
    using their info cached in our DB.
    """
    # adelaide is True if pulling from adelaide; false if from Gutenberg.
    # todo dry from search_local:
    if adelaide_:
        model = AdelaideWork
        if not source:
            source = Source.objects.get(name='University of Adelaide')
    else:
        model = GutenbergWork
        if not source:
            source = Source.objects.get(name='Project Gutenberg')

    title_matches = model.objects.filter(title__search=work.title)

    author_last_v = SearchVector('author_last', weight='A')
    # author_first_v = SearchVector('first_name', weight='B')
    # v = author_last_v + author_first_v

    combined_matches = title_matches.annotate(search=author_last_v).filter(
        search=work.author.last_name
    )
    if not combined_matches:
        return

    best = combined_matches.first()

    # All books on Adelaide include in-browser reading, with links to epub and mobi.
    WorkSource.objects.update_or_create(
        work=work,
        source=source,
        defaults={
            'epub_url': best.url,
            'kindle_url': best.url,
            'internal_id_str': str(best.book_id) if not adelaide else None
        }
    )


def update_google_ws(work: Work, source: Source) -> None:
    google_data = google.search_title_author(work.title, work.author.full_name())
    if not google_data:
        return
    for gbook in google_data:
        WorkSource.objects.update_or_create(
            source=source,
            work=work,
            defaults={
                'book_url': gbook.book_url,
                'epub_url': gbook.epub_url,
                'pdf_url': gbook.pdf_url,
                'purchase_url': gbook.purchase_url,
                'price': gbook.price
            }
        )


def update_kobo_ws(work: Work, source: Source) -> None:
    kobo_data = kobo.scrape(work)
    if kobo_data:
        kobo_url, kobo_price = kobo_data
        if kobo_price:
            if kobo_price == 'free':
                purchase_url = None
                epub_url = kobo_url
                kobo_price = None
            else:
                purchase_url = kobo_url
                epub_url = None
                kobo_price = float(kobo_price[1:])  # todo removes dollar sign. Janky/inflexible
        else:
            epub_url = None
            purchase_url = kobo_url

        WorkSource.objects.update_or_create(
            work=work,
            source=source,
            defaults={
                'purchase_url': purchase_url,
                'epub_url': epub_url,
                'price': kobo_price
            }
        )


def update_openlibrary_ws(
        work: Work,
        source: Source,
        gr_source: Source,
        lt_source: Source,
        books=None,
) -> None:
    """
    Update the OL worksource, as well as goodreads and librarything
    worksources, and add additional ISBNs.  Books may already be provided,
    preventing the need for a serach, if we just populated the initial work.
    """

    books2 = books if books else openlibrary.search(work.title, work.author.full_name())
    # todo by proxy, update librarything and goodreads WSs here since we have
    # todo their ids from openlibrary!
    # for book in books:

    # todo for now, go with the top OL result.
    try:
        book = next(books2)
    except StopIteration:
        return

    # todo for now, if multiple items exist for things like ids etc,
    # todo just pick the first.
    # Update the OpenLibrary worksource.
    WorkSource.objects.update_or_create(
        work=work,
        source=source,
        defaults={
            'internal_id_str': book.internal_id,
            'book_url': openlibrary.url_from_id(book.internal_id)
        }
    )

    # Update Goodreads and Librarything WorkSources.
    for gr_id in book.goodreads_ids:
        WorkSource.objects.update_or_create(
            work=work,
            source=gr_source,
            defaults={
                'internal_id_str': str(gr_id),
                'book_url': goodreads.url_from_id(gr_id)
            }
        )

    for lt_id in book.librarything_ids:
        WorkSource.objects.update_or_create(
            work=work,
            source=lt_source,
            defaults={
                'internal_id_str': str(lt_id),
                'book_url': librarything.url_from_id(lt_id)
            }
        )


def update_worksources(
        work: Work,
        adelaide_source: Source,
        gutenberg_source: Source,
        google_source: Source,
        kobo_source: Source,
        goodreads_source: Source,
        librarything_source: Source,
        openlibrary_source: Source,
        skip_ol=False,
) -> None:
    """
    Update a single Work's source info by pulling data from each API. The work
    must already exist in the database.
    """

    print("Updating ad")
    update_sources_adelaide_gutenberg(work, True, source=adelaide_source)
    print("Updating Gut")
    update_sources_adelaide_gutenberg(work, False, source=gutenberg_source)

    # We skip searching OpenLibrary here if we just created the work from there.
    if not skip_ol:
        update_openlibrary_ws(
            work,
            source=openlibrary_source,
            gr_source=goodreads_source,
            lt_source=librarything_source,
        )

    # We don't need to call goodreads or librarything; we have their info from
    # Openlibrary.
    # update_goodreads_ws(work, source=goodreads_source)

    print("Updating kobo")
    update_kobo_ws(work, source=kobo_source)
    print("updating Google")
    update_google_ws(work, source=google_source)
    print("Done with updates")


def search_local(title: str, author: str) -> List[Work]:
    """Use Postgres's search feature to query the databse based on title and author."""
    # Prioritize author last name over first.
    author_last_v = SearchVector('last_name', weight='A')
    author_first_v = SearchVector('first_name', weight='B')
    author_v = author_last_v + author_first_v
    authors = Author.objects.annotate(search=author_v).filter(search=author)

    # If no title provided, return all works by the located author(s).
    if not title:
        return Work.objects.filter(author__in=authors)

    # Otherwise, search by title.
    title_v = SearchVector('title')  # A is highest priority.
    works = Work.objects.annotate(search=title_v).filter(search=title)

    # If no author provided, don't filter by author results.
    works = works.filter(author__in=authors) if author else works

    # Bump results that have free downloads to the top.
    has_free = []
    no_free = []
    for work in works:
        if work.has_free_sources():
            has_free.append(work)
        else:
            no_free.append(work)
    return has_free + no_free


def filter_chaff(title: str, author: str) -> bool:
    # todo add tests for this
    # Keywords in titles that indicate it's not the book you're looking for.
    TITLE_CHAFF = [
        'abridged',
        'selected from'
        'condensed',
        'classroom',
        'related readings',
        'reader\'s companion',
        'tie-in',
        'literature unit',
        'cinematic',
        'guide',
        'handbook',
        'collector',
        'movie',
        'literature',
        'selected from',
        'close reading',
        'with audio',
        'library',
        'the essential',
        'read-aloud',
        'storybook',
        'coloring book',
        'print edition',
        'analysis',
        'summary',
        'S/Wx',
        'sampler',

        # Misspellings here
        'monte christo'
    ]

    AUTHOR_CHAFF = [
        'press',
        'limited',
        'staff',
        'inc',
        'scholastic',
        'john virgil',
        ', sir'  # eg first='author conan doyle', last='sir'
    ]

    # Test if it's a weird, non-original version.
    for t_chaff in TITLE_CHAFF:
        if t_chaff in title.lower():
            return True
    for a_chaff in AUTHOR_CHAFF:
        if a_chaff in author.lower():
            return True
    return False


def purge_chaff():
    """
    Remove all work that fit our chaff criteria; useful for removing works
    that fit chaff criteria added after they were.
    """
    for author in Author.objects.all():
        if filter_chaff('any_text_not_in_filters', author.full_name()):
            author.delete()
    for work in Work.objects.all():
        if filter_chaff(work.title, work.author.full_name()):
            work.delete()


def clean_titles() -> None:
    """Remove surrounding quotes, and other anomolies from titles."""
    for work in Work.objects.all():
        if work.title[0] == "'" and work.title[-1] == "'":
            work.title = work.title[1:-1]
            work.save()
        if work.title[0] == '"' and work.title[-1] == '"':
            work.title = work.title[1:-1]
            work.save()


def _update(title: str, author: str) -> None:
    """Add or update works to the database from a title/author search."""
    print("OL query start")
    internet_results = openlibrary.search(title, author)
    print("OL query end")
    if not internet_results:
        return

    # Cache these here to prevent extra queries.
    librarything_source = Source.objects.get(name='LibraryThing')
    goodreads_source = Source.objects.get(name='GoodReads')
    openlibrary_source = Source.objects.get(name='OpenLibrary')

    for book in internet_results:
        # todo just top author for now.
        author_first, author_last = util.split_author(book.author)

        author, _ = Author.objects.get_or_create(first_name=author_first,
                                                 last_name=author_last)

        if filter_chaff(book.title, author.full_name()):
            continue

        if len(book.title) > 100:
            continue

        # Add the new work to the database.
        new_work, _ = Work.objects.update_or_create(
            title=book.title,
            author=author,
            defaults={
                'genre': '',  # todo fix this
                # 'description': book.description,
                'language': book.languages[0] if len(book.languages) else None,
                # 'publication_date': book.publication_date
            }
        )
        print("Work created")

        for isbn in book.isbns:
            # Add the new ISBN to the database.
            if len(isbn) not in [10, 13] or isbn[0] == '0':
                continue
            try:
                isbn = int(isbn)
            except ValueError:
                continue

            # todo skip publication date and language, for now.
            isbn = Isbn.new(isbn, new_work)
            try:
                isbn.save()
            except IntegrityError:
                continue

        print("Start OL WS")
        # Update the OpenLibrary work source here, since we already queried them.
        update_openlibrary_ws(
            new_work,
            source=openlibrary_source,
            gr_source=goodreads_source,
            lt_source=librarything_source,
            books=internet_results
        )
        print("End OL WS")
        update_worksources(
            new_work,
            adelaide_source=Source.objects.get(name='University of Adelaide'),
            gutenberg_source=Source.objects.get(name='Project Gutenberg'),
            google_source=Source.objects.get(name='Google'),
            kobo_source=Source.objects.get(name='Kobo'),
            goodreads_source=goodreads_source,
            librarything_source=librarything_source,
            openlibrary_source=openlibrary_source,
            skip_ol=True
        )


def search_or_update(title: str, author: str) -> List[Work]:
    """Try to find the work locally; if unable, Add the work to the database
       based on searching with the Openlibrary API.  This is the main endpoint
       acessed by the view."""
    results = search_local(title, author)
    # If we found a local result, return it. If not, query the API.
    if results:
        return results
    else:
        _update(title, author)
        results = search_local(title, author)
        return results if results else []


def setup() -> None:
    """This is the main workflow for setting up the initial works"""
    # Populate Adelaide and Gutenberg works
    adelaide.crawl()
    gutenberg.download_index()
    gutenberg.populate_from_index()

    # Add Works from these to the database, then add the worksources.
    create_works_from_adelaide_gutenberg()
    clean_titles()

    update_all_worksources()
