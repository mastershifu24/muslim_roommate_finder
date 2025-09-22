from django.contrib import admin
from core.models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "city", "state", "age", "gender")
    search_fields = ("name", "user__username", "city", "neighborhood", "bio")
    list_filter = ("gender", "city", "state", "is_looking_for_room", "halal_kitchen", "prayer_friendly")
    list_editable = ("city", "state", "age")
    readonly_fields = ("slug",)
    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "name", "age", "gender")
        }),
        ("Location", {
            "fields": ("city", "state", "neighborhood", "zip_code")
        }),
        ("Preferences", {
            "fields": ("is_looking_for_room", "halal_kitchen", "prayer_friendly", "guests_allowed")
        }),
        ("Contact & Bio", {
            "fields": ("contact_email", "bio", "slug")
        }),
    )
