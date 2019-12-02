from django.db import models
from .models import Post, Comment
from django.forms import Form, CharField, URLField, ModelForm
from django import forms

class PostForm(ModelForm):
    """投稿画面用のフォーム"""
    class Meta:
        #利用するモデルクラスを設定
        model = Post
        #利用するモデルのフィールドを設定
        fields = ('movie', 'tags', 'content')

class CommentForm(ModelForm):
    """投稿画面用のフォーム"""
    class Meta:
        #利用するモデルクラスを設定
        model = Comment
        #利用するモデルのフィールドを設定
        fields = ('content',)

class SearchForm(Form):
    title = forms.CharField(
        initial='',
        label='タイトル',
        required = False, # 必須ではない
    )
    genre = forms.CharField(
        initial='',
        label='ジャンル',
        required = False, # 必須ではない
    )
    keyword = forms.CharField(
        initial='',
        label='キーワード',
        required = False, # 必須ではない
    )