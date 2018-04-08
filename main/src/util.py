from typing import Tuple


def split_author(author: str) -> Tuple[str, str]:
    """Split an author string into first and last names. Middle names, initials
    etc go in the first name."""
    author = author.split(' ')
    if len(author) == 1:
        author_first, author_last = None, author[0]
    else:
        # If len is more than 2, it may be initials or a middle name; group these
        # into the first name.
        *author_first, author_last = author
        author_first = ' '.join(author_first)
    return author_first, author_last
