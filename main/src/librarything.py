from typing import List

import requests

from ..models import Work, Author, Source
from .auth import LIBRARYTHING_KEY as KEY

# API ref: https://www.librarything.com/services/


BASE_URL = 'http://www.librarything.com/services/rest/1.1/'

source, _ = Source.objects.get_or_create(
        name='LibraryThing',
        url='https://www.librarything.com/',
        information=True
)


test_isbn = 9780099469506  # todo temp


def find_isbn(isbn: int=test_isbn) -> dict:
    payload = {
        # 'method_name': 'librarything.ck.getwork',
        'apikey': KEY,
        'isbn': str(isbn)
    }
    r = requests.get(BASE_URL + '?method=librarything.ck.getwork', params=payload)

    xml_raw = r.text


def query_title(title: str) -> dict:
    payload = {
        # 'method_name': 'librarything.ck.getwork',
        'apikey': KEY,
        'name': title
    }
    r = requests.get(BASE_URL + '?method=librarything.ck.getwork', params=payload)
    return r
    return r.json()