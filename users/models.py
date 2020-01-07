from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.


def user_avatar_path(user, filename: str):
    return 'avatar/user_{0}/{1}'.format(user.username, filename)


def user_thumbnail_path(user, filename: str):
    return 'avatar/thumbnail/{0}_{1}'.format(user.pk, filename)


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(
        verbose_name='Avatar',
        # width_field=100,
        # height_field=100,
        upload_to=user_avatar_path,
        null=True,
        blank=True
    )
    birth = models.DateField(
        verbose_name='Birthday',
        null=True,
        blank=True,
    )
    thumbnail = models.ImageField(
        verbose_name='thumbnail',
        # width_field=100,
        # height_field=100,
        upload_to=user_thumbnail_path,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = verbose_name
        ordering = ('-id', )

    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        if not self.thumbnail:
            return '/static/image/default_avatar.png'
        else:
            return self.thumbnail.url


