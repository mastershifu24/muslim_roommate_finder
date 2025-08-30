from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    city = models.CharField(max_length=100)
    #Starting with Charleston for now
    neighborhood = models.CharField(max_length=100, blank=True, help_text="Downtown, West Ashley, Mount Pleasant")
    is_looking_for_room = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    # Lifestyle
    halal_kitchen = models.BooleanField(default=True)
    prayer_friendly = models.BooleanField(default=True)
    guests_allowed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['city', 'neighborhood']),
            models.Index(fields=['age']),
            models.Index(fields=['gender']),
            models.Index(fields=['city', 'gender']),
            models.Index(fields=['city', 'is_looking_for_room']),
            models.Index(fields=['city', 'halal_kitchen']),
            models.Index(fields=['city', 'prayer_friendly']),
            models.Index(fields=['city', 'guests_allowed']),
            models.Index(fields=['is_looking_for_room']),
            models.Index(fields=['city', 'created_at']),
        ]

    def get_absolute_url(self):
        return reverse("profile_detail", args=[self.id])
    
    def get_location_display(self):
        if self.neighborhood and self.city:
            return f"{self.neighborhood}, {self.city}"
        elif self.city:
            return self.city
        return "Unknown"
    
    def get_age_range(self):
        return (self.age - 2, self.age + 2)
    
    def is_charleston_area(self):
        charleston_areas = ['Downtown', 'West Ashley', 'Mount Pleasant', 'James Island', 'Charleston County']
        return self.city.lower() in charleston_areas
    
    def get_halal_kitchen_display(self):
        return "Halal Kitchen" if self.halal_kitchen else "Not Halal Kitchen"
    
    def save(self, *args, **kwargs):
        if not self.slug and self.name and self.city:
            self.slug = slugify(f"{self.name}-{self.city}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    """Room listing posted by a user (optionally linked to a Profile)."""

    owner = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rooms'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)

    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True, help_text="Downtown, West Ashley, Mount Pleasant")

    rent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)

    # Lifestyle preferences for the household/room
    halal_kitchen = models.BooleanField(default=True)
    prayer_friendly = models.BooleanField(default=True)
    guests_allowed = models.BooleanField(default=False)

    contact_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)

    # Additional room features
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    private_bathroom = models.BooleanField(default=False)
    furnished = models.BooleanField(default=False)
    utilities_included = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['city', 'neighborhood']),
            models.Index(fields=['city', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        # Default contact_email to owner's if not provided
        if not self.contact_email and self.owner:
            self.contact_email = self.owner.contact_email
        if not self.slug and self.title and self.city:
            self.slug = slugify(f"{self.title}-{self.city}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("room_detail", args=[self.id])

    def __str__(self):
        return self.title


class Contact(models.Model):
    """
    Contact model to store messages between users.
    
    This model tracks who contacted whom and when, allowing users to
    communicate through the platform while maintaining privacy.
    """
    
    # The profile being contacted (the person receiving the message)
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,  # If profile is deleted, delete all contacts
        related_name='contacts_received',  # Allows: profile.contacts_received.all()
        verbose_name='Profile being contacted'
    )
    
    # Contact information of the person sending the message
    sender_name = models.CharField(
        max_length=100,
        verbose_name='Your name'
    )
    sender_email = models.EmailField(
        verbose_name='Your email'
    )
    
    # The actual message content
    message = models.TextField(
        verbose_name='Your message'
    )
    
    # When the contact was made
    created_at = models.DateTimeField(
        auto_now_add=True,  # Automatically set when contact is created
        verbose_name='Contact date'
    )
    
    # Whether the contact has been read by the profile owner
    is_read = models.BooleanField(
        default=False,
        verbose_name='Has been read'
    )
    
    class Meta:
        # Order contacts by most recent first
        ordering = ['-created_at']
        # Human-readable name in admin
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def __str__(self):
        """String representation of the contact."""
        return f"Contact from {self.sender_name} to {self.profile.name}"
    
    def get_short_message(self):
        """Returns a shortened version of the message for display."""
        if len(self.message) <= 50:
            return self.message
        return self.message[:50] + "..."


def room_image_path(instance, filename):
    return f'room_images/{instance.room_id}/{filename}'


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=room_image_path)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f"Image for {self.room.title}"
    

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"
    

class RoomReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['room', 'reviewer']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.room.title}"
    

class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability')
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.room.title} - {self.start_date} to {self.end_date}"
    

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
    

class RoomAmenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    included = models.BooleanField(default=True)

    class Meta:
        unique_together = ['room', 'amenity']

    def __str__(self):
        return f"{self.room.title} - {self.amenity.name}"


class RoomVerification(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Verification for {self.room.title} - {self.status}"


class RoomFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'room']

    def __str__(self):
        return f"{self.user.username} likes {self.room.title}"