from django.contrib import admin

from django.contrib.admin import ModelAdmin, register

from .models import Work, Author, Isbn, Resource, Source, WorkSource


@register(Work)
class WorkAdmin(ModelAdmin):
    list_display = ('title', 'author', 'genre')


@register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name')


@register(Isbn)
class IsbnAdmin(ModelAdmin):
    list_display = ('isbn', 'work')


@register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ('name', 'website_url')


@register(Source)
class SourceAdmin(ModelAdmin):
    list_display = ('name', 'url', 'information', 'free_downloads', 'purchases')


@register(WorkSource)
class WorkSourceAdmin(ModelAdmin):
    list_display = ('work', 'source', 'price', 'epub_avail', 'kindle_avail')