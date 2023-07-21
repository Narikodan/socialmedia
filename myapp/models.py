from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_number = models.CharField(max_length=10)
    password = models.CharField(max_length=20)

class ProfilePicture(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile_picture')
    image = models.ImageField(upload_to='profile_pictures')

class Post(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images', blank=True)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(get_user_model(), through='Like', related_name='liked_posts')

    def __str__(self):
        return f"Post by {self.user.username}"

    def get_like_count(self):
        return self.likes.count()

    def get_like_notification(self):
        likers = self.likes.through.objects.filter(post=self).values_list('user__first_name', 'user__last_name')[:3]
        liker_count = self.likes.count() - len(likers)
        likers_full_names = [f"{first_name} {last_name}" for first_name, last_name in likers]
        if likers_full_names:
            if liker_count > 0:
                return f"{', '.join(likers_full_names)} and {liker_count} others liked your post"
            else:
                return f"{', '.join(likers_full_names)} liked your post"
        return ""
    
    def get_comment_count(self):
        return self.comments.count()

class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

    def get_comment_preview(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text

    @classmethod
    def get_comment_count_for_post(cls, post_id):
        return cls.objects.filter(post_id=post_id).count()
    

from chatapp.models import Room

class ChatParticipant(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='chats')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"
