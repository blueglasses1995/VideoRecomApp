from django.shortcuts import render, redirect, get_object_or_404
from VideoRecomApp.models import Movie, Post, MovieLike
from VideoRecomApp.forms import SearchForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.db.models import Q

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

@login_required
def movielike(request, *args, **kwargs):
    movie = Movie.objects.get(id=kwargs['movie_id'])
    is_like = MovieLike.objects.filter(user=request.user).filter(movie=movie).count()
    # unlike
    if is_like > 0:
        liking = MovieLike.objects.get(movie__id=kwargs['movie_id'], user=request.user)
        liking.delete()
        movie.like_num -= 1
        movie.save()
        messages.warning(request, 'いいねを取り消しました')
        return redirect('/')
    # like
    movie.like_num += 1
    movie.save()
    like = MovieLike()
    like.user = request.user
    like.movie = movie
    like.save()
    messages.success(request, 'いいね！しました')
    return redirect('/')


@login_required
def view_liked_movie(request):
    movielikes = MovieLike.objects.filter(user=request.user)
    # ログインユーザー自身の情報
    login_user = request.user
    return render(request, 'movie/view_liked_movie.html', {'movielikes': movielikes, 'login_user': login_user})

class IndexView(LoginRequiredMixin, generic.ListView):

    paginate_by = 5
    template_name = 'movie/search.html'
    model = Movie

    def post(self, request, *args, **kwargs):
        form_value = [
            self.request.POST.get('title', None),
            self.request.POST.get('genre', None),
            self.request.POST.get('keyword', None),
        ]
        request.session['form_value'] = form_value

        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        title = ''
        genre = ''
        keyword = ''
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            title = form_value[0]
            genre = form_value[1]
            keyword = form_value[2]

        default_data = {'title': title,  # タイトル
                        'genre' : genre,  # 内容
                        'keyword': keyword,  # キーワード
                        }

        test_form = SearchForm(initial=default_data) # 検索フォーム
        context['test_form'] = test_form

        # ログインユーザー自身の情報
        login_user = self.request.user
        context['login_user'] = login_user

        return context

    def get_queryset(self):

        # sessionに値がある場合、その値でクエリ発行する。
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            title = form_value[0]
            genre = form_value[1]
            keyword = form_value[2]

            # 検索条件
            condition_title = Q()
            condition_genre = Q()
            condition_keyword = Q()

            if len(title) != 0 and title[0]:
                condition_title = Q(title__icontains=title)
            if len(genre) != 0 and genre[0]:
                condition_genre = Q(genre__contains=genre)
            if len(keyword) != 0 and keyword[0]:
                condition_keyword = Q(summary__contains=keyword)

            return Movie.objects.select_related().filter(condition_title & condition_genre & condition_keyword)
        else:
            # 何も返さない
            return Movie.objects.none()