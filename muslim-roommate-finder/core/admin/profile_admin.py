from django.contrib import admin
from core.models.profiles import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "location", "created_at")
    search_fields = ("user__username", "bio", "location")
    list_filter = ("created_at",)
