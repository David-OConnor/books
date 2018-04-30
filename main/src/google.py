from collections import namedtuple
import datetime as dt
from typing import Tuple, List, Iterator, Optional, NamedTuple

import requests
import saturn
from saturn.from_arrow import ParserError

from . import util


# Overall notes: Robust API, but some parts are no longer being maintained.
# Prime candidate to populate new entries in our DB>

class GBook(NamedTuple):
    title: str
    authors: List[Tuple[str, str]]
    isbns: List[int]

    internal_id: str

    language: Optional[str]
    description: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[dt.date]
    categories: List[str]

    book_url: Optional[str]
    epub_url: Optional[str]
    pdf_url: Optional[str]
    purchase_url: Optional[str]

    price: Optional[float]


base_url = 'https://www.googleapis.com/books/v1/'


def search_title_author(title: str, author: str) -> Iterator[GBook]:
    # todo search by ISBN on Google is currently broken.
    url = base_url + 'volumes'
    payload = {
        'q': f'intitle:"{title}"inauthor:"{author}"',
        'printType': 'books',
        # 'projection': 'full',
        # 'key': KEY # todo necesary?
    }

    result = requests.get(url, params=payload).json()
    items = result.get('items')
    if not items:
        return iter(())

    return _process_results(items)


def _process_results(items: List[dict]) -> Iterator[GBook]:
    """Reformat raw Google Books api data into a format with only information
    we care about."""
    # todo write a test for this func
    for book in items:
        volume = book['volumeInfo']

        authors = volume.get('authors')
        if not authors:  # If authors is blank, just move on.
            continue

        authors = [util.split_author(a) for a in authors]

        isbns = []
        for ident in volume.get('industryIdentifiers', []):
            if ident['type'] == 'ISBN_10':
                try:
                    isbns.append(int('978' + ident['identifier']))
                except ValueError:  # eg an X in the identifier.
                    pass
            elif ident['type'] == 'ISBN_13':
                isbns.append(int(ident['identifier']))

        if not isbns:
            continue

        price = book['saleInfo'].get('retailPrice')
        if price:
            price = price['amount']

        try:
            pub_date = saturn.from_str(volume['publishedDate'], 'YYYY-MM-DD')
        except ParserError:  # Might be just a year
            pub_date = saturn.from_str(f"{volume['publishedDate']}-01-01", 'YYYY')
        except KeyError:
            pub_date = None

        yield GBook(
            title=volume['title'],
            authors=authors,
            isbns=isbns,

            internal_id=book['id'],

            language=volume.get('language').lower(),
            description=volume.get('description'),
            publication_date=pub_date,
            publisher=volume.get('publisher'),
            categories=volume.get('categories', []),

            book_url=volume.get('infoLink'),
            epub_url=book['accessInfo']['epub'].get('downloadLink'),
            pdf_url=book['accessInfo']['pdf'].get('downloadLink'),
            purchase_url=book['saleInfo'].get('buyLink'),
            price=price,
        )
