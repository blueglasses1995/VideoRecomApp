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
    like_num = models.IntegerField(default=0)

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
        verbose_name = '映画のタイトル'
    )
    tags = TaggableManager(blank=True, help_text='To make a new tag, add a comma after the new tag name.')  # タグ用フィールド
    tag = models.ManyToManyField(Tag, verbose_name='タグ', blank=True)
    title = models.CharField(max_length=30, verbose_name='投稿タイトル', default='')
    content = models.CharField(max_length=1028, verbose_name='コメント')
    like_num = models.IntegerField(default=0)
    #photo = models.ImageField(upload_to='documents/', default='defo')
    #date_modified

    def get_posts_by_tag(tag_name):
        return Post.objects.filter(tags__name__in=[tag_name])

    def get_article_by_staff():
        return Post.objects.filter(user__is_staff=True)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    #Postクラスからcommentsで逆参照できる
    post_id = models.ForeignKey(
        'Post',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    date_updated = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=256)
    like_num = models.IntegerField(default=0)
    #date_modified

    def __str__(self):
        return self.content

class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE, related_name='postlike')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now_add=True)

class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE, related_name='commentlike')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now_add=True)

class MovieLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE, related_name='movielike')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now_add=True)