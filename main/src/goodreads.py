import requests

# Documentation: https://www.goodreads.com/api
from ..models import Isbn, WorkSource
from .auth import GOODREADS_KEY as KEY

BASE_URL = 'https://goodreads.com/'

test_isbn = 782266079990 # todo temp


def search_isbn(isbn: int=test_isbn) -> WorkSource:
    """Find a WorkSource for a specific ISBN."""
    payload = {
        'q': str(isbn),
        # 'page': 1,  # default 1, optional,
        'key': KEY,
        # 'search[field]': 'all'  # title, author or all. I guess all for isbn??
    }

    r = requests.get(BASE_URL + 'search/index.xml', params=payload)
    return r.text


def search_title(title: str) -> WorkSource:
    # todo you could merge this with search_isbn, since they both
    # todo use the same API endpoint.
    pass