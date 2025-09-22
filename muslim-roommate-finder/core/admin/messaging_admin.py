from django.contrib import admin
from core.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "timestamp")
    search_fields = ("sender__name", "recipient__name", "content")
    list_filter = ("timestamp",)
    readonly_fields = ("timestamp",)
