import re

from django.db.models.query import QuerySet

from .models import Book, Author


def search(query: str) -> QuerySet:
    pass