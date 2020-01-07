from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import (auth, messages)
from django.http import (HttpResponse, HttpResponseRedirect, HttpResponseNotFound,
                         HttpResponseNotAllowed, JsonResponse, HttpResponseServerError)
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import LoginForm, MyUserCreationForm
import uuid
from . import models
import os
from recommend import settings
# Create your views here.


@login_required
def index(request):
    return redirect(reverse('movie:index'))


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                if user.is_superuser:
                    return redirect('/admin')
                return HttpResponseRedirect(reverse('users:index'))
            else:
                messages.warning(request, 'Wrong username or password. Please try again.')
                return render(
                    request, 'users/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data['avatar_thumbnail']:
                i = str(uuid.uuid4())
                p = models.user_thumbnail_path(user, '{}.png'.format(i))
                fp = os.path.abspath(os.path.join(settings.MEDIA_ROOT, p))

                form.save_avatar_thumbnail(fp)
                user.thumbnail = p
                user.save()
            messages.success(request, 'Your account created, Please login with your new account')
            return redirect('users:login')
    else:
        form = MyUserCreationForm()

    return render(request, 'users/registration.html', {'form': form})


@login_required
def logout(request):
    print('logout')
    auth.logout(request)
    return HttpResponseRedirect(reverse('users:login'))


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password updated')
            return redirect('users:password_change')
        else:
            messages.error(request, 'Failed to change your password')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/password_change.html', {'form': form, 'title': 'Password Change'})
