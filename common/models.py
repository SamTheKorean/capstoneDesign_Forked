from django.db import models
from django.contrib.auth.models import User as authUser

class Video(models.Model):
    user = models.ForeignKey(authUser, on_delete=models.CASCADE, null=True)
    text = models.TextField(null=True)
    thumbnail = models.TextField(null=True)
    video_key = models.TextField(null=True)

class Memo(models.Model):
    text = models.CharField(max_length=600, null=True)  # 메모 내용
    user = models.ForeignKey(authUser, on_delete=models.CASCADE, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    current_time = models.FloatField(null=True, blank=True)  # Add this line for current_time


    