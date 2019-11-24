from django.db import models
from .models import Post
from django.forms import Form, CharField, URLField, ModelForm

class PostForm(ModelForm):
    """投稿画面用のフォーム"""
    class Meta:
        #利用するモデルクラスを設定
        model = Post
        #利用するモデルのフィールドを設定
        fields = ('movie', 'tags', 'content')

class CommentForm(Form):
    post_id = models.ForeignKey(
        'Post',
        on_delete=models.PROTECT
    )
    content = models.CharField(max_length=256)