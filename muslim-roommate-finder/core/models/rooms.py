from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from .profiles import Profile

# Room-related models
class RoomType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="rooms")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    halal_kitchen = models.BooleanField(default=False)
    prayer_friendly = models.BooleanField(default=False)
    guests_allowed = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    contact_email = models.EmailField(blank=True)

    # methods (save, __str__) stay here

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="room_images/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.room.title}"

class RoomAmenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class RoomVerification(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

class RoomFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "room")
