from django.contrib import admin
from core.models import (
    Profile, RoommateProfile, Contact, Message, Room, RoomType, 
    Amenity, RoomImage, RoomReview, RoomFavorite, RoomVerification
)

# Import admin classes
from .profile_admin import ProfileAdmin
from .room_admin import RoomAdmin, RoomTypeAdmin, AmenityAdmin, RoomImageAdmin
from .messaging_admin import MessageAdmin
from .reviews_admin import RoomReviewAdmin

# Register additional models that don't have custom admin classes
@admin.register(RoommateProfile)
class RoommateProfileAdmin(admin.ModelAdmin):
    list_display = ("profile", "budget", "occupation")
    search_fields = ("profile__name", "occupation")
    list_filter = ("budget",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "profile", "created_at")
    search_fields = ("name", "email", "profile__name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

@admin.register(RoomFavorite)
class RoomFavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "created_at")
    search_fields = ("user__username", "room__title")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

@admin.register(RoomVerification)
class RoomVerificationAdmin(admin.ModelAdmin):
    list_display = ("room", "is_verified")
    list_filter = ("is_verified",)
    list_editable = ("is_verified",)
