from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO

# --- Define U.S. states as a dictionary (outside the class) ---
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

# --- Profiles ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User Account")
    name = models.CharField(max_length=100, verbose_name="Full Name")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    gender = models.CharField(max_length=20, choices=[("male", "Male"), ("female", "Female")], verbose_name="Gender")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City", db_index=True)
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name="State", db_index=True)
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name="Neighborhood")
    is_looking_for_room = models.BooleanField(default=False, verbose_name="Looking for Room")
    halal_kitchen = models.BooleanField(default=False, verbose_name="Prefers Halal Kitchen")
    prayer_friendly = models.BooleanField(default=False, verbose_name="Prefers Prayer-Friendly Environment")
    guests_allowed = models.BooleanField(default=True, verbose_name="Allows Guests")
    bio = models.TextField(blank=True, verbose_name="Biography")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL Slug")
    zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="ZIP Code", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True, blank=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['is_looking_for_room']),
            models.Index(fields=['gender']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"profile_id": self.id})

    def is_charleston_area(self):
        if not self.city or not self.state:
            return False
        return (
            self.city.strip().lower() == "charleston"
            and self.state.strip().lower() in ["sc", "south carolina"]
        )

    def is_in_area(self, cities=None, state=None, zip_codes=None):
        if not (self.city or self.state or self.zip_code):
            return False

        city_match = True
        state_match = True
        zip_match = True

        if cities:
            city_match = self.city and self.city.strip().lower() in [c.lower() for c in cities]

        if state:
            state_input = state.upper()
            state_fullnames = {v.upper(): k for k, v in US_STATES.items()}

            if state_input in US_STATES:
                state_match = self.state and self.state.strip().upper() == state_input
            elif state_input in state_fullnames:
                state_match = self.state and self.state.strip().upper() == state_fullnames[state_input]
            else:
                state_match = False

        if zip_codes:
            zip_match = self.zip_code and self.zip_code.strip() in [str(z).strip() for z in zip_codes]

        return city_match and state_match and zip_match
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name or self.user.username)
            slug = base_slug
            counter = 1
            while Profile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class RoommateProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="roommate_profile", verbose_name="Profile")
    budget = models.PositiveIntegerField(null=True, blank=True, verbose_name="Monthly Budget")
    occupation = models.CharField(max_length=100, blank=True, verbose_name="Occupation")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)

    class Meta:
        verbose_name = "Roommate Profile"
        verbose_name_plural = "Roommate Profiles"

    def __str__(self):
        return f"Roommate Profile: {self.profile.name}"

# --- Messaging ---
class Contact(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="contacts", verbose_name="Profile")
    name = models.CharField(max_length=100, verbose_name="Contact Name")
    email = models.EmailField(verbose_name="Contact Email")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} to {self.profile.name}"

class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_messages", verbose_name="Sender")
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="received_messages", verbose_name="Recipient")
    content = models.TextField(verbose_name="Message Content")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Sent At")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.name} to {self.recipient.name}"

# --- Rooms ---
class RoomType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Room Type")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"
        ordering = ['name']

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100, verbose_name="Amenity Name")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon Class")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPES = [
        ("private", "Private Room"),
        ("shared", "Shared Room"),
        ("entire", "Entire Place"),
    ]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="rooms", verbose_name="Owner")
    title = models.CharField(max_length=200, verbose_name="Room Title")
    description = models.TextField(blank=True, verbose_name="Description")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    amenities = models.ManyToManyField(Amenity, blank=True, verbose_name="Amenities")
    city = models.CharField(max_length=100, verbose_name="City", db_index=True)
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name="Neighborhood")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monthly Rent")
    available_from = models.DateField(null=True, blank=True, verbose_name="Available From")
    halal_kitchen = models.BooleanField(default=False, verbose_name="Halal Kitchen")
    prayer_friendly = models.BooleanField(default=False, verbose_name="Prayer-Friendly")
    guests_allowed = models.BooleanField(default=True, verbose_name="Guests Allowed")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL Slug")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    is_active = models.BooleanField(default=True, verbose_name="Active Listing")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True, blank=True)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'neighborhood']),
            models.Index(fields=['price']),
            models.Index(fields=['available_from']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.city})"

    def get_absolute_url(self):
        return reverse("room_detail", kwargs={"room_id": self.id})
    
    @property
    def primary_image(self):
        """Get the primary image for this room"""
        try:
            return self.images.filter(is_primary=True).first() or self.images.first()
        except:
            return None
    
    @property
    def image_count(self):
        """Get the number of images for this room"""
        return self.images.count()
    
    def get_price_display(self):
        """Format price for display"""
        return f"${self.price:,.2f}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

def validate_image_size(image):
    """Validate image file size (max 5MB)"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Image file too large ( > 5MB )")

def validate_image_format(image):
    """Validate image format"""
    allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
    try:
        with Image.open(image) as img:
            if img.format not in allowed_formats:
                raise ValidationError(f"Unsupported image format. Allowed: {', '.join(allowed_formats)}")
    except Exception as e:
        raise ValidationError("Invalid image file")

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images", verbose_name="Room")
    image = models.ImageField(
        upload_to="room_images/", 
        verbose_name="Image",
        validators=[validate_image_size, validate_image_format],
        help_text="Upload an image (max 5MB, JPEG/PNG/WEBP)"
    )
    is_primary = models.BooleanField(default=False, verbose_name="Primary Image")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Caption")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)

    class Meta:
        verbose_name = "Room Image"
        verbose_name_plural = "Room Images"
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.room.title}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset all other primary images for this room
        if self.is_primary:
            RoomImage.objects.filter(room=self.room, is_primary=True).update(is_primary=False)
        
        # Auto-set as primary if it's the first image for this room
        if not self.pk and not RoomImage.objects.filter(room=self.room).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)
    
    def get_thumbnail_url(self, size=(300, 200)):
        """Generate a thumbnail URL for the image"""
        if not self.image:
            return None
        
        # For now, return the original image URL
        # In production, you might want to generate actual thumbnails
        return self.image.url
    
    def get_file_size(self):
        """Get the file size in a human-readable format"""
        if not self.image:
            return "No image"
        
        try:
            size = self.image.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown size"

class RoomAmenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, verbose_name="Amenity")

    class Meta:
        verbose_name = "Room Amenity"
        verbose_name_plural = "Room Amenities"
        unique_together = ("room", "amenity")

class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    class Meta:
        verbose_name = "Room Availability"
        verbose_name_plural = "Room Availabilities"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.room.title} available {self.start_date} to {self.end_date}"

class RoomVerification(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, verbose_name="Room")
    is_verified = models.BooleanField(default=False, verbose_name="Is Verified")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Verified At")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Verified By")

    class Meta:
        verbose_name = "Room Verification"
        verbose_name_plural = "Room Verifications"

    def __str__(self):
        return f"{self.room.title} - {'Verified' if self.is_verified else 'Not Verified'}"

class RoomFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Room")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Room Favorite"
        verbose_name_plural = "Room Favorites"
        unique_together = ("user", "room")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.room.title}"

# --- Reviews ---
class RoomReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reviews", verbose_name="Room")
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Reviewer")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Rating")
    comment = models.TextField(blank=True, verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True, blank=True)

    class Meta:
        verbose_name = "Room Review"
        verbose_name_plural = "Room Reviews"
        unique_together = ("room", "reviewer")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.name} review of {self.room.title}: {self.rating}/5"

# --- Signals ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
