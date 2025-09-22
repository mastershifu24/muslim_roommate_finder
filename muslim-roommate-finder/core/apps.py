from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.text import slugify

def seed_data(sender, **kwargs):
    from core.models import RoomType, Amenity

    roomtypes = ["Entire place", "Private room", "Shared room"]
    amenities = ["Wifi", "Parking", "Furnished", "Laundry", "Utilities included"]

    # Seed RoomType
    for name in roomtypes:
        RoomType.objects.get_or_create(name=name)

    # Seed Amenity
    for name in amenities:
        Amenity.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name)}
    )

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        post_migrate.connect(seed_data, sender=self)
