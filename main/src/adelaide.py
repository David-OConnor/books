from string import ascii_uppercase
import re
from typing import Optional, NamedTuple

from requests_html import HTMLSession

from main.models import AdelaideWork
from . import util

BASE_URL = 'https://ebooks.adelaide.edu.au/meta/titles/'


class ABook(NamedTuple):
    """
    Information stored in an Abook (And for similar tuples in API files) encloses
    The information the source contains; we may not use all of it in the db, or may
    wish for more.
    """
    title: str
    author_first: Optional[str]
    author_last: str
    publication_year: Optional[int]
    translator: Optional[str]
    url: str

    def __repr__(self):
        return f"title: {self.title} author: {self.author_first} {self.author_last}\n" \
               f"publication: {self.publication_year}, url: {self.url}"


def parse_link(text: str, href: str) -> Optional[ABook]:
    # Initially split into three easy-to-parse chunks.
    split_title_misc_pub = r'(.*?) / (.*?)(?: \[(\d{4})\])?$'
    match = re.match(split_title_misc_pub, text)

    if not match:
        return

    title, misc, publication_year = match.groups()

    # todo Currently doesn't work in the cases where no author is listed in the text;
    # todo could deal with this if listed in the URL which it may be.

    # Now parse misc: This will be the author's first and last name, and filler
    # such as translator, illustrator etc.

    misc = misc.replace(' []', '')

    # (with an?.* ? by)?
    # Adelaide uses a semicolon after the author for fille.
    split_misc = r'(.*?)(\s?;.*)?$'

    misc_match = re.match(split_misc, misc)
    if not misc_match:
        return

    # todo parse extras like translator; for now we discard.
    author, extras = misc_match.groups()

    # translator = None
    # if translator_match:
    #     author, translator = translator_match.groups()

    author_first, author_last = util.split_author(author)

    # todo: You should be able to modify or remove this sanity check once you
    # todo clean up your algorithm.
    if len(title) > 150 or len(author_last) > 100:
        return
    if author_first and len(author_first) > 100:
        return

    title = title.replace("’", "'")
    if author_first:
        author_first = author_first.replace("’", "'")
    author_last = author_last.replace("’", "'")

    return ABook(
        title=title,
        author_first=author_first,
        author_last=author_last,
        publication_year=int(publication_year) if publication_year else None,
        translator=None,
        url=f"https://ebooks.adelaide.edu.au/{href}"
    )


def crawl() -> None:
    """
    Pull all information from Adelaide's site, by crawling each of its 26
    alphbetical title listings.  Save to the database.
    """
    session = HTMLSession()

    for letter in ascii_uppercase:
        r = session.get(BASE_URL + letter)
        work_div = r.html.find('.works', first=True)

        for work in work_div.find('a'):
            # Pull title from link text
            book = parse_link(work.text, work.attrs['href'])
            if not book:
                continue

            AdelaideWork.objects.update_or_create(
                title=book.title,
                author_last=book.author_last,

                defaults={
                    'author_first': book.author_first,
                    'publication_year': book.publication_year,
                    'translator': book.translator,
                    'url': book.url
                }
            )
