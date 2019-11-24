from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserForm

# Create your views here.
def index(request):
    return render(request, 'register/register.html')

def create_user(request):
    user = User.objects.create_user(
        request.POST.get('username'),
        request.POST.get('email'),
        request.POST.get('password'),
        #メール認証完了まで、アカウントは作成されたが有効でないステータス
        #is_active=False
    )
    user.save()
    return redirect('accounts/login/')

def create_user_view(request):
    form = UserForm()
    return render(request, 'register/create_user_view.html', {'form': form})

'''
def check(request):
    if request.POST['username'] and request.POST['email']:
        return render(request, 'registercheck.html', {'username': request.POST['username'], 'email': request.POST['email']})
    else:
        return  render(request, 'registererror.html')
'''