from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post
from .forms import PostForm, CommentForm

def login_view(request):
    user = authenticate(
        username=request.POST.get('username'),
        password=request.POST.get('password')
    )
    login(request, user)
    user_id = request.user.id
    return redirect('/')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

def index(request):
    return redirect('movie/')
#    return render(request, 'index.html', {'title': '日本の動画の口コミサイト'})

@login_required
def profile(request, pk):
    #アクセスしたアカウントの情報
    user = get_object_or_404(User, pk=pk)
    posts = Post.objects.filter(user=pk).select_related('movie')
        #.prefetch_related('tags')
    #ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'profile.html', {'user': user, 'posts': posts, 'login_user': login_user})

@login_required
def recommendation(request):
    #口コミの出力方法の選択
    #recom_method = request.GET.get('recom_method')
    #recom_str = "おすすめ: " + recom_method
    posts = Post.objects.all()
    #ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'recommendation.html', {'posts': posts, 'login_user': login_user})

@login_required
def tag_recommendation(request, tag_name):
    posts = Post.get_posts_by_tag(tag_name)
    #ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'tag_recommendation.html', {'posts': posts, 'login_user': login_user, 'tag_name': tag_name})


'''
def post(request):
    if request.method == 'POST' and request.POST['title'] and request.POST['href'] and request.POST['description']:
        post = Post.objects.create(
            title = request.POST['title'],
            description = request.POST['description'],
            href = request.POST[href]
        )
        post.save()
    return redirect(to='/')

def form(request):
    form = PostForm()
    return render(request, 'form.html', {'form': form})
'''