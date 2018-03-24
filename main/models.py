from django.db import models
from django.db.models import SET_NULL

from django.core.validators import validate_comma_separated_integer_list

TAGS = (
    (0, 'sci-fi'),
    (1, 'romance'),
    (2, 'non-fiction'),
    (3, 'science'),
    (4, 'language'),
    (5, 'philosophy'),
    (6, 'comedy'),
    (7, 'satire'),
    (8, 'OCA'),
    (9, 'SCAR'),
    (10, 'OCF'),
    (11, 'Red air'),
)


class Author(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ISBN(models.Model):
    isbn_10 = models.TextField(unique=True)
    isbn_13 = models.TextField(unique=True)
    publication_date = models.DateField(null=True)


# Create your models here.
class Book(models.Model):
    isbn = models.ForeignKey(ISBN, on_delete=models.CASCADE)

    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    genre = models.CharField(max_length=50, validators=[validate_comma_separated_integer_list])

    wikipedia_url = models.CharField(max_length=50, blank=True, null=True)
    amazon_url = models.CharField(max_length=50, blank=True, null=True)
    gutenberg_url = models.CharField(max_length=50, blank=True, null=True)
    adelaide_url = models.CharField(max_length=50, blank=True, null=True)
    google_url = models.CharField(max_length=50, blank=True, null=True)
    kobo_url = models.CharField(max_length=50, blank=True, null=True)

    copyright_exp_us = models.DateField(null=True)
    # todo this will probably get removed in favor of checking the date.
    copyright_expired = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}, by {self.author}"

    class Meta:
        ordering = ('author', 'title')
        unique_together = ('author', 'title')


class Resource(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    website_url = models.CharField(max_length=50, blank=True, null=True)
    download_url = models.CharField(max_length=50, blank=True, null=True)
