from django.db import models
from core.models import User

class Artist(models.Model):
    name = models.CharField(max_length=200)
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

class UserTrackTally(models.Model):
    user = models.ForeignKey(
        User,
        related_name='track_tally',
        related_query_name='track_tally',
        on_delete=models.CASCADE
    )
    track = models.ForeignKey(
        Track,
        related_name='user_track_tally',
        related_query_name='user_track_tally',
        on_delete=models.CASCADE
    )

    played_on = models.DateTimeField(auto_now_add=True)

    count= models.IntegerField(default=0)
    