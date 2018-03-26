from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Work, Resource
from .serializers import WorkSerializer, UserSerializer, GroupSerializer, \
    ResourceSerializer
from .src import db


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class BookList(generics.ListCreateAPIView):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ResourceList(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Why do I have to use this csrf decorator here, but not on the other views?
# @method_decorator(csrf_exempt, name='dispatch')
@csrf_exempt
@api_view(['POST'])
def search(request):
    title, author = request.data['title'], request.data['author']

    results = db.search_or_update(title, author)
    return Response(WorkSerializer(results, many=True).data)