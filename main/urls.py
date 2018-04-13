from django.urls import path

from main import views

urlpatterns = [
    path('books', views.BookList.as_view()),
    path('resources', views.ResourceList.as_view()),
    # path('<int:pk>/', views.BookDetail.as_view()),
    path('search', views.search),
    path('report', views.report),
]
