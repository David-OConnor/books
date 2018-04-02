from typing import List, Iterator, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from . import goodreads
from ..models import Work, Isbn, Author, WorkSource, Source, AdelaideWork, \
    GutenbergWork
from . import google, adelaide


def update_db_from_gutenberg() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""
    pass


def update_all() -> None:
    for work in Work.objects.all():
        update_worksources(work)


def update_sources_adelaide_gutenberg(work: Work, adelaide_: bool) -> None:
    """Update worksources from the University of Adelaide or Project Gutenberg,
       using their info cached in our DB."""
    # adelaide is True if pulling from adelaide; false if from Gutenberg.
    # todo dry from search_local:
    if adelaide_:
        model = AdelaideWork
        source = Source.objects.get(name='University of Adelaide')
    else:
        model = GutenbergWork
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


def update_worksources(work: Work) -> None:
    """Update a single Work's source info by pulling data from each API. The work
    must already exist in the database."""

    update_sources_adelaide_gutenberg(work, True)
    update_sources_adelaide_gutenberg(work, False)


    # Use the work's ISBNs as unique identifiers.
    # for isbn in work.isbns:
    #     gr_worksource = goodreads.search_isbn(isbn)
    #     gr_worksource.save()


def search_local(title: str, author: str) -> QuerySet:
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
    return works.filter(author__in=authors) if author else works


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
        'selected from'
    ]

    AUTHOR_CHAFF = [
        'press',
        'limited',
    ]

    # Test if it's a weird, non-original version.
    for chaff in TITLE_CHAFF:
        if chaff in title.lower():
            return True
    for chaff in AUTHOR_CHAFF:
        if chaff in author.lower():
            return True
    return False


def search_or_update(title: str, author: str) -> List[Work]:
    results = list(search_local(title, author))

    # If we found a local result, return it. If not, query the API.
    if results:
        return results

    internet_results = google.search_title_author(title, author)
    if not internet_results:
        return []

    source = Source.objects.get(name='Google')

    new_results = []
    for book in internet_results:
        if filter_chaff(book.title, book.authors[0]):
            continue

        # todo just top author for now.
        try:
            author_first, author_last = book.authors[0].split()
        except ValueError:
            author_last, author_first = book.authors[0], ''

        author, _ = Author.objects.get_or_create(first_name=author_first, last_name=author_last)

        # Add the new work to the database.
        new_work, _ = Work.objects.get_or_create(
            title=book.title,
            author=author,
            defaults={
                'genre': [],  # todo fix this
                'description':  book.description,
                # 'publication_date': book.publication_date
            }
        )

        # Add the new ISBN to the database.
        Isbn.objects.update_or_create(
            isbn=book.isbn,
            defaults={
                'work': new_work,
                'publication_date': book.publication_date,
                'language': book.language
            }
        )

        # Update the Google work source here, since we already queried them.
        WorkSource.objects.update_or_create(
            source=source,
            work=new_work,
            defaults={
                'book_url': book.book_url,
                'epub_url': book.epub_url,
                'pdf_url': book.pdf_url,
                'purchase_url': book.purchase_url,
                'price': book.price
            }
        )

        update_worksources(new_work)

        new_results.append(new_work)
    return new_results
