from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from .models import Track, UserTrackTally

class TrackTallySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrackTally
        fields = ('track', 'count')
        depth = 2