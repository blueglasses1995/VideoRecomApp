from django.shortcuts import render
from VideoRecomApp.models import Movie, Post

# Create your views here.
def index(request):
    movies = Movie.objects.all().select_related('genre')
    #ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'movie/list.html', {'movies': movies, 'login_user': login_user})

def show(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    #ログインユーザー自身の情報
    login_user = request.user
    posts = Post.objects.filter(movie=movie_id)
    return render(request, 'movie/show.html', {'movie': movie, 'posts': posts, 'login_user': login_user})