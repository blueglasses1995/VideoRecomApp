"""VideoRecomApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.index),
    path('register/', include('register.urls')),
    path('movie/', include('movie.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view),
    path('accounts/login/', LoginView.as_view(template_name='login_view.html'), name='accounts/login/'),
    path('profile/<int:pk>', views.profile, name='profilepage'),
    path('post/', include('post.urls')),
#    path('review/<int:content_id>', views.review),
    path('recommendation/', views.recommendation),
    path('recommendation/<tag_name>', views.tag_recommendation),
    path('admin/', admin.site.urls)
]
