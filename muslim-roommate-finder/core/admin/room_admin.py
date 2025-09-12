from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "price", "created_at")
    search_fields = ("title", "location")
    list_filter = ("created_at",)
