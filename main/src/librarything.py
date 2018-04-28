import xml.etree.ElementTree as ET
from typing import NamedTuple, Optional

import requests
from requests_html import HTMLSession

from ..models import Work
from .auth import LIBRARYTHING_KEY as KEY

# todo given this isn't working out, and we can pull its unique id from
# todo openlibrary, let's just use that.

# API ref: https://www.librarything.com/services/

#
#
# class LtBook(NamedTuple):
#     # Information stored in an Abook (And for similar tuples in API files) encloses
#     # The information the source contains; we may not use all of it in the db, or may
#     # wish for more.
#     internal_id: int
#     title: str
#     author_first: Optional[str]
#     author_last: str
#     publication_year: Optional[int]
#     translator: Optional[str]
#
#     def __repr__(self):
#         return f"title: {self.title} author: {self.author_first} {self.author_last}\n" \
#                f"publication: {self.publication_year}"


# todo Just like with goodreads, we could pull more data, but for now,
# just find the internal id, so we can link to it.
def scrape(work: Work) -> Optional[int]:
    """
    Search using .ck.getwork isn't working for name searches;
    crawl the page instead.
    """
    payload = {
        'search': work.title,
        'searchtype': 101,  # 101 is for books.
        'sortchoice': 0 # 0 is for sort by relevance
    }

    session = HTMLSession()
    r = session.get('https://www.librarything.com/search.php?', params=payload)
    return r
    # todo parsing isn't working... JS magic preventing it?
    work_div = r.html.find('.works', first=True)


def search(work: Work) -> Optional[int]:
    """
    Find a book by Title. Libarything's api isn't very flexible.
    http: // www.librarything.com / services / rest / documentation / 1.1 /
    librarything.ck.getwork.php
    """

    # todo DRY between this and goodreads

    payload = {
        'method': 'librarything.ck.getwork',
        'name': work.title,
        'api_key': KEY,
    }

    r = requests.get('http://www.librarything.com/services/rest/1.1/', params=payload)

    root = ET.fromstring(r.text)

    return root
    works = root.find('ltml').find.findall('item')

    for lt_work in works:
        # This is fragile; requires name to be exact, other than case.
        if lt_work.find('author').text.lower() == work.author.full_name().lower():
            return int(lt_work.attribute['id'])


def url_from_id(internal_id: int) -> str:
    """Find the goodreads URL associated with a book from its id."""
    return f"http://www.librarything.com/work/{internal_id}"
