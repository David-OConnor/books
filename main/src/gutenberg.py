from typing import Iterator, NamedTuple, TextIO
import re

import requests

from main.models import Source, WorkSource, GutenbergWork


# Gutenberg forbids using automated tools to parse their site directly, but provides
# feeds and catalogs.

# ie Don't use this:
# 'http://www.gutenberg.org/ebooks/search/?query='

# Use this instead:
# http://www.gutenberg.org/wiki/Gutenberg:Feeds


# I have no idea how to parse the machine-readable RDF package; looks
# like the plain text index with title, author and id may be the best bet.


def populate_from_index() -> None:
    INDEX_URL = 'http://www.gutenberg.org/dirs/GUTINDEX.ALL'
    r = requests.get(INDEX_URL)

    # Split into pairs of lines, which is what we're looking for
    text = r.text.split('\r\n\r\n')

    # todo: This regex isn't comprehensive; misses long titles
    # todo that extend onto the second line, foreign languages, etc
    re_str = r'(.*)\, by (.*?)\s+(\d{1,5})'

    # todo fix DRY between here and adelaide.
    for work in text:
        match = re.match(re_str, work)
        if not match:
            continue
        title, author, book_id = match.groups()

        # Divide author into first and last names.
        # Note: This is imperfect.
        author = author.split(' ')
        if len(author) == 1:
            author_first, author_last = '', author[0]
        else:
            *author_first, author_last = author
            author_first = ' '.join(author_first)

        if len(title) > 150 or len(author_first) > 100 or len(
                author_last) > 100:
            continue

        GutenbergWork.objects.update_or_create(
            book_id=book_id,

            defaults={
                'title': title,
                'author_first': author_first,
                'author_last': author_last,
            }
        )

