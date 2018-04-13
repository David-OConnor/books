from typing import List, Iterator, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from . import goodreads
from ..models import Work, Isbn, Author, WorkSource, Source, AdelaideWork, \
    GutenbergWork
from . import google, adelaide, gutenberg, kobo


# Try to keep database modifications from APIs in this file.


def update_db_from_gutenberg() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""
    pass


def update_all_worksources() -> None:
    for work in Work.objects.all():
        update_worksources(
            work,
            adelaide_source=Source.objects.get(name='University of Adelaide'),
            gutenberg_source=Source.objects.get(name='Project Gutenberg'),
            google_source=Source.objects.get(name='Google'),
            kobo_source=Source.objects.get(name='Kobo')
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
    """Populate works from Adelaide and Gutenberg; mostly for initial setup.
    Note that this can take quite a long time."""
    for awork in AdelaideWork.objects.all():
        _work_from_adelaide(awork)

    for gwork in GutenbergWork.objects.all():
        _work_from_gutenberg(gwork)

    # The above code is local, and still slow; the below requires multiple API calls.
    for work in Work.objects.all():
        update_worksources(work)


def update_sources_adelaide_gutenberg(work: Work, adelaide_: bool, source=None) -> None:
    """Update worksources from the University of Adelaide or Project Gutenberg,
       using their info cached in our DB."""
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
            'internal_id': best.book_id if not adelaide else None
        }
    )


def update_worksources(work: Work, skip_google=False, adelaide_source=None,
                       gutenberg_source=None, google_source=None, kobo_source=None) -> None:
    """Update a single Work's source info by pulling data from each API. The work
    must already exist in the database."""
    # Skip google if we just queried their API; prevents redundant calls.
    if not adelaide_source:
        adelaide_source = Source.objects.get(name='University of Adelaide')
    if not gutenberg_source:
        gutenberg_source = Source.objects.get(name='Project Gutenberg')

    update_sources_adelaide_gutenberg(work, True, source=adelaide_source)
    update_sources_adelaide_gutenberg(work, False, source=gutenberg_source)

    # for goodreads_id in goodreads.search(work):
    goodreads_id = goodreads.search(work)
    if goodreads_id:
        WorkSource.objects.update_or_create(
            work=work,
            source=Source.objects.get(name='GoodReads'),
            defaults={
                'internal_id': goodreads_id,
                'book_url': goodreads.url_from_id(goodreads_id)
            }
        )

    # Update from kobo
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
            source=kobo_source if kobo_source else Source.objects.get(name='Kobo'),
            defaults={
                'purchase_url': purchase_url,
                'epub_url': epub_url,
                'price': kobo_price
            }
        )

        # todo split into multiple funs
        # Update from Google.
        if skip_google:
            return
        google_data = google.search_title_author(work.title, work.author.full_name())
        if not google_data:
            return
        for gbook in google_data:
            WorkSource.objects.update_or_create(
                source=google_source if google_source else Source.objects.get(name='Google'),
                work=work,
                defaults={
                    'book_url': gbook.book_url,
                    'epub_url': gbook.epub_url,
                    'pdf_url': gbook.pdf_url,
                    'purchase_url': gbook.purchase_url,
                    'price': gbook.price
                }
            )


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
    """Remove all work that fit our chaff criteria; useful for removing works
    that fit chaff criteria added after they were."""
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



def update(title: str, author: str) -> None:
    """Add or update works to the database from a title/author search."""
    internet_results = google.search_title_author(title, author)
    if not internet_results:
        return

    for book in internet_results:

        # todo just top author for now.
        author_first, author_last = book.authors[0]

        author, _ = Author.objects.get_or_create(first_name=author_first,
                                                 last_name=author_last)

        if filter_chaff(book.title, author.full_name()):
            continue

        if len(book.title) > 100:
            continue

        # Add the new work to the database.
        new_work, _ = Work.objects.get_or_create(
            title=book.title,
            author=author,
            defaults={
                'genre': [],  # todo fix this
                'description': book.description,
                # 'publication_date': book.publication_date
            }
        )

        for isbn in book.isbns:
            # Add the new ISBN to the database.
            Isbn.objects.update_or_create(
                isbn=isbn,
                defaults={
                    'work': new_work,
                    'publication_date': book.publication_date,
                    'language': book.language
                }
            )

        # Update the Google work source here, since we already queried them.
        WorkSource.objects.update_or_create(
            source=Source.objects.get(name='Google'),
            work=new_work,
            defaults={
                'book_url': book.book_url,
                'epub_url': book.epub_url,
                'pdf_url': book.pdf_url,
                'purchase_url': book.purchase_url,
                'price': book.price
            }
        )

        update_worksources(new_work, skip_google=True)


def search_or_update(title: str, author: str) -> List[Work]:
    """Try to find the work locally; if unable, Add the work to the database
       based on searching with the Google Api."""
    results = search_local(title, author)
    # If we found a local result, return it. If not, query the API.
    if results:
        return results
    else:
        update(title, author)
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
