from django.contrib import admin
from core.models import RoomReview

@admin.register(RoomReview)
class RoomReviewAdmin(admin.ModelAdmin):
    list_display = ("room", "reviewer", "rating", "created_at")
    search_fields = ("room__title", "reviewer__name", "comment")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)
