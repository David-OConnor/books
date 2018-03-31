# from enum import Enum  # todo temp for Option testing.

from typing import List, Iterator, Optional

import itertools
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import IntegrityError
from django.db.models import QuerySet

from . import goodreads
from ..models import Work, Isbn, Author, WorkSource, Source
from . import google, adelaide


def update_db_from_gutenberg() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""
    pass


def update_all() -> None:
    for work in Work.objects.all():
        update_sources(work)


def update_sources(work: Work) -> None:
    """Update a single Work's source info by pulling data from each API. The work
    must already exist in the database."""

    # Update from Uni of Adelaide

    # todo for adelaide, you should search each of their pages to build a catalog
    # todo rather than hitting their site for each book. Or at least catch the pages.
    adelaide_url = adelaide.search_title(work.title, work.author.last_name)
    if adelaide_url:
        adelaide_source = Source.objects.get(name='University of Adelaide')

        # All books on Adelaide include in-browser reading, with links to epub and mobi.
        try:
            WorkSource.objects.update_or_create(
                work=work,
                source=adelaide_source,
                epub_url=adelaide_url,
                kindle_url=adelaide_url,
            )
        except IntegrityError:
            pass  # todo why do we get this on update_or_create??

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
            genre=[],  # todo fix this
            description=book.description,
            publication_date=book.publication_date
        )
        # Add the new ISBN to the database.
        Isbn.objects.create(
            isbn=book.isbn,
            work=new_work,
            publication_date=book.publication_date
        )

        # Update the Google work source here, since we already queried them.
        WorkSource.objects.update_or_create(
            source=source,
            work=new_work,
            book_url=book.book_url,
            epub_url=book.epub_url,
            pdf_url=book.pdf_url,
            purchase_url=book.purchase_url,
            price=book.price
        )

        new_results.append(new_work)
    return new_results
