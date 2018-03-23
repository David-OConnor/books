from django.urls import path
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('books', views.BookList.as_view()),
    path('<int:pk>/', views.BookDetail.as_view()),
    path('search/', views.search),

    # For django-webpack-loader; testing.
    path('test', TemplateView.as_view(template_name="index.html")),

]
