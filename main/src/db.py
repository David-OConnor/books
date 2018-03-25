from difflib import SequenceMatcher
from typing import List

from ..models import Work, Isbn
from . import google


def update_db_from_gutenbert() -> None:
    """Add and edit books and authors in the database using Gutenberg's catalog,
    stored locally."""


def query(title: str, author: str) -> List[Work]:
    # A higher min_match_ratio will be more likely to not match something in the
    # database, and favor looking up a new one in the API.
    min_match_ratio = .3
    title, author = title.lower(), author.lower()
    db_entries = Work.objects.all()

    ratios = []
    for book in db_entries:
        # todo consider quick ratio.
        title_ratio = SequenceMatcher(None, title, book.title).ratio()
        # todo for now, we're only using one author per work.
        author_ratio = SequenceMatcher(None, author, book.author).ratio()
        composite = google.composite_ratio(title_ratio, author_ratio)
        ratios.append((book, title_ratio, author_ratio, composite))

    sequenced = sorted(ratios, key=lambda x: x[3], reverse=True)

    filtered = list(filter(lambda x: x[3] > min_match_ratio, sequenced))

    if not filtered:
        print("Didn't find it; saving to API")
        return [save_from_api(title, author, db_entries)]

    return [book[0] for book in filtered]


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