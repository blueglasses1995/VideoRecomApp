from django.contrib import admin
from .models import Genre, Movie, Post, Comment

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Post)
admin.site.register(Comment)