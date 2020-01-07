from django.urls import path

from . import views

app_name = 'movie'


urlpatterns = [
    path('movie_create', views.movie_create, name='movie_create'),
    path('movie_info/<int:movie_id>', views.movie_info, name='movie_info'),
    path('movie_list', views.movie_list, name='movie_list'),
    path('movie_search', views.search, name='movie_search'),
    path('movie_like/<int:movie_id>', views.movie_like, name='movie_like'),
    path('movie_dislike/<int:movie_id>', views.movie_dislike, name='movie_dislike'),
    path('movie_favourite/<int:movie_id>', views.movie_favourite, name='movie_favourite'),
    path('movie_watch/<int:movie_id>', views.movie_watch, name='movie_watch'),
    path('movie_score/<int:movie_id>/<str:score>', views.movie_score, name='movie_score'),

    path('comment_like/<int:comment_id>', views.comment_like, name='comment_like'),
    path('comment_dislike/<int:comment_id>', views.comment_dislike, name='comment_dislike'),
    path('comment_favourite/<int:comment_id>', views.comment_favourite, name='comment_favourite'),

    path('review_create', views.review_create, name='review_create'),
    path('review_info/<int:review_id>', views.review_info, name='review_info'),
    path('review_list', views.review_list, name='review_list'),
    path('review_like/<int:review_id>', views.review_like, name='review_like'),
    path('review_dislike/<int:review_id>', views.review_dislike, name='review_dislike'),
    path('review_favourite/<int:review_id>', views.review_favourite, name='review_favourite'),

    path('tag_create/<str:tag_name>', views.tag_create, name='tag_create'),
    path('tag_list', views.tag_list, name='tag_list'),

    path('genre_create/<str:genre_name>', views.genre_create, name='genre_create'),
    path('genre_list', views.genre_list, name='genre_list'),

    path('user_profile_info', views.user_profile_info, name='user_profile_info'),
    path('user_profile_favourite_movies', views.user_profile_favourite_movies, name='user_profile_favourite_movies'),
    path('user_profile_favourite_reviews', views.user_profile_favourite_reviews, name='user_profile_favourite_reviews'),
    path('user_profile_published_reviews', views.user_profile_published_reviews, name='user_profile_published_reviews'),
    path('user_profile_favourite_users', views.user_profile_favourite_users, name='user_profile_favourite_users'),
    path('user_profile_notices', views.user_profile_notices, name='user_profile_notices'),

    path('profile_like/<int:profile_id>', views.profile_like, name='profile_like'),
    path('profile_dislike/<int:profile_id>', views.profile_dislike, name='profile_dislike'),
    path('profile_favourite/<int:profile_id>', views.profile_favourite, name='profile_favourite'),

    path('get_new_notices_num', views.get_new_notices_num, name='get_new_notices_num'),
    path('open_notice/<int:notice_id>', views.open_notice, name='open_notice'),

    path('', views.index, name='index'),
]
