from django.contrib.auth.models import User, Group

from rest_framework import serializers

from .models import Work, Author, Isbn, Resource


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


# class BookSerializer(serializers.HyperlinkedModelSerializer):
class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ('id', 'title', 'author', 'genre', 'description')
        depth = 1  # Allows author, isbn etc to serialize instead of showing the pk.


# class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('first_name', 'last_name')


# class IsbnSerializer(serializers.HyperlinkedModelSerializer):
class IsbnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Isbn
        fields = ('isbn_10', 'isbn_13', 'publication_date')


# class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource
        fields = ('name', 'description', 'website_url', 'download_url')