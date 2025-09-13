from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse

# Profile + RoommateProfile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[("male", "Male"), ("female", "Female")])
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True)
    is_looking_for_room = models.BooleanField(default=False)
    halal_kitchen = models.BooleanField(default=False)
    prayer_friendly = models.BooleanField(default=False)
    guests_allowed = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    # methods (e.g., save, get_age_range, __str__) stay here
    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"profile_id": self.id})

class RoommateProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="roommate_profile")
    budget = models.PositiveIntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"RoommateProfile of {self.profile.name}"

# signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
