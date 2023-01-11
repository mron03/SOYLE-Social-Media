from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

# Create your models here.
User = get_user_model()

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    firstname = models.CharField(max_length=100, default='Fistname')
    lastname = models.CharField(max_length=100, default='Lastname')
    email = models.EmailField(max_length=100, default='blank')
    bio = models.TextField(blank=True)
    working_at = models.CharField(max_length=100, default='No Information')
    relationship = models.CharField(max_length=50, default='None')
    profileimg = models.ImageField(upload_to='profile_images', default='blank_profile_picture.png')
    location = models.CharField(max_length=100, blank=True)
    room_id = models.CharField(max_length=100, default='None')
    recent_message = models.CharField(max_length=1000, default='')
    recent_message_time = models.DateTimeField(default=datetime.now)

    def __str__(self) -> str:
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now, )
    no_of_likes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.user

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, default='none')
    created_at = models.DateTimeField(default=datetime.now)
    value = models.TextField(max_length=1000)

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.user

class Room(models.Model):
    u1 = models.IntegerField(default=0)
    u2 = models.IntegerField(default=0)


class Message(models.Model):
    user = models.CharField(max_length=1000)
    value = models.CharField(max_length=10000)
    date = models.DateField(default=datetime.now, blank=True)
    date_time = models.DateTimeField(default=datetime.now, blank=True)
    room = models.CharField(max_length=1000)
