from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    path('', views.BookList),
    # path('', views.BookList),
    # url(r'^', include('main.urls')),
]

# urlpatterns = [
#     url(r'^main/$', views.BookList),
#     url(r'^main/(?P<pk>[0-9]+)/$', views.BookDetail),
# ]