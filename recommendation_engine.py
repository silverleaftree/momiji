from datetime import datetime
from decimal import Decimal
from playapp.models import Playlist, Track
from collections import defaultdict
import playapp.api as api
import random


# model math stuff
# how much we decay per related item.
FACTOR = .6
# how much we decay the chance for a recently played track, per track played
RECENT_FACTOR = Decimal(".6")
QUEUE_SIZE = 5

# how many tracks until the model forgets we've played this track
RECENT_TRACKED = 9
IM_TIRED_FUTURE = 30

STATE_WEIGHTS = {
  Track.VIEWED : 1,
  Track.SEED : 3,
  Track.POSITIVE : 2,
  Track.NEGATIVE : -1,
  Track.UNVIEWED : 0,
}


# Sets a track state to state_input if it's allowed.
# playlist must exist, video_id might not.
def set_track_in_db(playlist, video_id_input, state_input, forced=False, title=None):
  # try to lookup the track
  playlist_model = Playlist.objects.get(name=playlist)
  video_weight = STATE_WEIGHTS[state_input]
  if playlist_has_video(playlist_model, video_id_input):
    print 'modifying existing track: ' + video_id_input + ' for playlist: ' + playlist
    # undo the weight of the children
    existing_track = playlist_model.track_set.get(video_id=video_id_input)
    existing_state = existing_track.state
    # don't change the seed video state ever.
    if existing_state == Track.SEED:
      return
    # don't set anything to VIEWED if it has another user state,
    # unless we're curating with the forced flag
    if state_input == Track.VIEWED and existing_state != Track.UNVIEWED and not forced:
      print "not setting as VIEWED as track has another state"
      return
    video_weight += -1 * STATE_WEIGHTS[existing_state]
    existing_track.state = state_input
    existing_track.weight = STATE_WEIGHTS[state_input]
    existing_track.save()
  else:
    print 'adding new track: ' + video_id_input
    create_track(playlist_model, video_id_input, video_weight, state_input, title=title)

  # set new weights for children with the weight differential
  related_tracks = api.get_related_tracks(video_id_input)
  for related in related_tracks:
    video_weight *= FACTOR 
    increment_child_track(playlist_model, related['video_id'], video_weight, title=related['title']) 


def increment_child_track(playlist_model, video_id_input, weight_input, title=None):
  if weight_input < .01:
    # only record non-zero weights
    return
  if not playlist_has_video(playlist_model, video_id_input):
    create_track(playlist_model, video_id_input, weight_input, Track.UNVIEWED, title=title)
  else:
    track = playlist_model.track_set.get(video_id=video_id_input)
    if track.state == Track.UNVIEWED:
      track.weight += Decimal(str(weight_input))
      track.save()


def generate_queue(playlist):
  # set the playlist as played now for ordering purposes.
  playlist_model = Playlist.objects.get(name=playlist)
  playlist_model.last_played = datetime.now()
  playlist_model.save()
  queue = []
  for i in range(0,QUEUE_SIZE):
    queue.append(generate_recommendation(playlist));
  return queue


def generate_recommendation(playlist):
  # only recommend positive weights
  playlist_model = Playlist.objects.get(name=playlist)
  tracks = playlist_model.track_set.filter(weight__gt=0)

  total_weight = Decimal('0')
  for track in tracks:
    total_weight += effective_weight(track, playlist_model)

  random_choice = Decimal(str(random.random())) * total_weight

  for track in tracks:
    random_choice -= effective_weight(track, playlist_model) 
    if random_choice <= 0:
      mark_played(playlist, track.video_id, increment_clock=False)
      return track
  raise Exception('generate_recommendation failed')


def effective_weight(track_model, playlist_model):
  recently_played = track_model.recently_played
  playlist_clock = playlist_model.playlist_clock
  time_since_last_played = playlist_clock - recently_played
  if recently_played >= 0 and time_since_last_played < RECENT_TRACKED:
    return track_model.weight * RECENT_FACTOR ** Decimal(RECENT_TRACKED - time_since_last_played)
  else:
    return track_model.weight


# Moves playlist clock forward one tick, marks current video id as
# played so it doesn't come up so soon.
def mark_played(playlist, video_id, increment_clock=True, tired=False):
  playlist_model = Playlist.objects.get(name=playlist)
  if increment_clock:
    playlist_model.playlist_clock += 1
    print "incrementing playlist clock to : " + str(playlist_model.playlist_clock)
  track_model = playlist_model.track_set.get(video_id=video_id)
  track_model.recently_played = playlist_model.playlist_clock
  if tired:
    track_model.recently_played += IM_TIRED_FUTURE
  track_model.save()
  playlist_model.save()


# adds the video id with current state to the DB
def create_track(playlist_model, video_id, weight, state, title=None):
  if not title:
    title = api.get_title(video_id)
  playlist_model.track_set.create(
    video_id=video_id,
    weight=Decimal(str(weight)),
    state=state,
    title=title,
    creation_date=datetime.now(),
    )


# Creates a new playlist with one seed video
def initialize_playlist(playlist, video_id_input):
  if not valid_playlist(playlist):
    return False
  playlist_model = Playlist(name=playlist, creation_date=datetime.now())
  playlist_model.save()
  set_track_in_db(playlist, video_id_input, Track.SEED)
  return True


def playlist_has_video(playlist_model, video_id):
  return playlist_model.track_set.filter(video_id=video_id)


def valid_playlist(playlist):
  return (
    playlist and not '"' in playlist and not "'" in playlist and
    len(Playlist.objects.filter(name=playlist)) == 0
  )


def get_ordered_library(playlist):
  track_set = Playlist.objects.get(name=playlist).track_set
  library = []
  library.extend(track_set.filter(state=Track.SEED))
  library.extend(track_set.filter(state=Track.POSITIVE))
  library.extend(track_set.filter(state=Track.VIEWED))
  library.extend(track_set.filter(state=Track.NEGATIVE))
  upcoming = track_set.filter(state=Track.UNVIEWED).filter(weight__gte=0).order_by('-weight')
  return library, upcoming


def get_playlists_and_seeds(tag):
  playlists = Playlist.objects.all().order_by('-last_played')
  if tag:
    filtered = []
    for playlist in playlists:
      if tag in get_tags(playlist):
        filtered.append(playlist)
    playlists = filtered
  for playlist in playlists:
    seed_track = playlist.track_set.get(state=Track.SEED)
    playlist.seed_track = seed_track
  return playlists


def get_tags(playlist_model):
  return playlist_model.tags.split(' ')


def get_all_tags():
  playlists = Playlist.objects.all()
  tags = defaultdict(int)
  for playlist in playlists:
    for tag in get_tags(playlist):
      tags[tag] += 1
  sorted_tags = sorted(tags, key=tags.__getitem__, reverse=True)
  return sorted_tags


def get_suggestions(playlist):
  playlist_model = Playlist.objects.get(name=playlist)
  positive_tracks = playlist_model.track_set.filter(state=Track.UNVIEWED).filter(weight__gt=0)
  return positive_tracks.order_by('-weight')[:QUEUE_SIZE]


def delete_playlist(playlist):
  playlist_model = Playlist.objects.get(name=playlist)
  playlist_model.delete()


def set_tags(playlist, tags):
  playlist_model = Playlist.objects.get(name=playlist)
  playlist_model.tags = tags
  playlist_model.save()


def get_title(playlist, video_id):
  return Playlist.objects.get(name=playlist).track_set.get(video_id=video_id).title
  
