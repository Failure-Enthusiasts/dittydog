import os
import sys
import json
from flask import Flask, session, request, redirect, copy_current_request_context
from flask_session import Session
import spotipy
from flask_cors import CORS
import uuid
from time import sleep
from threading import Thread
from datetime import datetime
import socketio
import helper_functions

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

internal_playlist = []
playlist_is_running = False

# caches_folder = './.spotify_caches/'
# if not os.path.exists(caches_folder):
#     os.makedirs(caches_folder)

# def session_cache_path():
#     return caches_folder + session.get('uuid')

# def build_internal_playlist():
#     ## TODO: add functionality to build a new playlist or select exisiting playlist
#     spotify = helper_functions.get_spotify_api_client()
#     global playlist_id
#     playlist_id = spotify.user_playlist_create(spotify.current_user()["id"], f'{spotify.current_user()["display_name"]}, USE THE DITTYDOG APP TO ADD SONGS, YOU FOOL!', public=True, collaborative=False, description='')["uri"]
#     results = spotify.playlist_tracks(playlist_id)
#     playlist_id_only = playlist_id.split(':')[2]
#     print(f'Playlist URL: https://open.spotify.com/playlist/{playlist_id_only}', file=sys.stderr)
#     global internal_playlist
#     internal_playlist = helper_functions.playlist_parsing(results["items"])
#     print('\nINTERNAL PLAYLIST\n\n:' + str(results), file=sys.stderr)
#     return playlist_id_only



def playing_song_status():
    spotify = helper_functions.get_spotify_api_client()
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


def freeze_upcoming_song():
    global internal_playlist
    # internal_playlist[0]['locked'] = True
    internal_playlist[1]['locked'] = True
    # internal_playlist[2]['locked'] = True
    return internal_playlist[1]['song_uri']

# any song containing the `locked` attribute that isn't currently playing or upcoming_song is removed from internal_playlist (assuming that these have already been played)
def prune(enqueued_songs):
    print(str(enqueued_songs), file=sys.stderr)
    spotify = helper_functions.get_spotify_api_client()
    prune_these = []
    # probably need to update the format of prune_these to correspond to items: https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.playlist_remove_all_occurrences_of_items
    # https://a.cl.ly/DOud82GK
    global internal_playlist
    for song in internal_playlist:
        if song['locked'] and song['song_uri'] not in enqueued_songs:
            prune_these.append(song['song_uri'])
            print(f'ABOUT TO PRUNE: {song["song_uri"]}', file=sys.stderr)
            print(f'ABOUT TO PRUNE, and playlist is: {internal_playlist}', file=sys.stderr)

            internal_playlist.remove(song)
    if len(prune_these) != 0:
        print(f'PRUNING: {prune_these}', file=sys.stderr)
        spotify = helper_functions.get_spotify_api_client()
        spotify.playlist_remove_all_occurrences_of_items(playlist_id, prune_these)


def polling_function():
    playing_song = playing_song_status()
    ## if none return
    print(playing_song, file=sys.stderr)

    if playing_song:
        # freeze upcoming song
            # check conditions - more than 50% done, OR duration left is less than 30 seconds, or...
        if (playing_song['half_played'] or playing_song['time_remaining'] < 30000) and len(internal_playlist) > 1:
            upcoming_song_id = freeze_upcoming_song()
            enqueued_songs = [playing_song['song_uri'], upcoming_song_id]
            # trigger the "delete played songs" action
            prune(enqueued_songs)
            # Tell the frontend to manually pull the new playlist
            my_message("Hey FrontEnd, manually pull the new playlist!") # this successfully emits on both sockets - front and backend

    
    # assumptions we're making:
    # - [x] top song is frozen in place at some trigger
        # Timer'd start? How to do
        # Default vote and song count?
    # - [x - test though!] want to delete songs that have already been played. Either at voting time, or at some polling interval (requires polling what song status is)
    # - !!! Implement timer: polling interval needs to be as frequent as "freeze next song" interval to avoid votes on pruned songs

def start_playing():
    global internal_playlist
    global playlist_is_running

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
        
def sort_playlist(spotify):
    global internal_playlist
    start = len([song for song in internal_playlist if song['locked']])
    playlist_before_sort = internal_playlist.copy()
    internal_playlist[start:] = sorted(internal_playlist[start:], key=lambda item: item["vote_count"], reverse = True)
    # takes the selected song from the frontend response and adds it to spotify playlist if the sort order changed
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] != playlist_before_sort[i]["song_uri"]:
            print("made request to Spotify API", file = sys.stderr )
            spotify.playlist_replace_items(playlist_id, map(lambda song: song["song_uri"], internal_playlist))
            break

# def helper_functions.get_spotify_api_client():
#     cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
#     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
#     if not auth_manager.validate_token(cache_handler.get_cached_token()):
#         return redirect('/') # TODO: find a way to tell the front end that it needs to refresh the token. We don't think this works as is
#     spotify = spotipy.Spotify(auth_manager=auth_manager)
#     return spotify

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './.flask_session/'
    Session(app)

    @app.route('/')
    def index():
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=helper_functions.session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private', cache_handler=cache_handler, show_dialog=True)

        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            auth_manager.get_access_token(request.args.get("code"))
            return redirect('/')

        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            return f'<h2><a href="{auth_url}">Sign in</a></h2>'

        # building internal playlist as part of the default auth flow
        global internal_playlist
        global playlist_id
        internal_playlist, playlist_id = helper_functions.build_internal_playlist(internal_playlist)

        # Step 4. Signed in, display data
        return redirect(f'http://localhost:8080/?playlist_id={playlist_id}')


    @app.route("/search", methods=["POST"])
    def search():
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]

        spotify = helper_functions.get_spotify_api_client()
        limit = request.json["limit"] if "limit" in request.json else 5

        results = spotify.search(q=text, type="track", limit=limit)
        return helper_functions.search_result_parsing(results["tracks"]["items"])


    @app.route("/confirm", methods=["POST"])
    def confirm():
        spotify = helper_functions.get_spotify_api_client()

        # takes the selected song from the frontend response and adds it to our internal playlist with 1 vote
        new_song = request.json
        index = helper_functions.find_index(internal_playlist, new_song["song_uri"])
        if (index is not None):
            # increment vote count if song is already in playlist
            internal_playlist[index]["vote_count"] += 1
        else:
            # takes the selected song from the frontend response and adds it to spotify playlist
            new_song['vote_count'] = 1
            new_song['locked'] = False
            internal_playlist.append(new_song)
            spotify.playlist_add_items(playlist_id, [request.json["song_uri"]])
        
        sort_playlist(spotify)
        return json.dumps(internal_playlist)


    @app.route("/get_playlist", methods=["GET"])
    def get_playlist():
        return json.dumps(internal_playlist)

    @app.route("/polling_and_pruning", methods=["POST"])
    def polling_and_pruning():
        @copy_current_request_context
        def background_task():
            while True:
                print(datetime.now(), file=sys.stderr)
                sys.stderr.flush()
                start_playing()
                polling_function()
                sleep(10)
        thread = Thread(target=background_task)
        thread.daemon = True
        thread.start()
        
        return json.dumps(internal_playlist)

    @app.route("/another_endpoint", methods=["POST"])
    def another_endpoint():
        session_str = helper_functions.session_cache_path()
        print(session_str, file=sys.stderr)
        return session_str

    # vote endpoint expects a json object with 2 attributes `vote_direction` and `song_uri`
    @app.route("/vote", methods=["POST"])
    def vote():
        global internal_playlist
        target_index = helper_functions.find_index(internal_playlist, request.json["song_uri"])
        internal_playlist = helper_functions.update_song_vote(internal_playlist, target_index, request.json["vote_direction"])

        spotify = helper_functions.get_spotify_api_client()
        sort_playlist(spotify)        

        return json.dumps(internal_playlist)
        

    return app