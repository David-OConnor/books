from enum import Enum  # todo temp for Option testing.

from difflib import SequenceMatcher
from typing import List, Iterator

import itertools
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from ..models import Work, Isbn, Author
from . import google


class Option(Enum):
    # todo Experimental. Like Rust's Option.
    NONE = 1
    SOME = 2


def composite_ratio(ratio_1: float, ratio_2: float) -> float:
    try:
        return 1 / (1/ratio_1 + 1/ratio_2)
    except ZeroDivisionError:
        return 0


def update_db_from_gutenberg() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""


def search(title: str, author: str) -> Iterator[Work]:
    """Use Postgres's search feature to query the databse based on title and author."""
    authors = Author.objects.annotate(
        search=SearchVector('first_name', 'last_name')
    ).filter(search=author)

    works = Work.objects.filter(title__search=title)

    return itertools.chain(works.filter(author__in=authors))


# todo signature: Iteator[Work] or None.
def search_or_update(title: str, author: str) -> Iterator[Work]:
    results = list(search(title, author))
    return results
    # if results:
    #     return Option.SOME(results)
    # return Option.NONE(results)





def search2(title: str, author: str) -> Iterator[Work]:
    """Find the most likely database values for this work."""
    # A higher min_match_ratio will be more likely to not match something in the
    # database, and favor looking up a new one in the API.
    min_match_ratio = .3
    title, author = title.lower(), author.lower()

    # todo nope: We have to query specifically here.
    db_entries = Work.objects.all()

    ratios = []
    for book in db_entries:
        # todo consider quick ratio.
        title_ratio = SequenceMatcher(None, title, book.title).ratio()
        # todo for now, we're only using one author per work.
        author_ratio = SequenceMatcher(None, author, book.author.full_name()).ratio()
        composite = composite_ratio(title_ratio, author_ratio)
        ratios.append((book, title_ratio, author_ratio, composite))

    sequenced = sorted(ratios, key=lambda x: x[3], reverse=True)

    filtered = list(filter(lambda x: x[3] > min_match_ratio, sequenced))

    if not filtered:
        print("Didn't find it; saving to API")
        # return [save_from_api(title, author, db_entries)]

    return (book[0] for book in filtered)


def save_from_api(title: str, author: str, db_entries: List[Work]) -> Work:
    """Adds a new ISBN and/or Work to the database..."""
    # todo do we need to track ISBNs at all? May be too confusing.
    api_data = google.search(title, author)
    if not api_data:
        print("Nope, not here: {}, by {}".format(title, author))

    best = api_data[0][0]

    # todo add a duplicate check
    #
    # duplicate_thresh = .2
    # for entry in db_entries:
    #     if entry.

    author_ratios = [(author_goog, SequenceMatcher(None, author.lower(), author_goog.lower()).ratio()) for
                         author_goog in best.authors]
    # We're only searching for one author, so find the best match in the
    # authors list google returns, and ignore the rest.
    best_author = max(author_ratios, key=lambda x: x[1])[0]

    work = Work(title=best.title, author=best_author)

    work.save()
    # If an ISBN's present for that entry, make a database entry for it.
    if best.isbn_10 and best.isbn_13:
        isbn = ISBN(isbn_10=best.isbn_10,
                    isbn_13=best.isbn_13,
                    # publication_date=best.publication_date,
                    work=work)
        isbn.save()

    print("Saved {} by {}".format(best.title, best_author))
    return work

# todo use sequencematcher to check for duplicates?