from string import ascii_uppercase
from difflib import SequenceMatcher
import re
from typing import Optional, NamedTuple

from requests_html import HTMLSession

from main.models import AdelaideWork

BASE_URL = 'https://ebooks.adelaide.edu.au/meta/titles/'


# class Book(NamedTuple):
#     title: str
#     author_first: str
#     author_last: str
#     translator: Optional[str]
#     url: str


def crawl() -> None:
    """Pull all information from Adelaide's site, by crawling each of its 26
    alphbetical title listings."""
    session = HTMLSession()

    split_title_author_re = r'(.*) / (.*?)(with an introduction.*)? \[\d{4}\]'
    split_translator_re = r'(.*); translated (.*)'

    for letter in ascii_uppercase:
        r = session.get(BASE_URL + letter)
        work_div = r.html.find('.works', first=True)

        works = work_div.find('a')

        for work in works:
            # Pull title from link text
            match = re.match(split_title_author_re, work.text)
            if not match:
                continue
            title, author, _ = match.groups()

            translator = None
            translator_match = re.match(split_translator_re, author)
            if translator_match:
                author, translator = translator_match.groups()

            # Divide author into first and last names.
            # Note: This is imperfect.
            author = author.split(' ')
            if len(author) == 1:
                author_first, author_last = '', author[0]
            else:
                *author_first, author_last = author
                author_first = ' '.join(author_first)

            if len(title) > 150 or len(author_first) > 100 or len(author_last) > 100:
                continue

            AdelaideWork.objects.update_or_create(
                title=title,
                author_last=author_last,

                defaults={
                    'author_first': author_first,
                    'translator': translator,
                    'url': f"https://ebooks.adelaide.edu.au{work.attrs['href']}"

                }
            )
