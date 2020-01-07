from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from . import models
from .forms import MovieCreationForm, ShortCommentForm, ReviewCreateForm, UserEditForm
from lxml import html as lxml_html
from django.contrib.sites.shortcuts import get_current_site
from urllib.parse import urlparse
import re, base64, uuid, os
from django.contrib import (auth, messages)
from recommend import settings
# Create your views here.

User = get_user_model()
like_dislike_messages = {
    1: '已经点赞',
    2: '点赞成功',
    3: '已经拍砖',
    4: '拍砖成功',
    5: '取消收藏',
    6: '收藏成功',
    7: '已经看过',
    8: '添加观看',
    9: '打分成功',
    10: '更新打分',
}


@login_required
def movie_create(request):
    if request.method == 'POST':
        form = MovieCreationForm(request.POST, files=request.FILES)

        if form.is_valid():
            movie = form.save()
            return redirect(reverse('movie:movie_info', kwargs={'movie_id': movie.id}))
    else:
        form = MovieCreationForm(instance=models.Movie(rating=9))

    return render(request, 'movie/movie_create.html', context={'form': form})


@login_required
def movie_info(request, movie_id):
    user = request.user

    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    grade = models.Grade.objects.filter(movie=movie, user=user).first()
    if grade is None:
        user_score = movie.rating
    else:
        user_score = grade.grade
    if request.method == 'POST':
        content = request.POST.get('comments', '').strip()
        if len(content) > 1000:
            return JsonResponse(data={
                'status': 'error',
                'msg': '评论内容过长',
            })
        else:
            comment = models.Comment.objects.create(author=user, movie=movie, content=content)
            msg = '{} 评价了电影 “{}”'.format(request.user.username, movie.title)
            url = reverse('movie:movie_info', kwargs={'movie_id': movie.id}) + '#comments-list'
            send_notice(sender=request.user, msg=msg, url=url)
            return JsonResponse(data={
                'status': 'success',
                'msg': '添加评论成功',
                'comment_id': comment.id
            })

    comment_list = movie.comments.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(comment_list, 10)
    try:
        comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        comments = paginator.page(paginator.num_pages)

    return render(
        request,
        'movie/movie_info.html',
        context={'movie': movie, 'user_score': user_score, 'comments': comments})


@login_required
def movie_score(request, movie_id, score):
    '''电影打分'''
    try:
        score = float(score)
    except (TypeError, ValueError):
        return HttpResponse('error', status=500)
    if score < 0 or score > 10:
        return HttpResponse('error', status=500)

    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    user = request.user
    grade = models.Grade.objects.filter(movie=movie, user=user).first()
    if not isinstance(grade, models.Grade):
        grade = models.Grade.objects.create(movie=movie, user=user, grade=score)
        result = 9
    else:
        result = 10
        grade.grade = score
        grade.save()
    grades = movie.movie_user_grade.all()
    grades = [grade.grade for grade in grades]
    avg = round(sum(grades)/len(grades), 2)
    return JsonResponse(data={
        'movie_id': movie.id,
        'my_score': score,
        'average': avg,
        'msg': like_dislike_messages[result]
    })


@login_required
def movie_like(request, movie_id):
    '''点赞'''
    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    profile = request.user.profile
    if movie.users_liked.filter(id=profile.id).count():
        result = 1
    else:
        result = 2
        profile.liked_movies.add(movie)
        profile.save()
        movie.likes = movie.users_liked.count()
        movie.save()
    if movie.users_disliked.filter(id=profile.id).count():
        profile.disliked_movies.remove(movie)
        profile.save()
        movie.dislikes = movie.users_disliked.count()
        movie.save()
    if result == 2:
        msg = '{} 点赞了电影 {}'.format(request.user.username, movie.title)
        url = reverse('movie:movie_info', kwargs={'movie_id': movie.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )

    return JsonResponse(data={
        'movie_id': movie_id,
        'likes': movie.likes,
        'dislikes': movie.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def movie_dislike(request, movie_id):
    '''拍砖'''
    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    profile = request.user.profile
    if movie.users_disliked.filter(id=profile.id).count():
        result = 3
    else:
        result = 4
        profile.disliked_movies.add(movie)
        profile.save()
        movie.dislikes = movie.users_disliked.count()
        movie.save()
    if movie.users_liked.filter(id=profile.id).count():
        profile.liked_movies.remove(movie)
        profile.save()
        movie.likes = movie.users_liked.count()
        movie.save()
    if result == 4:
        msg = '{} 拍砖了电影 {}'.format(request.user.username, movie.title)
        url = reverse('movie:movie_info', kwargs={'movie_id': movie.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )
    return JsonResponse(data={
        'movie_id': movie_id,
        'likes': movie.likes,
        'dislikes': movie.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def movie_favourite(request, movie_id):
    '''收藏'''
    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    profile = request.user.profile
    if movie.users_favourite.filter(id=profile.id).count():
        result = 5
        profile.favourite_movies.remove(movie)
        profile.save()
        movie.favourites = movie.users_favourite.count()
        movie.save()
    else:
        result = 6
        profile.favourite_movies.add(movie)
        profile.save()
        movie.favourites = movie.users_favourite.count()
        movie.save()
    if result == 6:
        msg = '{} 收藏了电影 {}'.format(request.user.username, movie.title)
        url = reverse('movie:movie_info', kwargs={'movie_id': movie.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )

    return JsonResponse(data={
        'movie_id': movie_id,
        'favourites': movie.favourites,
        'msg': like_dislike_messages[result]
    })


@login_required
def movie_watch(request, movie_id):
    '''观看'''
    movie = get_object_or_404(klass=models.Movie, id=movie_id)
    profile = request.user.profile

    result = 8
    profile.watch_list.add(movie)
    profile.save()
    movie.watches += 1
    movie.save()

    # if movie.users_added_watch_list.filter(id=profile.id).count():
    #     result = 7
    # else:
    #     result = 8
    #     profile.watch_list.add(movie)
    #     profile.save()
    #     movie.watches = movie.users_added_watch_list.count()
    #     movie.save()
    if True:
        msg = '{} 观看了电影 {}'.format(request.user.username, movie.title)
        url = reverse('movie:movie_info', kwargs={'movie_id': movie.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )

    return JsonResponse(data={
        'movie_id': movie_id,
        'watches': movie.watches,
        'msg': like_dislike_messages[result],
        'url': movie.link_to_watch
    })


def tag_create(request, tag_name: str):
    tag_name = tag_name.strip()
    if not tag_name:
        return JsonResponse({'msg': 'empty tag content', 'status': 'error'}, status=500)
    tag = models.Tag.objects.filter(name__iexact=tag_name).first()
    if isinstance(tag, models.Tag):
        return JsonResponse({'msg': '', 'data': {'id': tag.id, 'name': tag.name}, 'status': 'success', 'action': 'exist'})
    tag = models.Tag.objects.create(name=tag_name)
    return JsonResponse({'msg': '', 'data': {'id': tag.id, 'name': tag.name}, 'status': 'success', 'action': 'update'}, status=201)


def tag_list(request):
    tags = []
    for tag in models.Tag.objects.all():
        tags.append({'id': tag.id, 'name': tag.name})
    return JsonResponse(data={'msg': '', 'data': tags, 'status': 'success'})


def genre_create(request, genre_name: str):
    genre_name = genre_name.strip()
    if not genre_name:
        return JsonResponse({'msg': 'empty genre content', 'status': 'error'}, status=500)
    genre = models.Genre.objects.filter(name__iexact=genre_name).first()
    if isinstance(genre, models.Genre):
        return JsonResponse({'msg': '', 'data': {'id': genre.id, 'name': genre.name}, 'status': 'success', 'action': 'exist'})
    genre = models.Genre.objects.create(name=genre_name)
    return JsonResponse(
        data={'msg': '', 'data': {'id': genre.id, 'name': genre.name}, 'status': 'success', 'action': 'update'},
        status=201)


def genre_list(request):
    genres = []
    for genre in models.Genre.objects.all():
        genres.append({'id': genre.id, 'name': genre.name})
    return JsonResponse(data={'msg': '', 'data': genres, 'status': 'success'})


@login_required
def comment_like(request, comment_id):
    '''点赞'''
    comment = get_object_or_404(klass=models.Comment, id=comment_id)
    profile = request.user.profile
    if comment.users_liked.filter(id=profile.id).count():
        result = 1
    else:
        result = 2
        profile.liked_comments.add(comment)
        profile.save()
        comment.likes = comment.users_liked.count()
        comment.save()
    if comment.users_disliked.filter(id=profile.id).count():
        profile.disliked_comments.remove(comment)
        profile.save()
        comment.dislikes = comment.users_disliked.count()
        comment.save()

    return JsonResponse(data={
        'comment_id': comment_id,
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def comment_dislike(request, comment_id):
    '''拍砖'''
    comment = get_object_or_404(klass=models.Comment, id=comment_id)
    profile = request.user.profile
    if comment.users_disliked.filter(id=profile.id).count():
        result = 3
    else:
        result = 4
        profile.disliked_comments.add(comment)
        profile.save()
        comment.dislikes = comment.users_disliked.count()
        comment.save()
    if comment.users_liked.filter(id=profile.id).count():
        profile.liked_comments.remove(comment)
        profile.save()
        comment.likes = comment.users_liked.count()
        comment.save()


    return JsonResponse(data={
        'comment_id': comment_id,
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def comment_favourite(request, comment_id):
    '''收藏'''
    comment = get_object_or_404(klass=models.Comment, id=comment_id)
    profile = request.user.profile
    if comment.users_favourite.filter(id=profile.id).count():
        result = 5
        profile.favourite_comments.remove(comment)
        profile.save()
        comment.favourites = comment.users_favourite.count()
        comment.save()
    else:
        result = 6
        profile.favourite_comments.add(comment)
        profile.save()
        comment.favourites = comment.users_favourite.count()
        comment.save()
    return JsonResponse(data={
        'comment_id': comment_id,
        'favourites': comment.favourites,
        'msg': like_dislike_messages[result]
    })


def parse_review(content, domain):
    tree = lxml_html.fromstring(content)
    movies = []
    for a in tree.xpath('//a'):
        url = a.attrib.get('href', '')
        if url:
            p = urlparse(url)
            if p.path.startswith('/movie/movie_info/'):
                if p.netloc:
                    if p.netloc != domain:
                        continue
                ids = re.findall(r'/movie/movie_info/(\d+)', p.path)
                if ids:
                    movie_id = int(ids[0])
                    movie = models.Movie.objects.filter(id=movie_id).first()
                    if movie is not None:
                        movies.append(movie)

    cover_img = ''
    for img in tree.xpath('//img'):
        src = img.attrib.get('src', '')
        if src and src[0] in ['/', 'h', 'f']:
            cover_img = src
            break
    return movies, cover_img


@login_required
def review_create(request):
    '''撰写影评'''
    domain = get_current_site(request).domain
    if request.method == 'POST':
        form = ReviewCreateForm(request.POST, instance=models.Review(author=request.user))
        if form.is_valid():
            content = form.cleaned_data['content']
            review = form.save()
            movies, cover_img = parse_review(content=content, domain=domain)
            if cover_img:
                review.cover = cover_img
            if movies:
                review.movies.add(*movies)
            if movies or cover_img:
                review.save()
            if True:
                msg = '{} 撰写了影评 "{}"'.format(request.user.username, review.title)
                url = reverse('movie:review_info', kwargs={'review_id': review.id})
                send_notice(sender=request.user, msg=msg, url=url)
            return redirect(reverse('movie:review_info', kwargs={'review_id': review.id}))
    else:
        form = ReviewCreateForm(instance=models.Review(author=request.user))

    return render(request, 'movie/review_create.html', context={'form': form})


@login_required
def review_info(request, review_id):
    '''查看影评'''
    review = get_object_or_404(klass=models.Review, id=review_id)
    user = request.user
    if request.method == 'POST':
        content = request.POST.get('comments', '').strip()
        if len(content) > 1000:
            return JsonResponse(data={
                'status': 'error',
                'msg': '评论内容过长',
            }, status=500)
        else:
            comment = models.Comment.objects.create(author=user, review=review, content=content)

            msg = '{} 评价了影评 “{}”'.format(request.user.username, review.title)
            url = reverse('movie:review_info', kwargs={'review_id': review.id}) + '#comments-list'
            send_notice(sender=request.user, msg=msg, url=url)

            return JsonResponse(data={
                'status': 'success',
                'msg': '添加评论成功',
                'comment_id': comment.id
            })

    comment_list = review.comments.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(comment_list, 10)
    try:
        comments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        comments = paginator.page(paginator.num_pages)

    return render(
        request,
        'movie/review_info.html',
        context={'review': review, 'comments': comments})


###
@login_required
def review_like(request, review_id):
    '''点赞'''
    review = get_object_or_404(klass=models.Review, id=review_id)
    profile = request.user.profile
    if review.users_liked.filter(id=profile.id).count():
        result = 1
    else:
        result = 2
        profile.liked_reviews.add(review)
        profile.save()
        review.likes = review.users_liked.count()
        review.save()
    if review.users_disliked.filter(id=profile.id).count():
        profile.disliked_reviews.remove(review)
        profile.save()
        review.dislikes = review.users_disliked.count()
        review.save()
    if result == 2:
        msg = '{} 点赞了影评 {}'.format(request.user.username, review.title)
        url = reverse('movie:review_info', kwargs={'review_id': review.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )
        # 通知作者
        pf = models.ProfileFavourite.objects.filter(me=request.user.profile, friend=review.author.profile).first()
        if not pf:
            send_notice(sender=request.user, receiver=review.author, msg=msg, url=url)
    return JsonResponse(data={
        'review_id': review_id,
        'likes': review.likes,
        'dislikes': review.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def review_dislike(request, review_id):
    '''拍砖'''
    review = get_object_or_404(klass=models.Review, id=review_id)
    profile = request.user.profile
    if review.users_disliked.filter(id=profile.id).count():
        result = 3
    else:
        result = 4
        profile.disliked_reviews.add(review)
        profile.save()
        review.dislikes = review.users_disliked.count()
        review.save()
    if review.users_liked.filter(id=profile.id).count():
        profile.liked_reviews.remove(review)
        profile.save()
        review.likes = review.users_liked.count()
        review.save()

    if result == 4:
        msg = '{} 拍砖了影评 {}'.format(request.user.username, review.title)
        url = reverse('movie:review_info', kwargs={'review_id': review.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )
        # 通知作者
        pf = models.ProfileFavourite.objects.filter(me=request.user.profile, friend=review.author.profile).first()
        if not pf:
            send_notice(sender=request.user, receiver=review.author, msg=msg, url=url)

    return JsonResponse(data={
        'review_id': review_id,
        'likes': review.likes,
        'dislikes': review.dislikes,
        'msg': like_dislike_messages[result]
    })


@login_required
def review_favourite(request, review_id):
    '''收藏'''
    review = get_object_or_404(klass=models.Review, id=review_id)
    profile = request.user.profile
    if review.users_favourite.filter(id=profile.id).count():
        result = 5
        profile.favourite_reviews.remove(review)
        profile.save()
        review.favourites = review.users_favourite.count()
        review.save()
    else:
        result = 6
        profile.favourite_reviews.add(review)
        profile.save()
        review.favourites = review.users_favourite.count()
        review.save()
    if result == 6:
        msg = '{} 收藏了影评 {}'.format(request.user.username, review.title)
        url = reverse('movie:review_info', kwargs={'review_id': review.id})
        send_notice(
            sender=request.user,
            msg=msg,
            url=url
            )
        # 通知作者
        pf = models.ProfileFavourite.objects.filter(me=request.user.profile, friend=review.author.profile).first()
        if not pf:
            send_notice(sender=request.user, receiver=review.author, msg=msg, url=url)

    return JsonResponse(data={
        'review_id': review_id,
        'favourites': review.favourites,
        'msg': like_dislike_messages[result]
    })


@login_required
def movie_list(request):
    query = models.Movie.objects
    # 过滤标签
    _tags = request.GET.get('tags', '')
    _tags = _tags.split(',')
    tags = []
    for t in _tags:
        try:
            t = int(t)
            tags.append(t)
        except (TypeError, ValueError):
            pass
    if tags:
        query = query.filter(tags__in=tags)
    # 过滤类别
    _genres = request.GET.get('genres', '')
    _genres = _genres.split(',')
    genres = []
    for g in _genres:
        try:
            g = int(g)
            genres.append(g)
        except (TypeError, ValueError):
            pass
    if genres:
        query = query.filter(genres__in=genres)
    # 过滤年份
    year_begin = request.GET.get('year_begin', '')
    try:
        year_begin = int(year_begin)
    except (TypeError, ValueError):
        year_begin = None
    if isinstance(year_begin, int):
        query = query.filter(year__gte=year_begin)
    year_end = request.GET.get('year_end', '')
    try:
        year_end = int(year_end)
    except (TypeError, ValueError):
        year_end = None
    if isinstance(year_end, int):
        query = query.filter(year__lte=year_end)
    # 过滤关键词
    accept = request.GET.get('accept', '')
    accept = accept.strip()
    if accept:
        query = query.filter(title__icontains=accept)
    # 排除关键词
    exclude = request.GET.get('exclude', '')
    exclude = exclude.strip()
    if exclude:
        query = query.exclude(title__icontains=exclude)

    movie_list = query.all()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(movie_list, 10)
    try:
        movies = paginator.page(page)
    except (EmptyPage, InvalidPage):
        movies = paginator.page(paginator.num_pages)
    return render(request, 'movie/movie_list.html', context={'movies': movies})


@login_required
def review_list(request):
    query = models.Review.objects
    # 过滤标签
    _tags = request.GET.get('tags', '')
    _tags = _tags.split(',')
    tags = []
    for t in _tags:
        try:
            t = int(t)
            tags.append(t)
        except (TypeError, ValueError):
            pass
    if tags:
        query = query.filter(tags__in=tags)
    # 过滤相关电影
    _movies = request.GET.get('movies', '')
    _movies = _movies.split(',')
    movies = []
    for g in _movies:
        try:
            g = int(g)
            movies.append(g)
        except (TypeError, ValueError):
            pass

    if movies:
        query = query.filter(movies__in=movies)
    
    # 作者id
    author = request.GET.get('author', '')
    try:
        author = int(author)
    except ValueError:
        author = None
    if author:
        query = query.filter(author_id__exact=author)
    # 过滤关键词
    accept = request.GET.get('accept', '')
    accept = accept.strip()
    if accept:
        query = query.filter(title__icontains=accept)
    # 排除关键词
    exclude = request.GET.get('exclude', '')
    exclude = exclude.strip()
    if exclude:
        query = query.exclude(title__icontains=exclude)

    review_list = query.all()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(review_list, 10)
    try:
        reviews = paginator.page(page)
    except (EmptyPage, InvalidPage):
        reviews = paginator.page(paginator.num_pages)
    return render(request, 'movie/review_list.html', context={'reviews': reviews})


@login_required
def user_profile_info(request):
    action = 'user_info'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我的用户信息'
        if request.method == 'POST':
            form = UserEditForm(request.POST, request.FILES, instance=the_user)
            if form.is_valid():
                the_user = form.save()
                if form.cleaned_data['avatar_thumbnail']:
                    i = str(uuid.uuid4())
                    p = models.user_thumbnail_path(the_user, '{}.png'.format(i))
                    fp = os.path.abspath(os.path.join(settings.MEDIA_ROOT, p))

                    form.save_avatar_thumbnail(fp)
                    the_user.thumbnail = p
                    the_user.save()
                messages.success(request, '用户信息更新成功')

        else:
            form = UserEditForm(instance=the_user)
    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 的用户信息'.format(the_user.username)
        form = UserEditForm(instance=the_user)

    return render(
        request,
        'movie/user_profile_info.html',
        context={
            'the_user': the_user,
            'action': action,
            'profile_title': profile_title,
            'from_user': from_user,
            'form': form,
            })


@login_required
def user_profile_favourite_movies(request):
    action = 'movies_favourite'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我收藏的电影'

    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 收藏的电影'.format(the_user.username)

    print(the_user.profile.favourite_movies.count())
    movie_list = the_user.profile.favourite_movies.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(movie_list, 10)
    try:
        movies = paginator.page(page)
    except (EmptyPage, InvalidPage):
        movies = paginator.page(paginator.num_pages)

    return render(request, 'movie/user_profile_favourite_movies.html',
                  context={'the_user': the_user, 'action': action, 'profile_title': profile_title,
                           'from_user': from_user, 'movies': movies})


@login_required
def user_profile_favourite_reviews(request):
    action = 'reviews_favourite'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我收藏的影评'

    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 收藏的影评'.format(the_user.username)

    review_list = the_user.profile.favourite_reviews.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(review_list, 10)
    try:
        reviews = paginator.page(page)
    except (EmptyPage, InvalidPage):
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'movie/user_profile_favourite_reviews.html',
                  context={'the_user': the_user, 'action': action, 'profile_title': profile_title,
                           'from_user': from_user, 'reviews': reviews})


@login_required
def user_profile_published_reviews(request):
    action = 'reviews_published'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我发表的影评'

    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 发表的影评'.format(the_user.username)

    review_list = the_user.reviews.all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(review_list, 10)
    try:
        reviews = paginator.page(page)
    except (EmptyPage, InvalidPage):
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'movie/user_profile_published_reviews.html',
                  context={'the_user': the_user, 'action': action, 'profile_title': profile_title,
                           'from_user': from_user, 'reviews': reviews})


@login_required
def user_profile_favourite_users(request):
    action = 'user_friends'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我关注的影迷'

    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 关注的影迷'.format(the_user.username)

    friend_list = models.ProfileFavourite.objects.filter(friend=the_user.profile).all()
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(friend_list, 9)
    try:
        friends = paginator.page(page)
    except (EmptyPage, InvalidPage):
        friends = paginator.page(paginator.num_pages)

    return render(
        request,
        'movie/user_profile_favourite_users.html',
                  context={'the_user': the_user, 'action': action, 'profile_title': profile_title,
                           'from_user': from_user, 'friends': friends})


@login_required
def user_profile_notices(request):
    action = 'user_notices'
    user = request.user
    user_id = request.GET.get('user', str(user.id))
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = user.id
    if user_id == user.id:
        the_user = user
        from_user = 'me'
        profile_title = '我的通知'

    else:
        from_user = 'other'
        the_user = get_object_or_404(klass=User, id=user_id)
        profile_title = '{} 的通知'.format(the_user.username)
    only = request.GET.get('only', '')

    if only == 'new':
        notice_list = models.Notice.objects.filter(receiver=the_user, is_read=False).all()
    elif only == 'read':
        notice_list = models.Notice.objects.filter(receiver=the_user, is_read=True).all()
    else:
        notice_list = models.Notice.objects.filter(receiver=the_user).all()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(notice_list, 9)
    try:
        notices = paginator.page(page)
    except (EmptyPage, InvalidPage):
        notices = paginator.page(paginator.num_pages)

    return render(
        request,
        'movie/user_profile_notices.html',
        context={
            'the_user': the_user,
            'action': action,
            'profile_title': profile_title,
            'from_user': from_user,
            'notices': notices}
        )


@login_required
def profile_like(request, profile_id):
    '''点赞'''
    me = get_object_or_404(klass=models.Profile, id=profile_id)
    other = request.user.profile
    like = me.friends_like.filter(friend=other).first()
    if like is None:
        like = models.ProfileLike.objects.create(me=me, friend=other).save()
        result = 2
    else:
        result = 1

    dislike = me.friends_dislike.filter(friend=other).first()
    if dislike:
        dislike.delete()

    return JsonResponse(data={
        'profile_id': me.id,
        'likes': me.friends_like.count(),
        'dislikes': me.friends_dislike.count(),
        'msg': like_dislike_messages[result]
    })


@login_required
def profile_dislike(request, profile_id):
    '''拍砖'''
    me = get_object_or_404(klass=models.Profile, id=profile_id)
    other = request.user.profile
    dislike = me.friends_dislike.filter(friend=other).first()
    if dislike is None:
        dislike = models.ProfileDislike.objects.create(me=me, friend=other)
        dislike.save()
        result = 4
    else:
        result = 3
    like = me.friends_like.filter(friend=other).first()
    if like is not None:
        like.delete()
    return JsonResponse(data={
        'profile_id': me.id,
        'likes': me.friends_like.count(),
        'dislikes': me.friends_dislike.count(),
        'msg': like_dislike_messages[result]
    })


@login_required
def profile_favourite(request, profile_id):
    '''收藏'''
    me = get_object_or_404(klass=models.Profile, id=profile_id)
    other = request.user.profile
    friend = models.ProfileFavourite.objects.filter(me=me, friend=other).first()
    if friend is None:
        result = 5
        friend = models.ProfileFavourite.objects.create(me=me, friend=other)
        friend.save()
    else:
        result = 6
        friend.delete()

    return JsonResponse(data={
        'profile_id': me.id,
        'favourites': me.friends_favourite.count(),
        'msg': like_dislike_messages[result]
    })


def send_notice(sender: User, msg: str, url: str, receiver: User = None):
    if not isinstance(msg, str):
        raise TypeError
    if not isinstance(url, str):
        raise TypeError
    if not msg:
        raise ValueError
    if not url:
        raise ValueError
    if not isinstance(sender, User):
        raise TypeError
    if not isinstance(receiver, User):
        for pf in models.ProfileFavourite.objects.filter(me=sender.profile).all():
            if sender == pf.friend.user:
                continue
            notice = models.Notice.objects.create(sender=sender, receiver=pf.friend.user, msg=msg, url=url)
            notice.save()
    else:
        if sender == receiver:
            return
        notice = models.Notice.objects.create(sender=sender, receiver=receiver, msg=msg, url=url)
        notice.save()


@login_required
def get_new_notices_num(request):
    notices_num = models.Notice.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse(data={
        'status': 'success',
        'notices_num': notices_num,
        'url': reverse('movie:user_profile_notices') + '?only=new'
        })


@login_required
def open_notice(request, notice_id):
    notice = get_object_or_404(klass=models.Notice, id=notice_id)
    if notice.receiver != request.user:
        return HttpResponseNotAllowed('没有权限')
    dismiss = request.GET.get('dismiss', 'no')
    notice.is_read = True
    notice.save()
    if dismiss == 'yes':
        return JsonResponse(data={
            'status': 'success',
            'redirect': False,
            'url': notice.url
            })
    elif dismiss == 'all':
        models.Notice.objects.filter(receiver=request.user).update(is_read=True)
        return JsonResponse(data={
            'status': 'success',
            'redirect': True,
            'url': reverse('movie:user_profile_notices')
            })

    return JsonResponse(data={
            'status': 'success',
            'redirect': True,
            'url': notice.url
        })


def search(request):
    query = models.Movie.objects
    # 过滤标签
    _tags = request.GET.get('tags', '')
    _tags = _tags.split(',')
    tags = []
    for t in _tags:
        try:
            t = int(t)
            tags.append(t)
        except (TypeError, ValueError):
            pass
    if tags:
        query = query.filter(tags__in=tags)
    # 过滤类别
    _genres = request.GET.get('genres', '')
    _genres = _genres.split(',')
    genres = []
    for g in _genres:
        try:
            g = int(g)
            genres.append(g)
        except (TypeError, ValueError):
            pass
    if genres:
        query = query.filter(genres__in=genres)
    # 过滤年份
    _years = request.GET.get('years', '')
    _years = _years.split(',')
    years = []
    for g in _years:
        try:
            g = int(g)
            years.append(g)
        except (TypeError, ValueError):
            pass
    if years:
        query = query.filter(year__in=years)
    # 过滤关键词
    accept = request.GET.get('accept', '')
    accept = accept.strip()
    if accept:
        query = query.filter(title__icontains=accept)
    # 排除关键词
    exclude = request.GET.get('exclude', '')
    exclude = exclude.strip()
    if exclude:
        query = query.exclude(title__icontains=exclude)

    movie_list = query.all()

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(movie_list, 10)
    try:
        movies = paginator.page(page)
    except (EmptyPage, InvalidPage):
        movies = paginator.page(paginator.num_pages)
    print(models.Movie.objects.values('year').distinct())
    return render(
        request,
        'movie/movie_search.html',
        context={
            'movies': movies,
            'tags': sorted(models.Tag.objects.all(), key=lambda x: x.movies.count(), reverse=True),
            'genres': sorted(models.Genre.objects.all(), key=lambda x: x.movies.count(), reverse=True),
            'years': sorted(models.Movie.objects.values('year').distinct(), key=lambda x: x['year'], reverse=True)
            })


@login_required
def index(request):
    user = request.user
    movies = models.Movie.objects.all()
    movies = sorted(movies, key=lambda x: x.likes + x.dislikes * 0.5 + x.favourites + x.watches, reverse=True)[:5]
    watched_movies = user.profile.watch_list.all()
    return render(
        request, 'movie/movie_index.html',
        context={
            'movies': movies,
            'watched_movies': watched_movies
            }
        )
