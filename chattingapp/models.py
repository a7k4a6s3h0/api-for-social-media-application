import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from .manager import UserManager
from .file_validators import validate_video_size, validate_image_size
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
# Create your models here.


class User(AbstractUser):
    profile_photo = models.ImageField(upload_to='images/', default=None)
    email = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=30,unique=True)
    mobile_no = models.BigIntegerField(unique=True, default=None)
    is_verified = models.BooleanField(default=False)
    about = models.CharField(null=True, blank=True, max_length=50) 
    registered_userid = models.CharField(max_length=50, default='No')
    gender = models.CharField(null=True, blank=True, max_length=30, default='Others')
    is_online = models.BooleanField(default=False)


    objects = UserManager()

    def __str__(self):
        return self.username

class OTP_Checking(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    OTP = models.IntegerField(null=False)
    created_time = models.DateTimeField(auto_now_add = True)
    otp_generating_count = models.IntegerField(default=3)



class Conversation(models.Model):
    initiator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="convo_starter"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="convo_participant"
    )
    room_name = models.CharField(max_length=100, default=None)
    room_type = models.CharField(max_length=20, default='Normal')
    chat_room = models.CharField(max_length=100, null=True, blank=True)
    group_members = ArrayField(models.IntegerField(), size=0, null=True)
    start_time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='message_sender')
    text = models.CharField(max_length=200, blank=True)
    attachment =  models.CharField(default=None, max_length=200, null=True, blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE,)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ('-timestamp',)    


class CallHistory(models.Model):
    caller_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caller_history')
    reciever_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_history')
    started_time = models.DateTimeField(auto_now_add=True)
    ended_time = models.DateTimeField(default=None, null=True, blank=True) 
    is_accept = models.BooleanField(default=False)
        

class Notifications(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=200, blank=True, null=True)
    is_calling = models.BooleanField(default=False)
    calling_details =  models.ForeignKey(CallHistory, on_delete=models.SET_NULL, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)        



class user_status(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    videos = models.FileField(upload_to='status/', max_length=100, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov']), validate_video_size])
    pictures = models.FileField(upload_to='status_pictures/', max_length=100, null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), validate_image_size])
    text = models.CharField(max_length=500, blank=True, null=True)    