from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect
from playapp.models import Playlist, Track
import playapp.recommendation_engine as engine
import logging

logger = logging.getLogger(__name__)

# Keep in sync with playing.html
DELIMITER = '::VzVQxrhNTX::'

def playing(request):
  # playing the requesting piece
  video_id = request.GET.get('video_id', '')
  playlist = request.GET.get('playlist', '')
  template = loader.get_template('playing.html')
  deb_arg = request.GET.get('deb', '0')
  if not playlist:
    return render_landing();
  
  if not video_id:
    video_id = engine.generate_recommendation(playlist).video_id
  library = None
  upcoming = None
  if deb_arg == '1':
    library, upcoming = engine.get_ordered_library(playlist)
  queue = engine.generate_queue(playlist)
  
  context = Context({
    'playlist': playlist,
    'playlists': Playlist.objects.all(),
    'queue': queue,
    'video_id': video_id, 
    'library': library, 
    'upcoming': upcoming,
  })
  return HttpResponse(template.render(context))

def render_landing():
  playlists = engine.get_playlists_and_seeds()
  context = Context({
    'playlists': playlists,
    })
  template = loader.get_template('landing.html')
  return HttpResponse(template.render(context))
  

def generate(request):
  # generates a recommendation from the engine
  playlist = request.GET.get('playlist', 'NO PLAYLIST')
  print "generating for playlist: " + playlist 
  rec = engine.generate_recommendation(playlist)
  response = rec.video_id + DELIMITER + rec.title
  return HttpResponse(response)


def new_playlist(request):
  # render the new playlist form
  context = Context({})
  template = loader.get_template('new_playlist.html')
  return HttpResponse(template.render(context))


def create_playlist(request):
  # create a new playlist
  playlist = request.GET.get('playlist', '')
  video_id = request.GET.get('video_id', '')
  if engine.initialize_playlist(playlist, video_id):
    return redirect(get_url(playlist, video_id))
  else:
    return redirect('/playapp/new_playlist/')


def add_track(request):
  # user adds a track manually
  playlist = request.GET.get('playlist', '')
  video_id_input = request.GET.get('video_id', '')
  engine.set_track_in_db(playlist, video_id_input, Track.POSITIVE)
  return redirect(get_url(playlist, video_id_input))


def modify_track(request):
  # changes track state
  playlist = request.GET.get('playlist', '')
  video_id = request.GET.get('video_id', '')
  state = request.GET.get('state', '')
  force = request.GET.get('force', '0')
  forced = force == "1"
  engine.set_track_in_db(playlist, video_id, state, forced=forced)
  return HttpResponse('OK')


def mark_played(request):
  # marks track as played in DB
  playlist = request.GET.get('playlist', '')
  video_id = request.GET.get('video_id', '')
  tired_arg = request.GET.get('tired', '0')
  tired = (tired_arg == "1")
  engine.mark_played(playlist, video_id, tired=tired)
  return HttpResponse('OK')

def get_suggestions(request):
  playlist = request.GET.get('playlist', '')
  suggestions = engine.get_suggestions(playlist)
  response = ""
  for s in suggestions:
    response += s.video_id + DELIMITER + s.title + DELIMITER
  return HttpResponse(response)


def get_title(request):
  # gets title from DB
  playlist = request.GET.get('playlist', '')
  video_id = request.GET.get('video_id', '')
  title = Playlist.objects.get(name=playlist).track_set.get(video_id=video_id).title
  return HttpResponse(title)


def curate(request):
  playlist = request.GET.get('playlist', '')
  library, upcoming = engine.get_ordered_library(playlist)
  context = Context({
    'playlist' : playlist,
    'library': library,
    'upcoming': upcoming,
    })
  template = loader.get_template('curate.html')
  return HttpResponse(template.render(context))



def get_url(playlist, video_id):
  return '/playapp/?playlist=' + playlist + "&video_id=" + video_id 

