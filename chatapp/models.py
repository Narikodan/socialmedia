# chatapp/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.text import slugify

class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate the slug automatically based on the room name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return "Room: " + self.name + " | Id: " + self.slug

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Message: " + self.content

class ChatParticipant(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chat_participants')

    def __str__(self):
        return f"Participant: {self.user.username} in Room: {self.room.name}"
