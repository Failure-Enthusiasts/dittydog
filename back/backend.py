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
    return None

def update_song_vote(ind, dir):
    internal_playlist[ind]['vote_count'] += 1 if (dir == 'up') else -1

def build_internal_playlist():
    ## TODO: add functionality to build a new playlist or select exisiting playlist
    spotify = get_spotify_api_client()
    results = spotify.playlist_tracks("6bMWOcbmA9X1sl30boENAD")
    global internal_playlist
    internal_playlist = playlist_parsing(results["items"])

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
        if (index is not None):
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

        return json.dumps(internal_playlist)
    return app
