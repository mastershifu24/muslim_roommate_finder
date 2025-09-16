from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[("male", "Male"), ("female", "Female")])
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    is_looking_for_room = models.BooleanField(default=False)
    halal_kitchen = models.BooleanField(default=False)
    prayer_friendly = models.BooleanField(default=False)
    guests_allowed = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

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

class RoommateProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="roommate_profile")
    budget = models.PositiveIntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"RoommateProfile of {self.profile.name}"

# --- Messaging ---
class Contact(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} to {self.profile.name}"

class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.name} to {self.recipient.name} at {self.timestamp}"

# --- Rooms ---
class RoomType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="rooms")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField(null=True, blank=True)
    halal_kitchen = models.BooleanField(default=False)
    prayer_friendly = models.BooleanField(default=False)
    guests_allowed = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    contact_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.city})"

    def get_absolute_url(self):
        return reverse("room_detail", kwargs={"room_id": self.id})

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

# --- Reviews ---
class RoomReview(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "reviewer")

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
