from django.contrib import admin
from core.models import Room, RoomType, Amenity, RoomImage

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
        ("Basic Info", {
            "fields": ("user", "title", "description", "room_type")
        }),
        ("Location", {
            "fields": ("city", "neighborhood")
        }),
        ("Details", {
            "fields": ("price", "available_from", "amenities", "is_active")
        }),
        ("Preferences", {
            "fields": ("halal_kitchen", "prayer_friendly", "guests_allowed")
        }),
        ("Contact", {
            "fields": ("contact_email", "slug")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
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
