from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('create_view/', views.create_view),
    path('upload/', views.upload),
    path('<int:post_id>/modify/', views.modify),
    path('<int:post_id>/update/', views.update),
    path('<int:post_id>/confirm_delete/', views.confirm_delete),
    path('<int:post_id>/delete/', views.delete),
    path('<int:post_id>/', views.index),
]