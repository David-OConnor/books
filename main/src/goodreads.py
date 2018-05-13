def url_from_id(internal_id: int) -> str:
    """Find the goodreads URL associated with a book from its id."""
    return f"https://www.goodreads.com/book/show/{internal_id}"
