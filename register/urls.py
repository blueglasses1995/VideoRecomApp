from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('create_user/', views.create_user, name='create_user'),
    path('create_user_view/', views.create_user_view),
#    path('check/', views.check)
]