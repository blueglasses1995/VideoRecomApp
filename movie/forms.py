from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from tempus_dominus.widgets import DatePicker
from . import models
import re, base64
import os


class MovieCreationForm(forms.ModelForm):
    description = forms.CharField(label='简介', widget=CKEditorUploadingWidget())

    class Meta:
        model = models.Movie
        fields = ('title', 'year', 'director', 'key_actors', 'production_countries', 'rating', 'genres', 'tags', 'cover', 'description', 'link_to_watch')
        widgets = {
            'year': DatePicker(
                options={
                    'format': 'YYYY',
                },
                attrs={
                    'append': 'fas fa-calendar',
                    'icon_toggle': True,
                    'size': '300',
                },
            )
        }

    def fill_all_choices(self):
        tags = []
        for tag in models.Tag.objects.all():
            tags.append((tag.id, tag.name))
        self.tags.choices = tags

        genres = []
        for genre in models.Genre.objects.all():
            genres.append((genre.id, genre.name))
        self.genres.choices = genres


class ShortCommentForm(forms.Form):
    comment = forms.CharField(max_length=1000)


class ReviewCreateForm(forms.ModelForm):
    # content = forms.CharField(label='简介', widget=CKEditorUploadingWidget())

    class Meta:
        model = models.Review
        fields = ('title', 'content', 'tags')
        widgets = {
            'content': CKEditorUploadingWidget()
        }


class UserEditForm(forms.ModelForm):
    avatar = forms.ImageField(label='Avatar', required=False)
    avatar_thumbnail = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.User
        fields = ('username', 'email', 'avatar', 'first_name', 'last_name', 'birth', 'avatar_thumbnail')
        widgets = {
            'birth': DatePicker(
                options={
                    'format': 'YYYY-MM-DD',
                         },
                attrs={'append': 'fas fa-calendar', 'icon_toggle': True, 'size': '300', },
                ),
            }
        readonly_fields = ('username', 'email')
        exclude = ('password1', 'password2')

    def save_avatar_thumbnail(self, path):
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        image_data = self.cleaned_data['avatar_thumbnail']
        image_data = dataUrlPattern.match(image_data).group(2)
        image_data = image_data.encode()
        image_data = base64.b64decode(image_data)

        fd = os.path.dirname(path)
        if not os.path.exists(fd):
            os.makedirs(fd, exist_ok=True)

        with open(path, 'wb') as f:
            f.write(image_data)