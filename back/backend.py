import os
import sys
import json
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
from flask_cors import CORS
import uuid

internal_playlist = []

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
            "vote_count": 0
        },
        results,
    )
    test_names_arr = list(test_names_arr)
    return test_names_arr

def find_index(song_uri):
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] == song_uri:
            return i

def update_song_vote(ind, dir):
    internal_playlist[ind]['vote_count'] += 1 if (dir == 'up') else -1

def build_internal_playlist():
    ## TODO: add functionality to build a new playlist or select exisiting playlist
    spotify = get_spotify_api_client()
    results = spotify.playlist_tracks("6bMWOcbmA9X1sl30boENAD")
    global internal_playlist
    internal_playlist = playlist_parsing(results["items"])
    print('\nINTERNAL PLAYLIST\n\n:' + str(results), file=sys.stderr)


def playing_song_status():
    spotify = get_spotify_api_client()
    current_song = spotify.currently_playing(market=None, additional_types=None)
    print("CURRENTLY PLAYING:\n" + str(current_song), file=sys.stderr)

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
    # import pdb
    # pdb.set_trace()
    # pass

def freeze_upcoming_song():
    global internal_playlist
    internal_playlist[1]['locked'] = True
    return internal_playlist[1]['song_uri']

# any song containing the `locked` attribute that isn't currently playing or upcoming_song is removed from internal_playlist (assuming that these have already been played)
def prune(prune_these):
    return

def polling_function():
    playing_song = playing_song_status()
    print(playing_song, file=sys.stderr)
    
    # freeze upcoming song
        # check conditions - more than 50% done, OR duration left is less than 30 seconds, or...
    if playing_song['half_played'] or playing_song['time_remaining'] < 30000:
        upcoming_song_id = freeze_upcoming_song()
        # needs to be tested
        enqueued_songs = [playing_song['song_uri'], upcoming_song_id]
        prune(enqueued_songs)

    # trigger the "delete played songs" action
    # assumptions we're making:
    # - top song is frozen in place at some trigger (not implimented)
    # - want to delete songs that have already been played. Either at voting time, or at some polling interval (requires polling what song status is)
    # - polling interval needs to be as frequent as "freeze next song" interval to avoid votes on pruned songs


def playlist_cleanup(self):

    pass
    # make the api call to see what's playing
    # grab the internal playlist, see where that song falls in the list
    # pop any songs that have played already
    # update the Spotify playlist to reflect that
        

def sort_playlist(spotify):
    global internal_playlist
    playlist_before_sort = internal_playlist.copy()
    internal_playlist = sorted(internal_playlist, key=lambda item: item["vote_count"], reverse = True)

    # takes the selected song from the frontend response and adds it to spotify playlist if the sort order changed
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] != playlist_before_sort[i]["song_uri"]:
            print("made request to Spotify API", file = sys.stderr )
            spotify.playlist_replace_items("6bMWOcbmA9X1sl30boENAD", map(lambda song: song["song_uri"], internal_playlist))
            break

def get_spotify_api_client():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/') # TODO: find a way to tell the front end that it needs to refresh the token. We don't think this works as is
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify

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

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
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
        build_internal_playlist()

        # Step 4. Signed in, display data
        return redirect('http://localhost:8080')


    @app.route("/search", methods=["POST"])
    def search():
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]

        spotify = get_spotify_api_client()
        limit = request.json["limit"] if "limit" in request.json else 5

        results = spotify.search(q=text, type="track", limit=limit)
        return search_result_parsing(results["tracks"]["items"])


    @app.route("/confirm", methods=["POST"])
    def confirm():
        spotify = get_spotify_api_client()

        # takes the selected song from the frontend response and adds it to our internal playlist with 1 vote
        new_song = request.json

        index = find_index(new_song["song_uri"])
        if (index):
            # increment vote count if song is already in playlist
            internal_playlist[index]["vote_count"] += 1
        else:
            # takes the selected song from the frontend response and adds it to spotify playlist
            new_song['vote_count'] = 1
            internal_playlist.append(new_song)
            spotify.playlist_add_items("6bMWOcbmA9X1sl30boENAD", [request.json["song_uri"]])
        
        sort_playlist(spotify)
        return json.dumps(internal_playlist)


    @app.route("/get_playlist", methods=["GET"])
    def get_playlist():
        return json.dumps(internal_playlist)


    # vote endpoint expects a json object with 2 attributes `vote_direction` and `song_uri`
    @app.route("/vote", methods=["POST"])
    def vote():
        target_index = find_index(request.json["song_uri"])
        update_song_vote(target_index, request.json["vote_direction"])
        
        spotify = get_spotify_api_client()
        sort_playlist(spotify)        

        polling_function()

        return json.dumps(internal_playlist)
    return app
