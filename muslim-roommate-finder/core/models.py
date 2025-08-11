from django.db import models

class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    city = models.CharField(max_length=100)
    is_looking_for_room = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField()

    # Lifestyle
    halal_kitchen = models.BooleanField(default=True)
    prayer_friendly = models.BooleanField(default=True)
    guests_allowed = models.BooleanField(default=False)

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
