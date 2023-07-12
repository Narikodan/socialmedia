from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_number = models.CharField(max_length=10)
    password = models.CharField(max_length=20)


class Post(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images', blank=True)
    text = models.TextField(blank=True)
    likes = models.ManyToManyField(get_user_model(), through='Like', related_name='liked_posts')

    def __str__(self):
        return f"Post by {self.user.username}"
    
class Like(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
