def url_from_id(internal_id: int) -> str:
    """Find the goodreads URL associated with a book from its id."""
    return f"http://www.librarything.com/work/{internal_id}"
