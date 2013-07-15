from datetime import datetime
from django.db import models

class Playlist(models.Model):
    
  def __unicode__(self):
    return self.name
  
  def get_fixture(self):
    my_fields = {"name": self.name, "playlist_clock": self.playlist_clock}
    my_model = {"pk": self.name, "model": "playapp.Playlist", "fields": my_fields}
    return my_model

  name = models.CharField(max_length=16, primary_key=True)
  creation_date = models.DateTimeField('date created')
  
  # used by the engine to tell how recently a track was played
  playlist_clock = models.BigIntegerField(default=0)
  
  last_played = models.DateTimeField('date last played', default=datetime.now())
  
  # space-delimited tags
  tags = models.CharField(max_length=200)


class Track(models.Model):
  def __unicode__(self):
    return self.video_id + ',' + str(self.weight) + ',' + self.state + ',' + str(self.recently_played)

  def get_fixture(self):
    my_fields = {"title": self.title}
    my_model = {"fields": my_fields}
    return my_model

  VIEWED = 'V'
  SEED = 'S'
  POSITIVE = 'P'
  NEGATIVE = 'N'
  UNVIEWED = 'U'

  TRACK_STATE = (
    (VIEWED, 'viewed'),
    (SEED, 'seed'),
    (POSITIVE, 'positive'),
    (NEGATIVE, 'negative'),
    (UNVIEWED, 'unviewed'),
  )

  playlist = models.ForeignKey(Playlist)
  video_id = models.CharField(max_length=30, blank = False)
  weight = models.DecimalField(max_digits=5, decimal_places=2, blank = False)
  state = models.CharField(max_length=1, choices=TRACK_STATE, blank = False)
  creation_date = models.DateTimeField('date created', blank = False)
  
  # set at the current playlist_clock whenever it gets played.
  # will be set in the future when user clicks "I'm tired of this track"
  recently_played = models.IntegerField(default=-1)
  
  # Number of plays
  num_played = models.IntegerField(default=0)

  # human-readable
  title = models.CharField(max_length=200, blank = False)
