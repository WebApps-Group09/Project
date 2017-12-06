from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Count
from random import randint


## Topic model - referred to as 'pods' on the site
class Topic(models.Model):
    topic = models.CharField(max_length=40, unique=True, blank=False)
    description = models.TextField(blank=True)
    num_podcasts = models.IntegerField(default=0, editable=False)
    num_subscribers = models.IntegerField(default=0, editable=False)


## User subscriptions to an individual topic
class TopicSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, related_name='topicuser')
    pod = models.ForeignKey(Topic, on_delete=models.CASCADE, editable=False, related_name='pod')

    def get_model_type(self):
        return 'topicsubscription'


## User subscriptions to individual creators
class CreatorSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, related_name='user')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, related_name='creator')

    def get_model_type(self):
        return 'creatorsubscription'


## Podcast model functions
# TODO: integrate this function with the podcast model
def file_path(instance, filename):
    instance.file_path = instance.slugfield+'.wav'


# Retrieve a random podcast from the database
class PodcastManager(models.Manager):
    def random(self):
        count = self.aggregate(ids=Count('id'))['ids']
        if count > 0:
            random_index = randint(0, count - 1)
            return self.all()[random_index]
        else:
            return None


# Podcast model
class Podcast(models.Model):
    slugfield = models.SlugField(max_length=200, unique=True, editable=False)
    title = models.CharField(max_length=200, blank=False)
    description = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='', null=True)
    file_type = models.CharField(max_length=3, choices=(('WAV', '.wav'), ('MP3', '.mp3')), default='WAV')
    file_path = models.CharField(max_length=220, null=True, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    views = models.IntegerField(default=0, editable=False)
    num_comments = models.IntegerField(default=0, editable=False)
    num_upvotes = models.IntegerField(default=0, editable=False)
    num_downvotes = models.IntegerField(default=0, editable=False)
    num_favorites = models.IntegerField(default=0, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    updated = models.DateTimeField(default=timezone.now, editable=False)

    objects = PodcastManager()

    def get_model_type(self):
        return 'podcast'


## Comment model
class Comment(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    comment = models.TextField()
    created = models.DateTimeField(default=timezone.now, editable=False)
