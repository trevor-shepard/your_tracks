import requests
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone, dateformat
from django.db import transaction


from datetime import timedelta, datetime

from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from .utils import build_lastfm_api_call


from core.models import User, Profile
from core.serializers import UserSerializer

from .models import Track, Album, UserTrackHistory, Tag, Artist




# Render Methods
def index(request): 
  return render(request, 'info/index.html')


# API Endpoints

# api/top
@api_view(['GET'])
def stats(request):
  user = get_object_or_404(User, pk=request.user.pk)
  
  
  def history(user):
    start = user.profile.last_track_pull.replace(tzinfo=timezone.utc).timestamp()
    response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', start=start))
    response.raise_for_status()
    data = response.json()
    tracks = []
    for track in data['recenttracks']['track']:
      tracks.append(track)
    page = 1
    while page <= int(data['recenttracks']['@attr']['totalPages']):
      response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', start=start, page=page))
      response.raise_for_status()
      data = response.json()
      for track in data['recenttracks']['track']:
        tracks.append(track)
      page += 1

    record_user_history(user, tracks)
  
  history(user)
  

  if request.method == "GET":
    days = int(request.GET['days'])
    from_date = start = timezone.now() - timedelta(days=days)

    history = UserTrackHistory.objects.filter(user=user).filter(played_on__gte=from_date)

    listens = {}

    for listen in history:
      if listen.track.name in listens:
        listens[listen.track.name] = listens[listen.track.name] + 1
      else:
        listens[listen.track.name] = 1
    
    track_data = sorted(listens.items(), key=lambda kv: kv[1])
    track_data.reverse()
    
    return JsonResponse({
      'track_data': track_data
      })


# api/history
# 

def req_history(request):
  user = get_object_or_404(User, pk=request.user.pk)

  if request.method == "GET":
    start = user.profile.last_track_pull.replace(tzinfo=timezone.utc).timestamp()
    import pdb; pdb.set_trace()
    response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', start=start.getTime()))
    response.raise_for_status()
    data = response.json()
    tracks = []
    for track in data['recenttracks']['track']:
      tracks.append(track)
    page = 1
    while page <= int(data['recenttracks']['@attr']['totalPages']):
      response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', start=start, page=page))
      response.raise_for_status()
      data = response.json()
      for track in data['recenttracks']['track']:
        tracks.append(track)
      page += 1

    record_user_history(user, tracks)

      
    return JsonResponse(response.json())






# Private Methods
@transaction.atomic
def record_user_history(user, tracks_data):
  for track_data in tracks_data:
    # check to see if mbid exists, use artist name if mbid does not exist as primary key
    if track_data['artist']['mbid'] == "":
      if len(track_data['artist']['#text']) > 100:
          artist_mbid = track_data['artist']['#text'][:100]
      else:
          artist_mbid=track_data['artist']['#text']
      artist, artist_created = Artist.objects.get_or_create(
        mbid=artist_mbid
      )
    else:
      artist, artist_created = Artist.objects.get_or_create(
        mbid=track_data['artist']['mbid']
      )

    # if new artist created, save to database
    if artist_created:
      artist.name = track_data['artist']['#text']

      # if name is over 200 chars, truncate
      if len(track_data['artist']['#text']) > 200:
        artist.name = track_data['artist']['#text'][:200]
      else:
        artist.name = track_data['artist']['#text']
      artist.save()
      print(f'{artist.name} saved')

    # check to see if mbid exists, use track name if mbid does not exist as primary key
    if track_data['mbid'] == "":
      if len(track_data['name']) >200:
        track_mbid = track_data['name'][:200]
      else:
        track_mbid = track_mbid = track_data['name']

      track, track_created = Track.objects.get_or_create(
        mbid=track_mbid
      )
    else:
      track, track_created = Track.objects.get_or_create(
        mbid=track_data['mbid']
      )

    # if new track created, save to database
    if track_created:

      # if name is over 200 chars, truncate
      if len(track_data['name']) >200:
        track.name = track_data['name'][:200]
        
      else:
        track.name = track_data['name']
      track.artist.add(artist)
      track.save()
      print(f"{track.name} saved")

    # create new listening event
    event = UserTrackHistory(
      user= user,
      track= track
    )

    # record date played
    if 'date' in track_data.keys():
      if track_data['date']['#text'] != '':
        date = track_data['date']['#text']
        date = datetime.strptime(date, '%d %b %Y, %H:%M')
        date = timezone.make_aware(date)
        event.played_on = date
      else:
        event.played_on = datetime.now()
    else:
      event.played_on = datetime.now()

    event.save()
    print(f"{user.username} listening to {track.name} saved")
  
  # update user's last track pull to prevent pulling duplicate histories
  user.last_track_pull = timezone.now()
  user.save()
  print(f"user history updated at {timezone.now()}")
    
    

    












