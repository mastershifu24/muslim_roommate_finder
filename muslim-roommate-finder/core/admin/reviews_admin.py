from django.contrib import admin
from core.models.reviews import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "rating", "created_at")
    search_fields = ("room__title", "user__username", "comment")
    list_filter = ("rating", "created_at")
