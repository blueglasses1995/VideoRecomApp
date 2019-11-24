from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from . import models
from VideoRecomApp.models import Post
from VideoRecomApp.forms import PostForm
from hashlib import md5

# Create your views here.
def index(request, post_id):
    #ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'post/post.html', {'post_id': post_id, 'login_user': login_user})

#使用しない
@login_required
def create_view(request):
    #ログインユーザー自身の情報
    login_user = request.user
    form = PostForm
    return render(request, 'post/create_view.html', {'form': form, 'login_user': login_user})

#使用しない
@login_required
def upload(request):
    # POST データから新たなフォームインスタンスを生成
    postform = PostForm(request.POST)

    if postform.is_valid():
        # フォームデータから新たな Article オブジェクトを生成
        post = postform.save(commit=False)
        post.user = request.user
        post.save()  # この段階でDBに保存されます
        # Without this next line the tags won't be saved.
        postform.save_m2m()
    #else

    login_user = request.user
    return redirect('profilepage', pk=login_user.pk)

@login_required
def modify(request, post_id):
    #ログインユーザー自身の情報
    login_user = request.user
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST)
    return render(request, 'post/modify.html', {'post': post, 'form': form, 'login_user': login_user})

@login_required
def update(request, post_id):
    # POST データから新たなフォームインスタンスを生成
    if post_id:   # book_id が指定されている (修正時)
        post = get_object_or_404(Post, pk=post_id)
    else:         # book_id が指定されていない (追加時)
        post = Post()

    postform = PostForm(request.POST, instance=post)

    if postform.is_valid():
        # フォームデータから新たな Article オブジェクトを生成
        post = postform.save(commit=False)
        post.user = request.user
        post.save()  # この段階でDBに保存されます
        # Without this next line the tags won't be saved.
        postform.save_m2m()
    #else

    login_user = request.user
    return redirect('profilepage', pk=login_user.pk)


@login_required
def confirm_delete(request, post_id):
    post = Post.objects.get(pk=post_id)

    # ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'post/confirm_delete.html', {'post': post, 'login_user': login_user})

@login_required
def delete(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except models.Article.DoesNotExist:
        raise Http404
    post.delete()

    #ログインユーザー自身の情報
    login_user = request.user
    return redirect('profilepage', pk=login_user.pk)