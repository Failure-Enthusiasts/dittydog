import os
import sys
import json
from flask import Flask, session, request, redirect, copy_current_request_context, url_for
from flask_session import Session
import spotipy
from flask_cors import CORS
import uuid
from time import sleep
from threading import Thread
from datetime import datetime
import helper_functions
import logging
from redis_helper import get_cache_playlist, set_cache_playlist, mycache, get_specific_cache_playlist 

log = logging.getLogger(__name__)

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './.flask_session/'
    Session(app)
    ## this doesn't work -- how do we share the Redis client across routes?
    # mycache = redis_client.RedisClient()


    @app.route('/')
    def index():
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            log.info("route /, step 1")
            session['uuid'] = str(uuid.uuid4())
            print(f"login456 session is {session} in step 1 if", file=sys.stderr)
        else:
            print("in / else", file=sys.stderr)
            print(f"login456 session is {session}", file=sys.stderr)

        cache_handler = spotipy.cache_handler.RedisCacheHandler(redis=mycache, key=helper_functions.session_db_path('token'))
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private', cache_handler=cache_handler, show_dialog=True)

        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            log.info("route /, step 3")
            auth_manager.get_access_token(request.args.get("code"))
            print(f"login456 session is {session} in step 3", file=sys.stderr)
            return redirect(f'http://localhost:8080/')


        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            log.info("route /, step 2")
            print(f"login456 session is {session} in step 2", file=sys.stderr)
            auth_url = auth_manager.get_authorize_url()
            return f'<h2><a href="{auth_url}">Sign in</a></h2>'

        #  logic to check if there's a playlist that corresponds to the session ID
        playlist_obj = get_specific_cache_playlist(mycache, session.get('uuid'))
        if playlist_obj is not None:
            print(f"login456 session already exists pulling the ID", file=sys.stderr)
            playlist_id = playlist_obj['playlist_id']
        else:
            internal_playlist, playlist_id = helper_functions.build_internal_playlist()
            playlist_obj = {
                "playlist": internal_playlist, 
                "playlist_id": playlist_id,
                "playlist_is_running": False
            }
            set_cache_playlist(mycache, playlist_obj)

        # Step 4. Signed in, display data
        log.info("route /, step 4")
        print(f"login456 session is {session} in step 4", file=sys.stderr)
        return redirect(f'http://localhost/playlist?playlist_id={playlist_id}&session_id={session["uuid"]}')

    @app.route("/get_login_url", methods=["GET"])
    def get_login_url():
        if not session.get('uuid'):
            print("in get_login_url if not", file=sys.stderr)
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())
            print(session['uuid'], file=sys.stderr)
            print("in get_login_url if not -here's the session_id get", file=sys.stderr)
            print(session.get('uuid'), file=sys.stderr)
        else:
            print("in get_login_url else", file=sys.stderr)
            playlist_obj = get_specific_cache_playlist(mycache, session.get('uuid'))
            return json.dumps({'playlist_id': playlist_obj['playlist_id'], 'session_id': session.get('uuid')}), 200, {'ContentType':'application/json'}
        cache_handler = spotipy.cache_handler.RedisCacheHandler(redis=mycache, key=helper_functions.session_db_path('token'))
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private', cache_handler=cache_handler, show_dialog=True)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
        print(f"THIS IS THE AUTH_URL: {auth_url}", file=sys.stderr)
        return auth_url

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
        # global internal_playlist
        # global playlist_id
        playlist_obj = get_cache_playlist(mycache)
        playlist_id = playlist_obj["playlist_id"]
        internal_playlist = playlist_obj["playlist"]
        print("playlist from cache", file=sys.stderr)
        print(playlist_obj, file=sys.stderr)
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
        playlist_obj["playlist"] = internal_playlist
        set_cache_playlist(mycache, playlist_obj)
        return json.dumps(internal_playlist)


    @app.route("/get_playlist", methods=["GET"])
    def get_playlist():
        playlist_obj = get_cache_playlist(mycache)
        internal_playlist = playlist_obj["playlist"]
        return json.dumps(internal_playlist)


    @app.route("/polling_and_pruning", methods=["POST"])
    def polling_and_pruning():
        @copy_current_request_context
        def background_task():
            while True:
                print(datetime.now(), file=sys.stderr)
                sys.stderr.flush()
                playlist_obj = get_cache_playlist(mycache)
                internal_playlist = playlist_obj["playlist"]
                playlist_id = playlist_obj["playlist_id"]
                playlist_is_running = playlist_obj["playlist_is_running"]
                internal_playlist, playlist_is_running = helper_functions.start_playing(internal_playlist, playlist_is_running)
                internal_playlist = helper_functions.polling_function(internal_playlist, playlist_id)
                playlist_obj = {'playlist': internal_playlist, 'playlist_id': playlist_id, 'playlist_is_running': playlist_is_running}
                set_cache_playlist(mycache, playlist_obj)
                sleep(10)
        thread = Thread(target=background_task)
        thread.daemon = True
        thread.start()

        return json.dumps({'message': 'started polling and pruning'})


    # vote endpoint expects a json object with 2 attributes `vote_direction` and `song_uri`
    @app.route("/vote", methods=["POST"])
    def vote():
        # global internal_playlist
        playlist_obj = get_cache_playlist(mycache)
        internal_playlist = playlist_obj["playlist"]
        playlist_id = playlist_obj["playlist_id"]
        target_index = helper_functions.find_index(internal_playlist, request.json["song_uri"])
        internal_playlist = helper_functions.update_song_vote(internal_playlist, target_index, request.json["vote_direction"])

        spotify = helper_functions.get_spotify_api_client()
        # global playlist_id
        helper_functions.sort_playlist(spotify, internal_playlist, playlist_id)
        playlist_obj["playlist"] = internal_playlist 
        set_cache_playlist(mycache, playlist_obj)

        return json.dumps(internal_playlist)
    
    @app.route("/get_playlist_id", methods=["POST"])
    def get_playlist_id():
        session['uuid'] = request.json["query_string"]
        print(f'request is: {request.json["query_string"]}', file=sys.stderr)
        playlist_obj = get_specific_cache_playlist(mycache, request.json["query_string"])
        # TODO: return the playlistID and the session ID
        # return json.dumps({'playlist_id':playlist_obj["playlist_id"]}), 200, {'ContentType':'application/json'}
        if playlist_obj is None:
            json.dumps({'error': 'playlist not found'}), 404, {'ContentType':'application/json'}
        return json.dumps({'playlist_id': playlist_obj['playlist_id']}), 200, {'ContentType':'application/json'}
    return app
