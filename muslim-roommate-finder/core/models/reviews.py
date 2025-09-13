from django.db import models
from .profiles import Profile
from .rooms import Room

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
