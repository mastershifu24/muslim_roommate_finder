from django.contrib import admin
from .models import RoomImage

@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ("room", "image")
