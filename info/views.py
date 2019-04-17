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

from .models import Track, UserTrackHistory, Artist, UserTrackTally




# Render Methods
def index(request): 
  return render(request, 'info/index.html')


# API Endpoints
# api/top
@api_view(['GET'])
def stats(request):
  user = get_object_or_404(User, pk=request.user.pk)
  
  def history(user):
    start = int(user.profile.last_track_pull.replace(tzinfo=timezone.utc).timestamp())
    
    response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', _from=start))
    response.raise_for_status()
    data = response.json()
    if isinstance(data['recenttracks']['track'], list):
      tracks = []
      for track in data['recenttracks']['track']:
        tracks.append(track)
      page = 1
      while page <= int(data['recenttracks']['@attr']['totalPages']):
        response = requests.get(build_lastfm_api_call(user=request.user, method='user.getrecenttracks', limit='200', _from=start, page=page))
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
def find_artist(mbid, name):
  # check to see if mbid exists, use artist name if mbid does not exist as primary key
  if mbid == "":
    if len(name) > 100:
        artist_mbid = name[:100]
    else:
        artist_mbid=name
    artist, artist_created = Artist.objects.get_or_create(
      mbid=artist_mbid
    )
  else:
    artist, artist_created = Artist.objects.get_or_create(
      mbid=mbid
    )

  # if new artist created, save to database
  if artist_created:
    # if name is over 200 chars, truncate
    if len(name) > 100:
      artist.name = name[:100]
    else:
      artist.name = name
    artist.save()
    print(f'{artist.name} saved')

def find_track(name, mbid, artist):
  # check to see if mbid exists, use track name if mbid does not exist as primary key
  if mbid == "":
    if len(name) >200:
      track_mbid = name[:200]
    else:
      track_mbid = name

    track, track_created = Track.objects.get_or_create(
      mbid=track_mbid
    )
  else:
    track, track_created = Track.objects.get_or_create(
      mbid=mbid
    )

  # if new track created, save to database
  if track_created:

    # if name is over 200 chars, truncate
    if len(name) >200:
      track.name = name[:200]
      
    else:
      track.name = name
    track.artist.add(artist)
    track.save()
    print(f"{track.name} saved")

@transaction.atomic
def record_user_history(user, tracks_data):

  for track_data in tracks_data:
    # find or create artist
    artist = find_artist(track_data['artist']['mbid'], track_data['artist']['#text'])

    # find or create track
    track = find_track(track_data['name'], mbid, artist)

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

    tally = UserTrackTally.objects.get_or_create(
      user= user,
      track= track
    )
    tally.count += 1
    tally.save()

    print(f"{user.username} listening to {track.name} saved")
  
  # update user's last track pull to prevent pulling duplicate histories
  user_profile = user.profile
  user_profile.last_track_pull = timezone.now()
  user_profile.save()

  print(f"user history updated at {timezone.now()}")
    
    

    












