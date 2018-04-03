import xml.etree.ElementTree as ET
import datetime as dt
from typing import Optional, Iterator, NamedTuple, List

import requests

# Documentation: https://www.goodreads.com/api
import saturn

from ..models import Isbn, Source, WorkSource, Work
from .auth import GOODREADS_KEY as KEY


# API ref: https://www.goodreads.com/api

BASE_URL = 'https://goodreads.com/'


class GrBook(NamedTuple):
    title: str
    authors: List[str]
    isbn: int

    language: Optional[str]
    description: Optional[str]
    publication_date: Optional[dt.date]
    categories: List[str]

    book_url: Optional[str]
    epub_url: Optional[str]
    pdf_url: Optional[str]
    purchase_url: Optional[str]

    price: Optional[float]



# todo make goodreads your main populator, instead of google!

def search(work: Work) -> Optional[int]:
    """Find the unique goodreads ids associated with a work's isbns."""
    # for isbn in Isbn.objects.filter(work=work):
    # todo deal with different editions!
    # todo just title search for now
    payload = {
        # 'q': str(isbn.isbn),
        'q': f'{work.title}',
        'key': KEY,
        # 'search': 'isbn'  # title, author or all. I guess all for isbn??
        'search': 'title'  # title, author or all. I guess all for isbn??
    }

    r = requests.get(BASE_URL + 'search/index.xml', params=payload)

    root = ET.fromstring(r.text)
    works = root.find('search').find('results').findall('work')

    for gr_work in works:
        book = gr_work.find('best_book')
        if book.find('author').find('name').text.lower() == work.author.full_name().lower():
            return int(book.find('id').text)


def search_title_author(title: str, author: str) -> Iterator[GrBook]:
    """Find the unique goodreads ids associated with a work's isbns."""
    # for isbn in Isbn.objects.filter(work=work):
    # todo deal with different editions!
    # todo just title search for now
    payload = {
        # 'q': str(isbn.isbn),
        'q': f'{title} {author}]',
        'key': KEY,
        # 'search': 'isbn'  # title, author or all. I guess all for isbn??
        'search': 'all'  # title, author or all. I guess all for isbn??
    }

    r = requests.get(BASE_URL + 'search/index.xml', params=payload)

    root = ET.fromstring(r.text)
    works = root.find('search').find('results').findall('work')

    for gr_work in works:
        book = gr_work.find('best_book')
        if book.find('author').find('name').text.lower() == 0:

            gr_id = int(book.find('id').text)

            publ_year = gr_work.find('original_publication_year').text
            publ_month = gr_work.find('original_publication_month').text
            publ_day = gr_work.find('original_publication_day').text
            publication_date = saturn.from_str(f'{publ_year}-{publ_month}-{publ_day}', 'YYYY-MM-DD')


def url_from_id(internal_id: int) -> str:
    """Find the goodreads URL associated with a book from its id."""
    return f"https://www.goodreads.com/book/show/{internal_id}"
