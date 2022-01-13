import os
import sys
import json
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
from flask_cors import CORS, cross_origin
import uuid

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


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

        # Step 4. Signed in, display data
        return redirect('http://localhost:8080')

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
            results["tracks"]["items"],
        )
        test_names_arr = json.dumps(list(test_names_arr))
        return test_names_arr


    @app.route("/search", methods=["POST"])
    @cross_origin(supports_credentials=True)
    def search():
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]
        limit = request.json["limit"] if "limit" in request.json else 5

        # TODO: update this so the token is retrieved in each API call like it is in confirm
        results = spotify.search(q=text, type="track", limit=limit)
        return search_result_parsing(results)


    @app.route("/confirm", methods=["POST"])
    @cross_origin(supports_credentials=True)
    def confirm():
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        spotify2 = spotipy.Spotify(auth_manager=auth_manager)
        results = spotify2.playlist_add_items("6bMWOcbmA9X1sl30boENAD", [request.json["song_uri"]])

        return "very very gooooood request", 200

    return app
