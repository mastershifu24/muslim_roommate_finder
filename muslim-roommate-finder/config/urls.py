"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin #this import is used to access the admin site
from django.urls import path #this import is used to define the url patterns for the app
from core.views import (
    home, create_profile, profile_detail, edit_profile, delete_profile, 
    contact_profile, room_detail, create_room, register, user_login, 
    user_logout, my_listings, dashboard
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('my-listings/', my_listings, name='my_listings'),
    path('create/', create_profile, name='create_profile'),
    path('profile/<int:profile_id>/', profile_detail, name='profile_detail'),
    path('profile/<int:profile_id>/edit/', edit_profile, name='edit_profile'),
    path('profile/<int:profile_id>/delete/', delete_profile, name='delete_profile'),
    path('profile/<int:profile_id>/contact/', contact_profile, name='contact_profile'),
    path('rooms/<int:room_id>/', room_detail, name='room_detail'),
    path('rooms/create/', create_room, name='create_room'),
]
