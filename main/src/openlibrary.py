import re
from typing import NamedTuple, Optional, Iterator, List

import requests

from ..models import Work

# openlibrary appears to be a fantastic resource, with an easy-to-use, headache-free
# api, and loads of works, including many scanned texts.


# https://openlibrary.org/developers/api
# https://openlibrary.org/dev/docs/restful_api
class OlBook(NamedTuple):
    internal_id: str
    goodreads_ids: List[int]
    librarything_ids: List[int]
    title: str
    author: str
    languages: List[str]
    isbns: List[str]  # May have X in isbn; can't use int here
    publication_dates: List[str]

    def __repr__(self):
        return f"""
            title: {self.title}
            author: {self.author}
            id: {self.internal_id}
            languages: {self.languages}
            goodreads ids: {self.goodreads_ids}
            librarything ids: {self.librarything_ids}
        """


def search(work: Work) -> Iterator[OlBook]:
# def search(title, author) -> Iterator[OlBook]:
    URL = 'http://openlibrary.org/search.json'

    # Openlibrary produces many results, and can handle having
    # the author here; query by both rather than querying by title,
    # then filtering by author as we do on other APIs.
    data = {
        'title': work.title,
        # 'title': title,
        'author': work.author
        # 'author': author
    }

    r = requests.get(URL, params=data)

    books = r.json()
    for book in books['docs']:
        match = re.match(r'/works/(.*)$', book['key'])
        internal_id = match.groups()[0]
        yield OlBook(
            # the key is listed in several slightly-different ways through
            # the result. How to handle best?
            # Looks like we should use 'key', since it is teh one ending with W,
            # indicating work as opposed to M for book.
            # internal_ids=book['edition_key'],
            # todo dry on this get if/else logic
            internal_id=internal_id,
            goodreads_ids=[int(i) for i in book['id_goodreads']] if book.get('id_goodreads') else [],
            librarything_ids=[int(i) for i in book['id_librarything']] if book.get('id_librarything') else [],
            title=book['title'],
            author=book['author_name'][0],
            languages=[l for l in book['language']] if book.get('language') else [],
            publication_dates=[p for p in book['publish_date']] if book.get('publish_date') else [],
            isbns=[i for i in book['isbn']] if book.get('isbn') else []
        )
        # todo use the author key to find author's first/last name?


    # for book in books:


# def query(title: str, author: str) -> Iterator[OlBook]:
    # URL = 'http://openlibrary.org/query.json'
    #
    # data = {
    #     # 'title': work.title
    #     'type': '/type/edition',
    #     'title': title
    # }

    # r = requests.get(URL, params=data)
    #
    # books = r.json()
    #
    # regex = re.compile(r'/books/(.*)^')
    #
    # for book in books:
    #     internal_id = regex.match(book.value)
    #     if not internal_id:
    #         continue
    #
    #     yield OlBook(
    #         internal_id=internal_id.groups()[0],
    #         title='',
    #     )
    #
    # return r

def url_from_id(internal_id: str) -> str:
    """Find the URL associated with a book from its id."""
    return f"https://openlibrary.org/works/{internal_id}"
