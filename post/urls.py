from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('create_view/', views.create_view),
    path('upload/', views.upload),
    path('<int:post_id>/', views.index, name='post'),
    path('<int:post_id>/modify/', views.modify),
    path('<int:post_id>/update/', views.update),
    path('<int:post_id>/confirm_delete/', views.confirm_delete),
    path('<int:post_id>/delete/', views.delete),
    path('<int:comment_id>/modify_comment/', views.modify_comment),
    path('<int:comment_id>/update_comment/', views.update_comment),
    path('<int:comment_id>/confirm_delete_comment/', views.confirm_delete_comment),
    path('<int:comment_id>/delete_comment/', views.delete_comment),
    url(r'^(?P<post_id>[0-9]+)/postlike/$', views.postlike, name='postlike'),
    url(r'^(?P<comment_id>[0-9]+)/commentlike/$', views.commentlike, name='commentlike'),
    path('view_liked_post/', views.view_liked_post),
]