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
	nav.html('<a href="/playapp/"><image src="/static/img/W.png" width="55"></a><span class="currentPlaylist"></span><a href="#"><span>Playlists</span></a><a href="/playapp/search/"><span>+Playlist</span></a>');
	nav.animate({width:'11em'}, 200);
	
	console.log('in');
}

function displayCurrentPlaylist(playlist){
	var currentPlaylist = $(".currentPlaylist");
	currentPlaylist.html(playlist);
}