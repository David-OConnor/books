import datetime as dt

from django.db import models
from django.db.models import SET_NULL

import saturn

from django.core.validators import validate_comma_separated_integer_list

TAGS = [
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
]


class Author(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Source(models.Model):
    """Information and metadata about a source of free books"""
    name = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=50, unique=True)

    information = models.BooleanField(default=False)
    free_downloads = models.BooleanField(default=False)
    purchases = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Create your models here.
# todo Work?
class Work(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    genre = models.CharField(
        max_length=50, null=True, blank=True,
        validators=[validate_comma_separated_integer_list],
        # choices=TAGS
    )

    description = models.TextField(blank=True, null=True)

    # todo currently duplicated pub date between here and ISBN.
    publication_date = models.DateField(null=True, blank=True)

    def us_copyright_exp(self) -> bool:
        """Calculate if a book's copyright is expired in the US. From rules listed
            here: https://fairuse.stanford.edu/overview/faqs/copyright-basics/ """
        if not self.publication_date:
            return False
        if self.publication_date < saturn.date(1923, 1, 1):
            return True
        if saturn.date(1922, 12, 31) < self.publication_date < saturn.date(1978, 1, 1):
            return self.publication_date + saturn.timedelta(days=365) < saturn.today()

        # "If the work was created, but not published, before 1978, the copyright
        # lasts for the life of the author plus 70 years."
        return False

    def __str__(self):
        return f"{self.title}, by {self.author}"

    class Meta:
        ordering = ('author', 'title')
        unique_together = ('author', 'title')


class Isbn(models.Model):
    # A work may have multiple associated isbns, eg different editions.
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='isbns')
    isbn_10 = models.TextField(unique=True)
    isbn_13 = models.TextField(unique=True)
    publication_date = models.DateField(null=True)

    def __str__(self):
        return f"isbn 10:{self.isbn_10} isbn 13: {self.isbn_13}"


class WorkSource(models.Model):
    work = models.ForeignKey(Work, related_name='work_sources', on_delete=models.CASCADE,)
    source = models.ForeignKey(Source, related_name='work_sources', on_delete=models.CASCADE)
    epub_avail = models.BooleanField()
    kindle_avail = models.BooleanField()

    price = models.FloatField(blank=True, null=True)

    book_url = models.CharField(max_length=100, blank=True, null=True, unique=True)
    download_url = models.CharField(max_length=100, blank=True, null=True, unique=True)


class Resource(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    website_url = models.CharField(max_length=100, blank=True, null=True)
    download_url = models.CharField(max_length=100, blank=True, null=True)


class Config(models.Model):
    about = models.TextField()  # ie text for the about page.


def populate_initial_sources():
    Source.objects.update_or_create(
        name='Google',
        url='https://play.google.com/books/',
        information=True,
        free_downloads=True,
        purchases=True,
    )

    Source.objects.update_or_create(
        name='Wikipedia',
        url='https://www.wikipedia.org/',
        information=True,
    )

    Source.objects.update_or_create(
        name='Amazon',
        url='https://www.amazon.com/Kindle-eBooks/',
        purchases=True
    )

    Source.objects.update_or_create(
        name='Kobo',
        url='https://www.kobo.com/',
        purchases=True
    )

    Source.objects.update_or_create(
        name='Project Gutenberg',
        url='http://www.gutenberg.org/',
        free_downloads=True
    )

    Source.objects.update_or_create(
        name='University of Adelaide Library',
        url='https://ebooks.adelaide.edu.au/',
        free_downloads=True
    )

    Source.objects.update_or_create(
        name='LibraryThing',
        url='https://www.librarything.com/',
        information=True
    )


def populate_initial_resources():
    Resource.objects.update_or_create(
        name="Calibre",
        description="Popular book viewer and editor with lots of options.",
        website_url="https://calibre-ebook.com/",
        download_url="https://calibre-ebook.com/download"
    )

    Resource.objects.update_or_create(
        name="Microsoft Edge",
        description="Epub viewer built into Windows 10",
        website_url="https://support.microsoft.com/en-us/help/4014945/windows-10-read-books-in-the-browser",
        download_url=""
    )

    Resource.objects.update_or_create(
        name="Moon+",
        description="Popular book viewer for Android",
        website_url="http://www.moondownload.com/",
        download_url="http://www.moondownload.com/download.html"
    )

    Resource.objects.update_or_create(
        name="Aldiko",
        description="Popular book viewer for Android.",
        website_url="http://www.aldiko.com/",
        download_url="http://aldiko.com/download.html"
    )
