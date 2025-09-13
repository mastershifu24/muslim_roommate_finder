from django.db import models
from .profiles import Profile

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
