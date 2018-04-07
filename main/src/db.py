from typing import List, Iterator, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from . import goodreads
from ..models import Work, Isbn, Author, WorkSource, Source, AdelaideWork, \
    GutenbergWork
from . import google, adelaide, kobo


# Try to keep database modifications from APIs in this file.


def update_db_from_gutenberg() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""
    pass


def update_all_worksources() -> None:
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

    # update_sources_adelaide_gutenberg(work, True)
    # update_sources_adelaide_gutenberg(work, False)
    #
    # # for goodreads_id in goodreads.search(work):
    # goodreads_id = goodreads.search(work)
    # if goodreads_id:
    #     WorkSource.objects.update_or_create(
    #         work=work,
    #         source=Source.objects.get(name='GoodReads'),
    #         defaults={
    #             'internal_id': goodreads_id,
    #             'book_url': goodreads.url_from_id(goodreads_id)
    #         }
    #     )

    # Update from kobo
    kobo_data = kobo.scrape(work)
    if kobo_data:
        kobo_url, kobo_price = kobo_data
        kobo_price = float(kobo_price[1:]) if kobo_price else None  # todo removes dollar sign. Janky/inflexible
        WorkSource.objects.update_or_create(
            work=work,
            source=Source.objects.get(name='Kobo'),
            defaults={
                'purchase_url': kobo_url,
                'price': kobo_price
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
    ]

    AUTHOR_CHAFF = [
        'press',
        'limited',
        'staff',
        'inc',
        'scholastic',
        'john virgil'
    ]

    # Test if it's a weird, non-original version.
    for chaff in TITLE_CHAFF:
        if chaff in title.lower():
            return True
    for chaff in AUTHOR_CHAFF:
        if chaff in author.lower():
            return True
    return False


def purge_chaff():
    """Remove all work that fit our chaff criteria; useful for removing works
    that fit chaff criteria added after they were."""
    for work in Work.objects.all():
        if filter_chaff(work.title, work.author.full_name()):
            work.delete()


def search_or_update(title: str, author: str) -> List[Work]:
    """Try to find the work locally; if unable, Add the work to the database
       based on searching with the Google Api."""
    results = search_local(title, author)

    # If we found a local result, return it. If not, query the API.
    if results:
        return results

    internet_results = google.search_title_author(title, author)
    if not internet_results:
        return []

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

        if len(title) > 100:
            continue

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

        update_worksources(new_work)

        new_results.append(new_work)
    return new_results
