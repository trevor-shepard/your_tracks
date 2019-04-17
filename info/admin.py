from django.contrib import admin
from .models import Track, Artist, UserTrackHistory

# Register your models here.
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(UserTrackHistory)
