from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()


def user_thumbnail_path(user, filename: str):
    return 'avatar/thumbnail/{0}_{1}'.format(user.pk, filename)


class Genre(models.Model):
    '''电影类别'''
    name = models.CharField(max_length=30, unique=True, verbose_name='类别')

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = '类别'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    '''标签'''
    name = models.CharField(max_length=30, unique=True, verbose_name='标签')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    '''电影'''
    title = models.CharField(max_length=50, verbose_name='名称')
    year = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='上映年份'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='简介'
    )
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='评分'
    )
    cover = models.ImageField(verbose_name='电影封面', upload_to='movies')
    link_to_watch = models.URLField(
        null=True,
        blank=True,
        verbose_name='观看地址'
    )
    date_added = models.DateField(auto_now_add=True, verbose_name='添加到后台日期')

    likes = models.IntegerField(default=0, blank=True)
    dislikes = models.IntegerField(default=0, blank=True)
    favourites = models.IntegerField(default=0, blank=True)
    watches = models.IntegerField(default=0, blank=True)

    director = models.CharField(max_length=255, verbose_name='导演')
    production_countries = models.CharField(max_length=255, verbose_name='国家或地区')
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='movies',
        verbose_name='类别'
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='movies',
        verbose_name='标签'
    )

    key_actors = models.CharField(max_length=255, verbose_name='主演',)

    class Meta:
        verbose_name_plural = '电影'
        ordering = ['-date_added']

    def __str__(self):
        return self.title + ', ' + str(self.year)


class Review(models.Model):
    '''影评
    电影的影评，长篇、专业的评价
    '''
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='作者',
    )
    cover = models.CharField(verbose_name='Cover', max_length=128, blank=True, null=True)
    movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='reviews',
        verbose_name='相关电影',
    )
    title = models.CharField(max_length=50, verbose_name='标题')
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name='内容'
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    edit_date = models.DateTimeField(auto_now=True, verbose_name='编辑日期', null=True, blank=True)

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    favourites = models.IntegerField(default=0)

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='reviews',
        verbose_name='标签'
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = '影评'
        verbose_name_plural = verbose_name

    @property
    def cover_url(self):
        if self.cover:
            return self.cover
        return '/static/image/bottleship.jpg'


class Comment(models.Model):
    '''短评
    可以是 电影的 短评，也可以是 影评的 短评，不允许编辑
    '''
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='短评作者',
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='相关的电影',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='相关的短评',
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    content = models.CharField(max_length=1000, verbose_name='内容')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    favourites = models.IntegerField(default=0)

    class Meta:
        verbose_name = '短评'
        verbose_name_plural = '短评'
        ordering = ['-pub_date']


class Grade(models.Model):
    '''用户打分'''
    movie = models.ForeignKey(
        Movie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movie_user_grade',
        verbose_name='相关电影',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_grade',
        verbose_name='影迷',
    )
    date_added = models.DateField(auto_now_add=True, verbose_name='打分日期')
    grade = models.FloatField(
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='打分',
        null=False
    )

    class Meta:
        verbose_name = '用户打分'
        verbose_name_plural = verbose_name
        ordering = '-date_added',
        unique_together = [['movie', 'user']]


class Profile(models.Model):
    '''用户观影档案'''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # movies
    liked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_liked',
        verbose_name='喜欢的电影'
    )

    disliked_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_disliked',
        verbose_name='不喜欢的电影'
    )

    favourite_movies = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_favourite',
        verbose_name='收藏的电影'
    )

    watch_list = models.ManyToManyField(
        Movie,
        blank=True,
        related_name='users_added_watch_list',
        verbose_name='观看记录'
    )
    
    # reviews
    liked_reviews = models.ManyToManyField(
        Review,
        blank=True,
        related_name='users_liked',
        verbose_name='喜欢的影评',
    )
    disliked_reviews = models.ManyToManyField(
        Review,
        blank=True,
        related_name='users_disliked',
        verbose_name='不喜欢的影评',
    )
    favourite_reviews = models.ManyToManyField(
        Review,
        blank=True,
        related_name='users_favourite',
        verbose_name='收藏的影评',
    )

    # comments
    liked_comments = models.ManyToManyField(
        Comment,
        blank=True,
        related_name='users_liked',
        verbose_name='喜欢的短评',
    )
    disliked_comments = models.ManyToManyField(
        Comment,
        blank=True,
        related_name='users_disliked',
        verbose_name='不喜欢的短评',
    )
    favourite_comments = models.ManyToManyField(
        Comment,
        blank=True,
        related_name='users_favourite',
        verbose_name='收藏的短评',
    )

    # friends_liked_num = models.IntegerField(verbose_name='喜欢我的影迷数', default=0)
    #
    # # friends
    # liked_friends = models.ManyToManyField(
    #     'self',
    #     blank=True,
    #     related_name='friends_liked',
    #     verbose_name='喜欢的好友',
    #     )
    #
    # friends_disliked_num = models.IntegerField(verbose_name='不喜欢我的影迷数', default=0)
    # disliked_friends = models.ManyToManyField(
    #     'self',
    #     blank=True,
    #     related_name='friends_disliked',
    #     verbose_name='不喜欢的好友',
    #     )
    # friends_favourite_num = models.IntegerField(verbose_name='关注我的影迷数', default=0)
    # favourite_friends = models.ManyToManyField(
    #     'self',
    #     blank=True,
    #     related_name='friends_favourite',
    #     verbose_name='收藏的好友',
    #     )

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    class Meta:
        verbose_name = '用户观影档案'
        verbose_name_plural = verbose_name


class ProfileFavourite(models.Model):
    me = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='friends_favourite',
        verbose_name='我')
    friend = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='me_favourite',
        verbose_name='关注对象'
        )

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = '关注的好友'
        verbose_name_plural = verbose_name
        unique_together = (('me', 'friend'),)


class ProfileLike(models.Model):
    me = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='friends_like',
        verbose_name='我'
        )
    friend = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='me_like',
        verbose_name='点赞对象')

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = '影迷点赞'
        verbose_name_plural = verbose_name
        unique_together = (('me', 'friend'),)


class ProfileDislike(models.Model):
    me = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='friends_dislike',
        verbose_name='我',
         )
    friend = models.ForeignKey(
        to=Profile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='me_dislike',
        verbose_name='拍砖对象')

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = '影迷拍砖'
        verbose_name_plural = verbose_name
        unique_together = (('me', 'friend'),)


class Notice(models.Model):
    receiver = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='received_notices',
        null=False,
        blank=False,
        )
    msg = models.CharField(max_length=128, null=False, blank=True)
    sender = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='sent_notices',
        null=False,
        blank=False,
        )
    url = models.CharField(
        max_length=128, null=False, blank=True
        )
    is_read = models.BooleanField(
        null=False,
        blank=False,
        default=False
        )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ('-date',)

