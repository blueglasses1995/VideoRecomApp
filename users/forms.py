from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import PasswordResetForm as __PasswordResetForm
from tempus_dominus.widgets import DatePicker
from . import models
import re
import base64
import re
import os


def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)


class MyUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(label='Avatar')
    avatar_thumbnail = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = models.User
        fields = ('username', 'email', 'avatar', 'first_name', 'last_name', 'birth')
        widgets = {
            'birth': DatePicker(
                options={
                    'format': 'YYYY-MM-DD',

                },
                attrs={
                    'append': 'fas fa-calendar',
                    'icon_toggle': True,
                    'size': '300',
                },


            ),
        }

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


class LoginForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    # Use clean methods to define custom validation rules

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if email_check(username):
            filter_result = models.User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("This email does not exist.")
        else:
            filter_result = models.User.objects.filter(username__exact=username)
            if not filter_result:
                raise forms.ValidationError("This username does not exist. Please register first.")

        return username





