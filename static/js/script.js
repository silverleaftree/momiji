/* VARIABLES
==================*/
var nav= $(".nav");

/* #Navigation
==================*/
function shrinkNavBar(){
	nav.html('<img src="/static/img/W-M.png" width="40" /><span class="currentPlaylist"></span>');
	nav.animate({width:'3.5em'}, 200);
	console.log('out');
}

function growNavBar(){
	nav.html('<a href="/playapp/"><image id="logo" src="/static/img/W.png" width="55"></a><span class="currentPlaylist"></span><a href="#"><span>Playlists</span></a><a href="/playapp/search/"><span>+Playlist</span></a>');
	nav.animate({width:'11em'}, 200);
	
	console.log('in');
}

function displayPlaylistSeed(playlist){
	var currentPlaylist = $(".currentPlaylist");
	currentPlaylist.html(playlist);
}

/* Playlist
==================*/
  // keep in sync with views.DELIMITER
  var DELIMITER = "::VzVQxrhNTX::";
  // keep in sync with recommendation_engine.QUEUE_SIZE
  var QUEUE_SIZE = 5;
  var THUMB_PRE = "http://i3.ytimg.com/vi/";
  var THUMB_POST = "/hqdefault.jpg";

  // use lastSeen so we don't doublecount markPlayed calls.
  var lastSeen = "";
  var current_track = make_track("{{ video_id }}", "{{video_title}}");
  var playlist = "{{ playlist }}";

  // INITIALIZATION CODE

  var queue = new Array();
  {% for track in queue %}
    queue.push(make_track("{{ track.video_id }}", "{{ track.title }}"));
  {% endfor %}
  var queue_titles = new Array();
  var queue_imgs = new Array();

  var suggestions = new Array();
  var suggest_titles = new Array();
  var suggest_imgs = new Array();

  var tag = document.createElement('script');

  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

  var tags_textbox;

  var player;
  function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: current_track.video_id,
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  }

  function onPlayerReady(event) {
    console.log("onplayerready called");
    for (var i = 0; i < QUEUE_SIZE; i++) {
      queue_titles.push(document.getElementById('queue_title_' + i));
      queue_imgs.push(document.getElementById('queue_img_' + i));
      suggest_titles.push(document.getElementById('suggest_title_' + i));
      suggest_imgs.push(document.getElementById('suggest_img_' + i));
    }
    event.target.playVideo();
    refresh_queue();
    refresh_suggestions();
    tags_textbox = document.getElementById("tags_textbox");
  }

  // PLAYER CODE

  function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED ) {
      finishedPlaying();
    } else if ( event.data = YT.PlayerState.PLAYING ) {
      startedPlaying();
    }
  }

  function startedPlaying() {
    if (lastSeen != current_track.video_id) {
      lastSeen = current_track.video_id;
      $.get("mark_played/?playlist=" + playlist + "&video_id=" + current_track.video_id, function(data) {});
    }
  }

  function finishedPlaying() {
    $.get("modify_track/?playlist=" + playlist + "&video_id=" + current_track.video_id + "&state=V", function(data) {
      nextVideo();
    });
  }

  // ACTION FUNCTIONS

  function thumbsDown() {
    $.get(
      "modify_track/?playlist=" + playlist + "&video_id=" + current_track.video_id + "&state=N",
      function(data) {
        nextVideo();
      });
  }

  function thumbsUp() {
    $.get("modify_track/?playlist=" + playlist + "&video_id=" + current_track.video_id + "&state=P", function(data) {});
  }

  function remove_from_queue(index) {
    queue.splice(index,1);
    queue_another();
  }

  function thumbs_down_from_queue(index) {
    $.get(
      "modify_track/?playlist=" + playlist + "&video_id=" + queue[index].video_id + "&state=N",
      function(data) {
        queue.splice(index,1);
        queue_another();
      });
  }

  function suggest_play_now(index) {
    set_track_playing(suggestions[index]);
    $.get("modify_track/?playlist=" + playlist + "&video_id=" + suggestions[index].video_id + "&state=V", function(data) {
      refresh_suggestions();
    });
  }

  function suggest_thumbs_down(index) {
    $.get("modify_track/?playlist=" + playlist + "&video_id=" + suggestions[index].video_id + "&state=N", function(data) {
      refresh_suggestions();
    });
  }


  function tired() {
    $.get("mark_played/?playlist=" + playlist + "&video_id=" + current_track.video_id + "&tired=1", function(data) {
      nextVideo();
    });
  }

  function on_add_track_select(sel) {
    var value = sel.options[sel.selectedIndex].value;
    if (value == "no_choice") {
      console.log("default choice selected");
    } else if (value == "a_new_playlist") {
      window.location = "new_playlist/?video_id=" + current_track.video_id;
    } else {
      console.log("add to: " + value);
      $.get("add_track/?playlist=" + value + "&video_id=" + current_track.video_id, function(data) {
        alert("Track added!");
      });
    }
  }

  function set_tags() {
    $.get("/playapp/set_tags/?playlist={{ playlist }}&tags=" + tags_textbox.value, function(data) {
      alert("Tags set!");
    });
    return false;
  }

  // HELPER FUNCTIONS

  function nextVideo() {
    current_track = queue.shift();
    set_track_playing(current_track);
    queue_another();
  }

  function queue_another() {
    $.get("generate/?playlist=" + playlist, function(data) {
      queue.push(parse_track(data));
      refresh_queue();
    });
  }

  function refresh_queue() {
    for (var i = 0; i < QUEUE_SIZE; i++) {
      queue_imgs[i].src = THUMB_PRE + queue[i].video_id + THUMB_POST;
      queue_titles[i].innerHTML = queue[i].title.substring(0,35);
    }
  }

  function play_now(index) {
    set_track_playing(queue[index]);
    remove_from_queue(index);
  }

  function parse_track(response) {
    var track = new Object();
    var parsed = response.split(DELIMITER);
    track.video_id = parsed[0];
    track.title = parsed[1];
    return track;
  }

  function make_track(video_id, title) {
    var track = new Object();
    track.video_id = video_id;
    track.title = title;
    return track;
  }

  function refresh_suggestions() {
    $.get("get_suggestions/?playlist=" + playlist, function(data) {
      var parsed = data.split(DELIMITER);
      suggestions = new Array();
      for (var i = 0; i < QUEUE_SIZE; i++) {
        suggestions.push(make_track(parsed[i*2], parsed[i*2 + 1]));
      }
      for (var i = 0; i < QUEUE_SIZE; i++) {
        suggest_imgs[i].src = THUMB_PRE + suggestions[i].video_id + THUMB_POST;
        suggest_titles[i].innerHTML = suggestions[i].title.substring(0,35);
      }
      console.log("refreshed: " + suggestions);
    });
  }

  function set_track_playing(track) {
    current_track = track;
    player.loadVideoById(current_track.video_id);
  }