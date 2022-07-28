import json
import sys
import os
from flask import session
import spotipy
import socketio

sio = socketio.Client(logger=False, engineio_logger=True)

@sio.event
def connect():
    print("connection established", flush=True)

@sio.event
def my_message(data):
    print("message received with ", data, flush=True)
    sio.emit("incomingData", data)

@sio.event
def disconnect():
    print("disconnected from server", flush=True)

print("before sio.connect", file=sys.stderr)
sio.connect("http://host.docker.internal:4001")

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

def search_result_parsing(results):
        test_names_arr = map(
            lambda x: {
                "song_name": x["name"],
                "song_id": x["id"],
                "song_uri": x["uri"],
                "album_name": x["album"]["name"],
                "artist_name": x["artists"][0]["name"],
                "duration": x["duration_ms"],
                "img_link": x["album"]["images"][0]["url"],
            },
            results,
        )
        test_names_arr = json.dumps(list(test_names_arr))
        return test_names_arr

def get_spotify_api_client():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/') # TODO: find a way to tell the front end that it needs to refresh the token. We don't think this works as is
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify

def playlist_parsing(results):
    test_names_arr = map(
        lambda x: {
            "song_name": x["track"]["name"],
            "song_id": x["track"]["id"],
            "song_uri": x["track"]["uri"],
            "album_name": x["track"]["album"]["name"],
            "artist_name": x["track"]["artists"][0]["name"],
            "duration": x["track"]["duration_ms"],
            "img_link": x["track"]["album"]["images"][0]["url"],
            "vote_count": 0,
            "locked": False
        },
        results,
    )
    test_names_arr = list(test_names_arr)
    return test_names_arr

def update_song_vote(internal_playlist, ind, dir):
    internal_playlist[ind]['vote_count'] += 1 if (dir == 'up') else -1
    return internal_playlist

def find_index(internal_playlist, song_uri):
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] == song_uri:
            return i
    return None

def build_internal_playlist(internal_playlist):
    ## TODO: add functionality to build a new playlist or select exisiting playlist
    spotify = get_spotify_api_client()
    playlist_id = spotify.user_playlist_create(spotify.current_user()["id"], f'{spotify.current_user()["display_name"]}, USE THE DITTYDOG APP TO ADD SONGS, YOU FOOL!', public=True, collaborative=False, description='')["uri"]
    results = spotify.playlist_tracks(playlist_id)
    playlist_id_only = playlist_id.split(':')[2]
    print(f'Playlist URL: https://open.spotify.com/playlist/{playlist_id_only}', file=sys.stderr)
    internal_playlist = playlist_parsing(results["items"])
    print('\nINTERNAL PLAYLIST\n\n:' + str(results), file=sys.stderr)
    return internal_playlist, playlist_id_only

def playing_song_status():
    spotify = get_spotify_api_client()
    current_song = spotify.currently_playing(market=None, additional_types=None)
    if not current_song:
     return
    playing_song = {}
    # current_song
    playing_song['song_uri'] = current_song['item']['uri']

    # current playing?
    playing_song['is_playing'] = current_song['is_playing']

    # time remaining?
    playing_song['time_remaining'] = current_song['item']['duration_ms'] - current_song['progress_ms']
    playing_song['half_played'] = 0.5 < (current_song['progress_ms'] / current_song['item']['duration_ms'])
    return playing_song

def freeze_upcoming_song(internal_playlist):
    # internal_playlist[0]['locked'] = True
    internal_playlist[1]['locked'] = True
    # internal_playlist[2]['locked'] = True
    return internal_playlist[1]['song_uri']

# any song containing the `locked` attribute that isn't currently playing or upcoming_song is removed from internal_playlist (assuming that these have already been played)
def prune(enqueued_songs, internal_playlist, playlist_id):
    print(str(enqueued_songs), file=sys.stderr)
    spotify = get_spotify_api_client()
    prune_these = []
    # probably need to update the format of prune_these to correspond to items: https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.playlist_remove_all_occurrences_of_items
    # https://a.cl.ly/DOud82GK
    for song in internal_playlist:
        if song['locked'] and song['song_uri'] not in enqueued_songs:
            prune_these.append(song['song_uri'])
            print(f'ABOUT TO PRUNE: {song["song_uri"]}', file=sys.stderr)
            print(f'ABOUT TO PRUNE, and playlist is: {internal_playlist}', file=sys.stderr)

            internal_playlist.remove(song)
    if len(prune_these) != 0:
        print(f'PRUNING: {prune_these}', file=sys.stderr)
        spotify = get_spotify_api_client()
        spotify.playlist_remove_all_occurrences_of_items(playlist_id, prune_these)

def polling_function(internal_playlist, playlist_id):
    playing_song = playing_song_status()
    ## if none return
    print(playing_song, file=sys.stderr)

    if playing_song:
        # freeze upcoming song
            # check conditions - more than 50% done, OR duration left is less than 30 seconds, or...
        if (playing_song['half_played'] or playing_song['time_remaining'] < 30000) and len(internal_playlist) > 1:
            upcoming_song_id = freeze_upcoming_song(internal_playlist)
            enqueued_songs = [playing_song['song_uri'], upcoming_song_id]
            # trigger the "delete played songs" action
            prune(enqueued_songs, internal_playlist, playlist_id)
            # Tell the frontend to manually pull the new playlist
            my_message("Hey FrontEnd, manually pull the new playlist!") # this successfully emits on both sockets - front and backend


    # assumptions we're making:
    # - [x] top song is frozen in place at some trigger
        # Timer'd start? How to do
        # Default vote and song count?
    # - [x - test though!] want to delete songs that have already been played. Either at voting time, or at some polling interval (requires polling what song status is)
    # - !!! Implement timer: polling interval needs to be as frequent as "freeze next song" interval to avoid votes on pruned songs

def start_playing(internal_playlist, playlist_is_running):
    if playlist_is_running == False:
        playlist_is_running = True
        internal_playlist[0]['locked'] = True
        my_message("Hey FrontEnd, manually pull the new playlist!")

        # removing auto-play for now, doesn't work ##
        # spotify = helper_functions.get_spotify_api_client()
        # try:
        #     spotify.start_playback(context_uri=playlist_id)
        # except:
        #     print("Need premium", file=sys.stderr)
        # lock the first song
        # if internal_playlist is not None:
        #     internal_playlist[0]['locked'] = True

def sort_playlist(spotify, internal_playlist, playlist_id):
    start = len([song for song in internal_playlist if song['locked']])
    playlist_before_sort = internal_playlist.copy()
    internal_playlist[start:] = sorted(internal_playlist[start:], key=lambda item: item["vote_count"], reverse = True)
    # takes the selected song from the frontend response and adds it to spotify playlist if the sort order changed
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] != playlist_before_sort[i]["song_uri"]:
            print("made request to Spotify API", file = sys.stderr )
            spotify.playlist_replace_items(playlist_id, map(lambda song: song["song_uri"], internal_playlist))
            break