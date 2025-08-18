from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

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
            models.Index(fields=['i_looking_for_room']),
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
    
    def get_gender_display(self):
        return self.get_gender_display()
    
    def get_halal_kitchen_display(self):
        return "Halal Kitchen" if self.halal_kitchen else "Not Halal Kitchen"
    
    def save(self, *args, **kwargs):
        if not self.slug and self.name and self.city:
            self.slug = slugify(f"{self.name}-{self.city}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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
