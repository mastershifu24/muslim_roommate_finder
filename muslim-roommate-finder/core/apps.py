from django.apps import AppConfig
from django.db.models.signals import post_migrate

def seed_data(sender, **kwargs):
    from core.models import RoomType, Amenity

    roomtypes = ["Entire place", "Private room", "Shared room"]
    amenities = ["Wifi", "Parking", "Furnished", "Laundry", "Utilities included"]

    for name in roomtypes:
        RoomType.objects.get_or_create(name=name)

    for name in amenities:
        Amenity.objects.get_or_create(name=name)

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        post_migrate.connect(seed_data, sender=self)
