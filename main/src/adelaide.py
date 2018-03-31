import difflib
from difflib import SequenceMatcher
from typing import Optional, NamedTuple

from requests_html import HTMLSession


BASE_URL = 'https://ebooks.adelaide.edu.au/meta/titles/'


class Book:
    def __init__(self, index, title, author, match_ratio):
        self.index = index
        self.title = title
        self.author = author
        self.match_ratio = match_ratio

    def __repr__(self):
        return f"{self.title}, by {self.author}. Match: {self.match_ratio}"

# need match_ratio to be mutable.
# class Book(NamedTuple):
#     index: int
#     title: str
#     author: str
#     match_ratio: float


def search_title(title: str, author: str) -> Optional[str]:
    """Find a direct link to a book from the University of Adelaide, by crawling
    their website."""
    MATCH_THRESH = .7
    # title must be included, so we know which alphabetical page to look up.

    session = HTMLSession()
    # Adelaide's site categorizes books by title letter.
    r = session.get(BASE_URL + title[0].upper())

    works = r.html.find('.works', first=True)
    links = works.find('a')

    # todo include author match as well.
    books = []
    for i, link in enumerate(links):
        split = link.text.split('/')

        if len(split) == 2:
            title2, author2 = split
        elif len(split) == 1:
            title2 = split[0]
            author2 = ''
        else:
            continue

        books.append(Book(i, title2, author2, 0))

    for book in books:
        title_ratio = SequenceMatcher(None, title, book.title).ratio()
        author_ratio = SequenceMatcher(None, author, book.author).ratio()

        # todo more sophisticated way of mixing the ratios!
        book.match_ratio = title_ratio + author_ratio/2

    best_match = max(books, key=lambda b: b.match_ratio)

    print(best_match)
    if best_match.match_ratio < MATCH_THRESH:
        return



    return f"https://ebooks.adelaide.edu.au{links[best_match.index].attrs['href']}"