from collections import namedtuple
import datetime as dt
from typing import Tuple, List, Iterator, Optional, NamedTuple

import requests
import saturn
from saturn.from_arrow import ParserError

from main.models import Source
from .auth import GOOG_KEY as KEY


# Overall notes: Robust API, but some parts are no longer being maintained.
# Prime candidate to populate new entries in our DB>

# This file taken from the older books project.


class gBook(NamedTuple):
    title: str
    authors: List[str]
    isbn: int
    description: Optional[str]
    publication_date: Optional[dt.date]
    categories: List[str]

    book_url: Optional[str]
    epub_url: Optional[str]
    pdf_url: Optional[str]
    purchase_url: Optional[str]

    price: Optional[float]


base_url = 'https://www.googleapis.com/books/v1/'


def search_isbn(isbn: str='0671004107'):
    # todo search by ISBN on Google is currently broken.
    url = base_url + 'volumes'
    payload = {
        'q': f'ISBN:"{isbn}"',
        'printType': 'books',  # Perhaps avoids magazine etc.
        # 'projection': 'full',
        'filter': 'ebooks',
    }

    result = requests.get(url, params=payload)
    return result.json()

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    return result


def search_title_author(title: str, author: str) -> Optional[Iterator[gBook]]:
    # todo search by ISBN on Google is currently broken.
    url = base_url + 'volumes'
    payload = {
        'q': f'intitle:"{title}"inauthor:"{author}"',
        'printType': 'books',
        # 'projection': 'full',
        # 'filter': 'ebooks',
        # 'key': KEY # todo necesary?
    }

    result = requests.get(url, params=payload).json()
    items = result.get('items')
    if not items:
        return

    return _trim_results(items)


def _trim_results(items: List[dict]) -> Iterator[gBook]:
    """Reformat raw Google Books api data into a format with only information
    we care about."""
    for book in items:

        volume = book['volumeInfo']

        authors = volume.get('authors')
        if not authors:  # If authors is blank, just move on.
            continue

        idents = volume.get('industryIdentifiers')
        if not idents:
            continue

        isbn = [ident for ident in idents if ident['type'] == 'ISBN_13']
        if not isbn:
            continue
        isbn = int(isbn[0]['identifier'])

        price = book['saleInfo'].get('retailPrice')
        if price:
            price = price['amount']

        try:
            pub_date = saturn.from_str(volume['publishedDate'], 'YYYY-MM-DD')
        except ParserError:  # Might be just a year
            pub_date = saturn.from_str(f"{volume['publishedDate']}-01-01", 'YYYY')
        except KeyError:
            pub_date = None

        yield gBook(
            title=volume['title'],
            authors=authors,
            isbn=isbn,
            description=volume.get('description'),
            publication_date=pub_date,
            categories=volume.get('categories', []),

            book_url=volume.get('infoLink'),
            epub_url=book['accessInfo']['epub'].get('downloadLink'),
            pdf_url=book['accessInfo']['pdf'].get('downloadLink'),
            purchase_url=book['saleInfo'].get('buyLink'),
            price=price,
        )
