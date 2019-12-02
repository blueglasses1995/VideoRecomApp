from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<int:movie_id>/', views.show),
    path('<int:movie_id>/movielike/', views.movielike),
    path('view_liked_movie/', views.view_liked_movie),
    path('search/', views.IndexView.as_view()),
]