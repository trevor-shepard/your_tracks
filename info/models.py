from django.db import models
from core.models import User

#TODO add image fields to all models
#TODO find out what scope (token) needed to access artist info form href
#Should groups take all types of listening history, and weight it diffrently, or just take one type from users
class Group(models.Model):
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(
        User)
    summary = models.CharField(max_length=800, blank=True, null=True)
    

class Tag(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=400, blank=True, null=True)
    wiki_url = models.CharField(max_length=100, blank=True, null=True)

class Artist(models.Model):
    name = models.CharField(max_length=200)
    tag = models.ManyToManyField(
        Tag,
        related_name='tags',
        related_query_name='tags')
    mbid = models.CharField(
        max_length=100,
        primary_key=True,
        editable=False)
    def __str__(self):
        return f"{self.name}"

class Album(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)    
    mbid = models.CharField(
        max_length=100,
        primary_key=True,
        editable=False)    
    def __str__(self):
        return f"{self.name}"
    
class Track(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    artist = models.ManyToManyField(Artist)
    mbid = models.CharField(
        max_length=200,
        primary_key=True,
        editable=False)
    
    def __str__(self):
        return f"{self.name}"
    
#TODO pull listening history after last time pulled
class UserTrackHistory(models.Model):
    user = models.ForeignKey(
        User,
        related_name='track_history',
        related_query_name='track_history',
        on_delete=models.CASCADE
        )
    track = models.ForeignKey(
        Track,
        related_name='user_track_history',
        related_query_name='user_track_history',
        on_delete=models.CASCADE
    )
    played_on = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} listening to {self.track.name}"
    