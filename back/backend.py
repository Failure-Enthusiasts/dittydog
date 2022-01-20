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
    # test_names_arr = json.dumps(list(test_names_arr))
    return test_names_arr

def find_index(song_uri):
    global internal_playlist
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] == song_uri:
            return i

def update_song_vote(ind, dir):
    global internal_playlist
    internal_playlist[ind]['vote_count'] += 1 if (dir == 'up') else -1

def build_internal_playlist():
    ## TODO: add functionality to build a new playlist or select exisiting playist
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    ## TODO: may need some recourse for an expired token as this is an internal method call
    spotify2 = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify2.playlist_tracks("6bMWOcbmA9X1sl30boENAD")
    print(playlist_parsing(results["items"]))
    global internal_playlist
    internal_playlist = playlist_parsing(results["items"])
    print(playlist_parsing(results["items"]), file=sys.stderr)

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './.flask_session/'
    Session(app)
    spotify = spotipy.Spotify(client_credentials_manager=spotipy.oauth2.SpotifyClientCredentials()) # TODO: remove this in favor of getting token for each API call like is done in confirm endpoint




    @app.route('/')
    def index():
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private', cache_handler=cache_handler, show_dialog=True)

        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            print(request.args.get("code"), file=sys.stderr)
            auth_manager.get_access_token(request.args.get("code"))
            return redirect('/')

        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            return f'<h2><a href="{auth_url}">Sign in</a></h2>'
        #building internal playlist as part of the default auth flow
        build_internal_playlist()
        # Step 4. Signed in, display data
        return redirect('http://localhost:8080')

    


    @app.route("/search", methods=["POST"])
    def search():
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]
        limit = request.json["limit"] if "limit" in request.json else 5

        # TODO: update this so the token is retrieved in each API call like it is in confirm
        results = spotify.search(q=text, type="track", limit=limit)
        return search_result_parsing(results["tracks"]["items"])


    @app.route("/confirm", methods=["POST"])
    def confirm():
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify2 = spotipy.Spotify(auth_manager=auth_manager)
        print(request.json, file=sys.stderr)
        #takes the selected song from the frontend response and adds it to our internal playlist with 1 vote
        new_song = request.json
        new_song['vote_count'] = 1
        global internal_playlist
        internal_playlist.append(new_song)
        print(internal_playlist, file=sys.stderr)
        #takes the selected song from the frontend response and adds it to spotify playlist
        results = spotify2.playlist_add_items("6bMWOcbmA9X1sl30boENAD", [request.json["song_uri"]])
        return "very very gooooood request", 200

    @app.route("/get_playlist", methods=["GET"])
    def get_playlist():
        return json.dumps(internal_playlist)

    # vote endpoint expects a json object with 2 attributes `vote_direction` and `song_uri`
    @app.route("/vote", methods=["POST"])
    def vote():
        print(request.json, file=sys.stderr)
        target_index = find_index(request.json["song_uri"])
        update_song_vote(target_index, request.json["vote_direction"])
        ## this function will :
        # 1. perform the internal playlist resorting 
        #   oneliner for resorting
        #   sorted(internal_playlist, key=lambda item: item[vote_count], reverse = True)
        # 2. (if necessary- internal playlist order has changed) make an async call to update the playlist in spotify (https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.playlist_replace_items)
        # 3. return the resorted internal playlist back to the front 
        #return recalc_internal_playlist()

    return app
