from django.forms import Form, CharField, URLField, ModelForm
from django.contrib.auth.models import User

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']