from django.contrib import admin
from core.models import RoomImage

@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ("room", "is_primary")
    list_filter = ("is_primary",)
    list_editable = ("is_primary",)
    search_fields = ("room__title",)
