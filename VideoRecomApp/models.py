from django.db import models
from django.urls import reverse
from django.conf import settings
from taggit.managers import TaggableManager

class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.PROTECT
    )
    release_date = models.DateField()
    summary = models.CharField(max_length=1028)
    href = models.URLField(max_length=2084)

    def __str__(self):
        return self.title

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(
        'Movie',
        on_delete=models.PROTECT,
        verbose_name = '映画ID'
    )
    tags = TaggableManager(blank=True, help_text='To make a new tag, add a comma after the new tag name.')  # タグ用フィールド
    tag = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    content = models.CharField(max_length=1028, verbose_name='コメント')
    #photo = models.ImageField(upload_to='documents/', default='defo')
    #like_num = models.
    #date_modified

    def get_posts_by_tag(tag_name):
        return Post.objects.filter(tags__name__in=[tag_name])

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    post_id = models.ForeignKey(
        'Post',
        on_delete=models.PROTECT
    )
    date_updated = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=256)
    #like_num = models.
    #date_modified