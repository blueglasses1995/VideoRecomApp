from django.contrib import admin
from .models import Genre, Movie, Post, Comment, PostLike, CommentLike, MovieLike

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(CommentLike)
admin.site.register(MovieLike)