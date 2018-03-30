from django.contrib.auth.models import User, Group

from rest_framework import serializers

from .models import Work, Author, Isbn, Resource, WorkSource


# class UserSerializer(serializers.HyperlinkedModelSerializer):
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class WorkSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSource
        # Don't include work here, since we're passing worksource as a child
        # of work.  Source gets passed as a child of this.
        # Include id, for React keys.
        fields = ('id', 'source', 'book_url', 'epub_url', 'kindle_url', 'pdf_url',
                  'price', 'purchase_url')
        depth = 1


# class BookSerializer(serializers.HyperlinkedModelSerializer):
class WorkSerializer(serializers.ModelSerializer):
    work_sources = WorkSourceSerializer(many=True)

    class Meta:
        model = Work
        fields = ('id', 'title', 'author', 'genre', 'description', 'work_sources')
        depth = 2  # Allows author, isbn etc to serialize instead of showing the pk.


# class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('first_name', 'last_name')


# class IsbnSerializer(serializers.HyperlinkedModelSerializer):
class IsbnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Isbn
        fields = ('isbn', 'work', 'publication_date')


# class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource
        fields = ('name', 'description', 'website_url', 'download_url')