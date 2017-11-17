from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.db.models import Count
from random import randint

def file_path(instance, filename):
    instance.file_path = 'podlife/uploads/'+instance.slugfield+'.wav'

class Topics(models.Model):
    topic = models.CharField(max_length=40, unique=True, blank=False)

class PodcastsManager(models.Manager):
    def random(self):
        count = self.aggregate(ids=Count('id'))['ids']
        if count > 0:
            random_index = randint(0, count - 1)
            return self.all()[random_index]
        else:
            return None

class Podcasts(models.Model):
    slugfield = models.SlugField(max_length=200, unique=True, editable=False)
    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(null=True)
    audio_file = models.FileField(upload_to=file_path, null=True)
    file_type = models.CharField(max_length=3, choices=(('WAV', '.wav'), ('MP3', '.mp3')), default='WAV')
    file_path = models.CharField(max_length=220, null=True, editable=False)
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    views = models.IntegerField(default = 0, editable=False)
    num_comments = models.IntegerField(default = 0, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=False)

    objects = PodcastsManager()

class Comments(models.Model):
    podcast = models.ForeignKey(Podcasts, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    comment = models.TextField()
    created = models.DateTimeField(default=timezone.now, editable=False)
