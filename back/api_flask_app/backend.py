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
import helper_functions
import redis_client
import asyncio
import logging

log = logging.getLogger(__name__)

internal_playlist = []
playlist_is_running = False

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
    async def search():
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]

        spotify = helper_functions.get_spotify_api_client()
        limit = request.json["limit"] if "limit" in request.json else 5

        results = spotify.search(q=text, type="track", limit=limit)

        mycache = redis_client.RedisClient()
        await mycache.set("mykey", "myval")
        mymsg = await mycache.get("mykey")
        log.info(f'The message from REDIS IS: {mymsg}')
        print(f'The message from REDIS IS: {mymsg}', file=sys.stderr)

        return helper_functions.search_result_parsing(results["tracks"]["items"])


    @app.route("/confirm", methods=["POST"])
    def confirm():
        spotify = helper_functions.get_spotify_api_client()
        global internal_playlist
        global playlist_id
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
        helper_functions.sort_playlist(spotify, internal_playlist, playlist_id)
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
                global internal_playlist
                global playlist_is_running
                helper_functions.start_playing(internal_playlist, playlist_is_running)
                global playlist_id
                helper_functions.polling_function(internal_playlist, playlist_id)
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
        global playlist_id
        helper_functions.sort_playlist(spotify, internal_playlist, playlist_id)

        return json.dumps(internal_playlist)


    return app