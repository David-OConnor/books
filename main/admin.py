from django.contrib import admin

from django.contrib.admin import ModelAdmin, register

from .models import Work, Author, Isbn, Resource, Source, WorkSource, \
    AdelaideWork, GutenbergWork


@register(Work)
class WorkAdmin(ModelAdmin):
    list_display = ('title', 'author', 'genre')
    search_fields = ('title', 'author__last_name', 'author__first_name')


@register(AdelaideWork)
class AdelaideWorkAdmin(ModelAdmin):
    list_display = ('title', 'author_first', 'author_last', 'translator')
    search_fields = ('title', 'author_first', 'author_last')


@register(GutenbergWork)
class GutenbergWorkAdmin(ModelAdmin):
    list_display = ('title', 'author_first', 'author_last', 'book_id')
    search_fields = ('title', 'author_first', 'author_last', 'book_id')


@register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')


@register(Isbn)
class IsbnAdmin(ModelAdmin):
    list_display = ('isbn', 'work', 'language', 'publication_date')
    search_fields = ('isbn', 'work__title', 'publication_date')


@register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ('name', 'website_url')


@register(Source)
class SourceAdmin(ModelAdmin):
    list_display = ('name', 'url', 'information', 'free_downloads', 'purchases')


@register(WorkSource)
class WorkSourceAdmin(ModelAdmin):
    list_display = ('work', 'source', 'price')
    search_fields = ('work__title', 'work__author__last_name', 'source__name')
