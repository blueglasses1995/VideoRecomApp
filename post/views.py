from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from . import models
from VideoRecomApp.models import Post, Comment, PostLike, CommentLike
from VideoRecomApp.forms import PostForm, CommentForm
from hashlib import md5
from django.contrib import messages

# Create your views here.
@login_required
def index(request, post_id):
    #ログインユーザー自身の情報
    post = Post.objects.get(id=post_id)
    login_user = request.user
    form = CommentForm
    return render(request, 'post/post.html', {'form': form, 'post': post, 'login_user': login_user})

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

@login_required
def upload_comment(request, post_id):
    # POST データから新たなフォームインスタンスを生成
    commentform = CommentForm(request.POST)

    if commentform.is_valid():
        # フォームデータから新たな Article オブジェクトを生成
        comment = commentform.save(commit=False)
        comment.post_id = Post.objects.get(pk=post_id)
        comment.user = request.user
        comment.save()  # この段階でDBに保存されます
        # Without this next line the tags won't be saved.
        commentform.save_m2m()
    #else

    return redirect('post', post_id=post_id)

@login_required
def modify_comment(request, comment_id):
    #ログインユーザー自身の情報
    login_user = request.user
    comment = Comment.objects.get(pk=comment_id)
    form = CommentForm(request.POST)
    return render(request, 'post/modify_comment.html', {'comment': comment, 'form': form, 'login_user': login_user})

@login_required
def update_comment(request, comment_id):
    # POST データから新たなフォームインスタンスを生成
    if comment_id:   # book_id が指定されている (修正時)
        comment = get_object_or_404(Comment, pk=comment_id)
    else:         # book_id が指定されていない (追加時)
        comment = Comment()

    commentform = CommentForm(request.POST, instance=comment)

    if commentform.is_valid():
        # フォームデータから新たな Article オブジェクトを生成
        comment = commentform.save(commit=False)
        comment.user = request.user
        comment.save()  # この段階でDBに保存されます
        # Without this next line the tags won't be saved.
        commentform.save_m2m()
    #else

    login_user = request.user
    #【ＴＯＤＯ】投稿ページに戻す
    post_id = comment.post_id.id
    return redirect('post', post_id=post_id)

def confirm_delete_comment(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)

    # ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'post/confirm_delete_comment.html', {'comment': comment, 'login_user': login_user})

@login_required
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        post_id = comment.post_id.id
    except models.Article.DoesNotExist:
        raise Http404
    comment.delete()

    #ログインユーザー自身の情報
    login_user = request.user
    #【ＴＯＤＯ】投稿ページに戻す
    return redirect('post', post_id=post_id)

@login_required
def postlike(request, *args, **kwargs):
    post = Post.objects.get(id=kwargs['post_id'])
    is_like = PostLike.objects.filter(user=request.user).filter(post=post).count()
    # unlike
    if is_like > 0:
        liking = PostLike.objects.get(post__id=kwargs['post_id'], user=request.user)
        liking.delete()
        post.like_num -= 1
        post.save()
        messages.warning(request, 'いいねを取り消しました')
        return redirect(reverse_lazy('post', kwargs={'post_id': kwargs['post_id']}))
    # like
    post.like_num += 1
    post.save()
    like = PostLike()
    like.user = request.user
    like.post = post
    like.save()
    messages.success(request, 'いいね！しました')
    return HttpResponseRedirect(reverse_lazy('post', kwargs={'post_id': kwargs['post_id']}))

@login_required
def commentlike(request, *args, **kwargs):
    comment = Comment.objects.get(id=kwargs['comment_id'])
    is_like = CommentLike.objects.filter(user=request.user).filter(comment=comment).count()
    post_id = comment.post_id.id
    # unlike
    if is_like > 0:
        liking = CommentLike.objects.get(comment__id=kwargs['comment_id'], user=request.user)
        liking.delete()
        comment.like_num -= 1
        comment.save()
        messages.warning(request, 'いいねを取り消しました')
        return redirect('post', post_id=post_id)
    # like
    comment.like_num += 1
    comment.save()
    like = CommentLike()
    like.user = request.user
    like.comment = comment
    like.save()
    messages.success(request, 'いいね！しました')
    return redirect('post', post_id=post_id)

@login_required
def view_liked_post(request):
    postlikes = PostLike.objects.filter(user=request.user)
    # ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'post/view_liked_post.html', {'postlikes': postlikes, 'login_user': login_user})