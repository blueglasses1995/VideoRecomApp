# Generated by Django 2.2.6 on 2020-01-05 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
        ),
        migrations.AddField(
            model_name='review',
            name='movies',
            field=models.ManyToManyField(blank=True, related_name='reviews', to='movie.Movie', verbose_name='相关电影'),
        ),
        migrations.AddField(
            model_name='review',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='reviews', to='movie.Tag', verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='profile',
            name='disliked_comments',
            field=models.ManyToManyField(blank=True, related_name='users_disliked', to='movie.Comment', verbose_name='不喜欢的短评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='disliked_friends',
            field=models.ManyToManyField(blank=True, related_name='_profile_disliked_friends_+', to='movie.Profile', verbose_name='不喜欢的好友'),
        ),
        migrations.AddField(
            model_name='profile',
            name='disliked_movies',
            field=models.ManyToManyField(blank=True, related_name='users_disliked', to='movie.Movie', verbose_name='不喜欢的电影'),
        ),
        migrations.AddField(
            model_name='profile',
            name='disliked_reviews',
            field=models.ManyToManyField(blank=True, related_name='users_disliked', to='movie.Review', verbose_name='不喜欢的影评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='favourite_comments',
            field=models.ManyToManyField(blank=True, related_name='users_favourite', to='movie.Comment', verbose_name='收藏的短评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='favourite_friends',
            field=models.ManyToManyField(blank=True, related_name='_profile_favourite_friends_+', to='movie.Profile', verbose_name='收藏的好友'),
        ),
        migrations.AddField(
            model_name='profile',
            name='favourite_movies',
            field=models.ManyToManyField(blank=True, related_name='users_favourite', to='movie.Movie', verbose_name='收藏的电影'),
        ),
        migrations.AddField(
            model_name='profile',
            name='favourite_reviews',
            field=models.ManyToManyField(blank=True, related_name='users_favourite', to='movie.Review', verbose_name='收藏的影评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='liked_comments',
            field=models.ManyToManyField(blank=True, related_name='users_liked', to='movie.Comment', verbose_name='喜欢的短评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='liked_friends',
            field=models.ManyToManyField(blank=True, related_name='_profile_liked_friends_+', to='movie.Profile', verbose_name='喜欢的好友'),
        ),
        migrations.AddField(
            model_name='profile',
            name='liked_movies',
            field=models.ManyToManyField(blank=True, related_name='users_liked', to='movie.Movie', verbose_name='喜欢的电影'),
        ),
        migrations.AddField(
            model_name='profile',
            name='liked_reviews',
            field=models.ManyToManyField(blank=True, related_name='users_liked', to='movie.Review', verbose_name='喜欢的影评'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='watch_list',
            field=models.ManyToManyField(blank=True, related_name='users_added_watch_list', to='movie.Movie', verbose_name='观看记录'),
        ),
        migrations.AddField(
            model_name='movie',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='movies', to='movie.Genre', verbose_name='类别'),
        ),
        migrations.AddField(
            model_name='movie',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='movies', to='movie.Tag', verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='grade',
            name='movie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movie_user_grade', to='movie.Movie', verbose_name='相关电影'),
        ),
        migrations.AddField(
            model_name='grade',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_grade', to=settings.AUTH_USER_MODEL, verbose_name='影迷'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='短评作者'),
        ),
        migrations.AddField(
            model_name='comment',
            name='movie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='movie.Movie', verbose_name='相关的电影'),
        ),
        migrations.AddField(
            model_name='comment',
            name='review',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='movie.Review', verbose_name='相关的短评'),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together={('movie', 'user')},
        ),
    ]
