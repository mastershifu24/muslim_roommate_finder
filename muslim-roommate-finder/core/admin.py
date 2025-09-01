from django.contrib import admin
from .models import (
    Profile, Contact, Room, RoomType, RoomImage, Message, 
    RoomReview, RoomAvailability, Amenity, RoomAmenity, 
    RoomVerification, RoomFavorite
)

@admin.register(Profile)  # This decorator registers the Profile model with admin
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    This class tells Django how to display and manage Profile objects in the admin interface.
    """
    
    # Fields to display in the list view (table of all profiles)
    # IMPORTANT: Any field in list_editable must also be in list_display
    list_display = [
        'name',           # Show name column
        'age',            # Show age column  
        'gender',         # Show gender column
        'city',           # Show city column
        'is_looking_for_room',  # Show if looking for room
        'halal_kitchen',  # Show halal kitchen preference
        'prayer_friendly', # Show prayer friendly preference
        'guests_allowed', # Show guests allowed preference (ADDED THIS)
        'contact_email',  # Show contact email
        'user',           # Show associated user
    ]
    
    # Fields that can be used to search/filter profiles
    list_filter = [
        'gender',         # Filter by gender (Male/Female dropdown)
        'city',           # Filter by city (dropdown of all cities)
        'is_looking_for_room',  # Filter by looking for room (Yes/No)
        'halal_kitchen',  # Filter by halal kitchen preference
        'prayer_friendly', # Filter by prayer friendly preference
        'guests_allowed', # Filter by guests allowed preference
    ]
    
    # Fields that can be searched (searches in name, city, bio, email)
    search_fields = [
        'name',           # Search by name
        'city',           # Search by city
        'bio',            # Search in bio text
        'contact_email',  # Search by email
        'user__username', # Search by username
    ]
    
    # Fields to display when editing a profile (organized in sections)
    fieldsets = (
        # Personal Information section
        ('Personal Information', {
            'fields': ('user', 'name', 'age', 'gender', 'city', 'contact_email')
        }),
        # Bio section
        ('About', {
            'fields': ('bio',),
            'classes': ('wide',)  # Makes the bio field wider
        }),
        # Preferences section
        ('Preferences', {
            'fields': ('is_looking_for_room', 'halal_kitchen', 'prayer_friendly', 'guests_allowed'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )
    
    # Number of profiles to show per page in the admin list
    list_per_page = 25
    
    # Fields that can be edited directly in the list view (without opening edit page)
    # RULE: All fields in list_editable must also be in list_display
    list_editable = [
        'is_looking_for_room',  # Can check/uncheck directly in list
        'halal_kitchen',        # Can check/uncheck directly in list
        'prayer_friendly',      # Can check/uncheck directly in list
        'guests_allowed',       # Can check/uncheck directly in list
    ]
    
    # Order profiles by name (alphabetical)
    ordering = ('name',)
    
    # Show a "View on site" link in admin (links to your profile detail page)
    def view_on_site(self, obj):
        """Returns the URL to view this profile on the public site."""
        from django.urls import reverse
        return reverse('profile_detail', args=[obj.id])
    
    # Customize the admin list view title
    def get_queryset(self, request):
        """Customize the queryset for the admin list view."""
        return super().get_queryset(request).select_related()
    
    # Add custom actions (bulk operations)
    actions = ['mark_as_looking_for_room', 'mark_as_not_looking_for_room']
    
    def mark_as_looking_for_room(self, request, queryset):
        """Custom admin action: Mark selected profiles as looking for room."""
        updated = queryset.update(is_looking_for_room=True)
        self.message_user(request, f'{updated} profiles marked as looking for room.')
    mark_as_looking_for_room.short_description = "Mark selected profiles as looking for room"
    
    def mark_as_not_looking_for_room(self, request, queryset):
        """Custom admin action: Mark selected profiles as not looking for room."""
        updated = queryset.update(is_looking_for_room=False)
        self.message_user(request, f'{updated} profiles marked as not looking for room.')
    mark_as_not_looking_for_room.short_description = "Mark selected profiles as not looking for room"

@admin.register(Contact)  # Register the Contact model with admin
class ContactAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Contact model.
    This class tells Django how to display and manage Contact objects in the admin interface.
    """
    
    # Fields to display in the list view (table of all contacts)
    list_display = [
        'sender_name',        # Show sender name
        'sender_email',       # Show sender email
        'profile',            # Show which profile was contacted
        'get_short_message',  # Show shortened message
        'created_at',         # Show when contact was made
        'is_read',            # Show read status
    ]
    
    # Fields that can be used to search/filter contacts
    list_filter = [
        'is_read',            # Filter by read status (Read/Unread)
        'created_at',         # Filter by date
        'profile__city',      # Filter by profile city
        'profile__gender',    # Filter by profile gender
    ]
    
    # Fields that can be searched
    search_fields = [
        'sender_name',        # Search by sender name
        'sender_email',       # Search by sender email
        'message',            # Search in message content
        'profile__name',      # Search by profile name
    ]
    
    # Fields to display when editing a contact
    fieldsets = (
        # Contact Information section
        ('Contact Information', {
            'fields': ('sender_name', 'sender_email')
        }),
        # Message section
        ('Message', {
            'fields': ('message',),
            'classes': ('wide',)  # Makes the message field wider
        }),
        # Profile and Status section
        ('Profile & Status', {
            'fields': ('profile', 'is_read', 'created_at'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )
    
    # Number of contacts to show per page
    list_per_page = 25
    
    # Fields that can be edited directly in the list view
    list_editable = [
        'is_read',  # Can check/uncheck read status directly in list
    ]
    
    # Order contacts by most recent first
    ordering = ('-created_at',)
    
    # Make created_at read-only (shouldn't be editable)
    readonly_fields = ['created_at']
    
    # Add custom actions
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Custom admin action: Mark selected contacts as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} contacts marked as read.')
    mark_as_read.short_description = "Mark selected contacts as read"
    
    def mark_as_unread(self, request, queryset):
        """Custom admin action: Mark selected contacts as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} contacts marked as unread.')
    mark_as_unread.short_description = "Mark selected contacts as unread"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'city',
        'neighborhood',
        'rent',
        'available_from',
        'halal_kitchen',
        'prayer_friendly',
        'guests_allowed',
        'owner',
        'created_at',
    ]
    list_filter = [
        'city',
        'neighborhood',
        'halal_kitchen',
        'prayer_friendly',
        'guests_allowed',
        'available_from',
        'room_type',
    ]
    search_fields = [
        'title',
        'description',
        'city',
        'neighborhood',
        'owner__name',
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ('-created_at',)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'caption', 'is_primary', 'image']
    list_filter = ['is_primary', 'room__city']
    search_fields = ['room__title', 'caption']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'room', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at', 'room__city']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'content']
    readonly_fields = ['created_at']
    ordering = ('-created_at',)


@admin.register(RoomReview)
class RoomReviewAdmin(admin.ModelAdmin):
    list_display = ['room', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'room__city']
    search_fields = ['room__title', 'reviewer__username', 'review_text']
    readonly_fields = ['created_at']
    ordering = ('-created_at',)


@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['room', 'start_date', 'end_date', 'is_available']
    list_filter = ['is_available', 'start_date', 'end_date', 'room__city']
    search_fields = ['room__title', 'notes']
    ordering = ('start_date',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ['room', 'amenity', 'included']
    list_filter = ['included', 'amenity']
    search_fields = ['room__title', 'amenity__name']


@admin.register(RoomVerification)
class RoomVerificationAdmin(admin.ModelAdmin):
    list_display = ['room', 'status', 'verified_by', 'verified_at']
    list_filter = ['status', 'verified_at']
    search_fields = ['room__title', 'verification_notes']
    readonly_fields = ['verified_at']


@admin.register(RoomFavorite)
class RoomFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'created_at']
    list_filter = ['created_at', 'room__city']
    search_fields = ['user__username', 'room__title']
    readonly_fields = ['created_at']
    ordering = ('-created_at',)
