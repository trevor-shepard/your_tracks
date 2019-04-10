from django.db import models
from django.contrib.auth.models import User


from django.utils import timezone
import pytz

from datetime import datetime


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        related_name= "profile",
        primary_key=True,
        on_delete=models.CASCADE
    )
    last_track_pull = models.DateTimeField(default=pytz.timezone(timezone.get_default_timezone_name()).localize(datetime(2002, 3, 22)))
