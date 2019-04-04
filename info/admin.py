from django.contrib import admin
from .models import Track, Artist, Album, Tag, UserTrackHistory

# Register your models here.
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Tag)
admin.site.register(UserTrackHistory)
