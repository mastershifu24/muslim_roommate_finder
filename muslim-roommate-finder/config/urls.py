from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard & Listings
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-listings/', views.my_listings, name='my_listings'),

    # Profiles
    path('create/', views.create_profile, name='create_profile'),
    path('profile/<int:profile_id>/', views.profile_detail, name='profile_detail'),
    path('profile/<int:profile_id>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:profile_id>/delete/', views.delete_profile, name='delete_profile'),
    path('profile/<int:profile_id>/contact/', views.contact_profile, name='contact_profile'),

    # Rooms
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path("rooms/<int:pk>/delete/", views.room_delete, name="room_delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
