import re
from typing import TextIO, NamedTuple, Optional

import requests

from main.models import Source, WorkSource, GutenbergWork
from . import util


# Gutenberg forbids using automated tools to parse their site directly, but provides
# feeds and catalogs.

# ie Don't use this:
# 'http://www.gutenberg.org/ebooks/search/?query='

# Use this instead:
# http://www.gutenberg.org/wiki/Gutenberg:Feeds


# I have no idea how to parse the machine-readable RDF package; looks
# like the plain text index with title, author and id may be the best bet.


class GbBook(NamedTuple):
    # Information stored in an Abook (And for similar tuples in API files) encloses
    # The information the source contains; we may not use all of it in the db, or may
    # wish for more.
    internal_id: int
    title: str
    author_first: Optional[str]
    author_last: str
    language: Optional[str]
    illustrator: Optional[str]
    subtitle: Optional[str]
    editor: Optional[str]

    def __repr__(self):
        return f"title: {self.title}\nauthor: {self.author_first} {self.author_last}\n" \
               f"id: {self.internal_id}\nlanguage: {self.language}" \
               f"\nillustrator: {self.illustrator}\nsubtitle: {self.subtitle}"


def download_index() -> None:
    """Downloads the gutenberg index file, and saves it locally."""
    INDEX_URL = 'http://www.gutenberg.org/dirs/GUTINDEX.ALL'
    r = requests.get(INDEX_URL)
    # todo Consider where you should put this file.
    with open('GUTINDEX.ALL', 'wb') as f:
        f.write(r.content)


def parse_entry(text: str) -> Optional[GbBook]:
    """This parser assumes the text is already split by \n\n."""
    split_data_id_data = r'(.*?)\s{3,}(\d{1,5})\n?(.*)'
    match = re.match(split_data_id_data, text)
    if not match:
        return

    part1, internal_id, part2 = match.groups()
    internal_id = int(internal_id)
    trimmed = part1 + part2

    # There's probably a way to match an arbitrary number of bracketed patterns,
    # but I can't find it; manually allowing up to 3.
    # todo foreign substitutions for 'by'

    split_title_author_extras = r'(.*?)\,\s+by\s+(.*?)\s*(\[.*\])?\s*(\[.*\])?\s*(\[.*\])?$'
    match2 = re.match(split_title_author_extras, trimmed)
    if not match2:
        return

    title, author, extras1, extras2, extras3 = match2.groups()

    author_first, author_last = util.split_author(author)

    # Pull language, subtitle, illustrator etc from extras, if available.
    language, illustrator, subtitle, editor = None, None, None, None

    for extra in (extras1, extras2, extras3):
        if not extra:
            continue
        extra = extra.replace('[', '').replace(']', '')

        subtitle_match = re.match(r'Subtitle:\s+(.*)', extra)
        if subtitle_match:
            subtitle = subtitle_match.groups()[0]
            continue

        illustrator_match = re.match(r'Illustrator:\s+(.*)', extra)
        if illustrator_match:
            illustrator = illustrator_match.groups()[0]
            continue

        language_match = re.match(r'Language:\s+(.*)', extra)
        if language_match:
            language = language_match.groups()[0]
            continue

        editor_match = re.match(r'Editor:\s+(.*)', extra)
        if editor_match:
            editor = editor_match.groups()[0]
            continue

    return GbBook(
        internal_id=internal_id,
        title=title,
        author_first=author_first,
        author_last=author_last,
        language=language,
        illustrator=illustrator,
        subtitle=subtitle,
        editor=editor,
    )


def populate_from_index(filename: str='GUTINDEX.ALL') -> None:
    """Populate Gutenberg works from the index."""
    with open(filename, encoding='utf8') as f:
        # Split into pairs of lines, which is what we're looking for
        text = f.read().split('\n\n')
        books = map(parse_entry, text)

    num_passed = 0
    num_failed = 0
    for book in books:
        if not book:
            num_failed += 1
            continue
        if len(book.title) > 150 or len(book.author_first) > 100 or len(
                book.author_last) > 100:
            continue

        GutenbergWork.objects.update_or_create(
            book_id=book.internal_id,

            defaults={
                'title': book.title,
                'author_first': book.author_first,
                'author_last': book.author_last,
                'language': book.author_last,
                'illustrator': book.illustrator,
                'subtitle': book.subtitle,
                'editor': book.editor,
            }
        )
        num_passed += 1

    print(f"Passed: {num_passed}, Failed: {num_failed}")
