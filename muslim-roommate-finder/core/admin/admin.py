from django.contrib import admin
from django.contrib.auth import get_user_model
from core.models import (
    Profile, Message, Room, RoomType, Amenity, RoomImage, RoomReview
)

User = get_user_model()

# -------------------------
# User Admin
# -------------------------
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")

# -------------------------
# Profile Admin
# -------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "city", "state", "age", "gender")
    search_fields = ("name", "user__username", "city", "neighborhood", "bio")
    list_filter = ("gender", "city", "state", "is_looking_for_room", "halal_kitchen", "prayer_friendly")
    list_editable = ("city", "state", "age")
    readonly_fields = ("slug",)
    fieldsets = (
        ("Basic Info", {"fields": ("user", "name", "age", "gender")}),
        ("Location", {"fields": ("city", "state", "neighborhood", "zip_code")}),
        ("Preferences", {"fields": ("is_looking_for_room", "halal_kitchen", "prayer_friendly", "guests_allowed")}),
        ("Contact & Bio", {"fields": ("contact_email", "bio", "slug")}),
    )

# -------------------------
# Message Admin
# -------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "timestamp")
    search_fields = ("sender__name", "recipient__name", "content")
    list_filter = ("timestamp",)
    readonly_fields = ("timestamp",)

# -------------------------
# Room Review Admin
# -------------------------
@admin.register(RoomReview)
class RoomReviewAdmin(admin.ModelAdmin):
    list_display = ("room", "reviewer", "rating", "created_at")
    search_fields = ("room__title", "reviewer__name", "comment")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)

# -------------------------
# Room & RoomImage Admin
# -------------------------
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ('image', 'is_primary', 'caption')
    readonly_fields = ('get_file_size',)
    
    def get_file_size(self, obj):
        if obj.pk:
            return obj.get_file_size()
        return "N/A"
    get_file_size.short_description = "File Size"

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "city", "neighborhood", "price", "available_from", "is_active", "image_count")
    search_fields = ("title", "description", "city", "neighborhood", "user__name")
    list_filter = ("city", "room_type", "halal_kitchen", "prayer_friendly", "guests_allowed", "is_active", "created_at")
    list_editable = ("price", "available_from", "is_active")
    readonly_fields = ("slug", "created_at", "updated_at", "image_count")
    filter_horizontal = ("amenities",)
    inlines = [RoomImageInline]
    fieldsets = (
        ("Basic Info", {"fields": ("user", "title", "description", "room_type")}),
        ("Location", {"fields": ("city", "neighborhood")}),
        ("Details", {"fields": ("price", "available_from", "amenities", "is_active")}),
        ("Preferences", {"fields": ("halal_kitchen", "prayer_friendly", "guests_allowed")}),
        ("Contact", {"fields": ("contact_email", "slug")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    def get_price_display(self, obj):
        return obj.get_price_display()
    get_price_display.short_description = "Price"
    
    def image_count(self, obj):
        return obj.image_count
    image_count.short_description = "Images"

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ("room", "is_primary", "get_file_size", "created_at")
    list_filter = ("is_primary", "created_at")
    list_editable = ("is_primary",)
    search_fields = ("room__title", "caption")
    readonly_fields = ("created_at", "get_file_size")
    
    def get_file_size(self, obj):
        return obj.get_file_size()
    get_file_size.short_description = "File Size"
