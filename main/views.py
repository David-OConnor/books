from io import BytesIO

import saturn
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from .models import Work, Resource, ContactMessage, Report
from .serializers import WorkSerializer, UserSerializer, GroupSerializer, \
    ResourceSerializer
from .src import db


class BookList(generics.ListCreateAPIView):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    permission_classes = (permissions.IsAdminUser,)


class ResourceList(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer


@api_view(['POST'])
def search(request):
    title, author = request.data['title'], request.data['author']

    results = db.search_or_update(title, author)
    return Response(WorkSerializer(results, many=True).data)


@api_view(['POST'])
def report(request):
    # s = WorkSerializer(data=request.data['books'])
    # s.is_valid()
    # print(s.validated_data)
    #
    # stream = BytesIO(request.data['books'])
    # data = JSONParser().parse(stream)
    # serializer = WorkSerializer(data=data)
    # serializer.is_valid()
    # works = serializer.validated_data
    # print(works)
    Report.objects.create(
        datetime=saturn.now(),
        title_query=request.data['title'],
        author_query=request.data['author']
    )

    return Response({'success': True})


@api_view(['POST'])
def contact(request):
    """Handle submitting the contact form."""
    ContactMessage.objects.create(
        datetime=saturn.now(),
        name=request.data['name'],
        email=request.data['email'],
        body=request.data['body']
    )

    return Response({'success': True})
