from collections import namedtuple
from difflib import SequenceMatcher
from typing import Tuple, List

import requests
import saturn

# from .auth import GOOG_KEY as key


# This file taken from the older books project.
from saturn.from_arrow import ParserError

Book2 = namedtuple('Book', ['title', 'authors', 'isbn_10', 'isbn_13',
                            'publication_date', 'categories'])

base_url = 'https://www.googleapis.com/books/v1/'


def search_title(title):
    url = base_url + 'volumes'
    payload = {'q': 'intitle:"{}"'.format(title),
               'printType': 'books',
               'projection': 'full'}

    result = requests.get(url, params=payload)

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    return _trim_results(result)


def search_author(author):
    url = base_url + 'volumes'
    payload = {'q': 'inauthor:"{}"'.format(author),
               'printType': 'books'}

    result = requests.get(url, params=payload)

    result = result.json()
    result = [book['volumeInfo'] for book in result['items']]

    return _trim_results(result)


def search(title='', author='') -> List[Book2]:
    # The author/title composite match ratio must exceed this to be returned.
    min_match_ratio = 0

    url = base_url + 'volumes'
    payload = {'q': f'intitle:{title}+inauthor:{author}',
               'printType': 'books'}

    result = requests.get(url, params=payload)

    result = result.json()

    items = result.get('items')
    if not items:  # ie no results from Google.
        return []

    result = [book['volumeInfo'] for book in items]

    trimmed = _trim_results(result)

    ratios = []
    for book in trimmed:
        title_ratio = SequenceMatcher(None, title.lower(), book.title.lower()).ratio()

        author_ratios = [SequenceMatcher(None, author.lower(), author_goog.lower()).ratio() for
                         author_goog in book.authors]
        # We're only searching for one author, so find the best match in the
        # authors list google returns, and ignore the rest.  Note that authors
        # may be empty.
        best_author_ratio = max(author_ratios) if author_ratios else 0
        composite = composite_ratio(title_ratio, best_author_ratio)
        ratios.append((book, title_ratio, best_author_ratio, composite))

    sequenced = sorted(ratios, key=lambda x: x[3], reverse=True)
    filtered = filter(lambda x: x[3] >= min_match_ratio, sequenced)

    return list(filtered)


def composite_ratio(ratio_1: float, ratio_2: float) -> float:
    try:
        return 1 / (1/ratio_1 + 1/ratio_2)
    except ZeroDivisionError:
        return 0


def _trim_results(raw_data) -> List[Book2]:
    """Reformat raw Google Books api data into a format with only information
    we care about."""
    result = []
    for book in raw_data:
        try:
            pub_date = saturn.from_str(book['publishedDate'], 'YYYY-MM-DD')
        except ParserError:  # Might be just a year
            pub_date = book['publishedDate']
        except KeyError:
            pub_date = 'missing'

        isbn_10 = ''
        isbn_13 = ''
        try:
            isbn_raw = book['industryIdentifiers']

            for num in isbn_raw:
                if num['type'] == 'ISBN_13':
                    isbn_13 = num['identifier']
                elif num['type'] == 'ISBN_10':
                    isbn_10 = num['identifier']

        # This keyerror means 'industryIdentifiers' is missing entirely; if
        # it's present, but doens't have 'isbn_13/10' subkeys, it doesn't
        # come up.
        except KeyError:
            pass

        authors = book.get('authors', [])  # authors may not be present.
        categories = book.get('categories', [])

        result.append(
            Book2(book['title'], authors, isbn_10, isbn_13, pub_date, categories)
        )
    return result
