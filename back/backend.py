import os
import sys
import json
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from flask_cors import CORS
import uuid

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    print(caches_folder + session.get('uuid'), file=sys.stderr)
    return caches_folder + session.get('uuid')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './.flask_session/'
    Session(app)
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials())

#    @app.route("/hello")
#    def hello():
#        # https://github.com/plamere/spotipy/blob/master/examples/app.py
#        scope = "user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative"
#        auth_manager = SpotifyOAuth(scope=scope, show_dialog=True)
#        auth_url = auth_manager.get_authorize_url()
#
#        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    #     curl -X POST 0.0.0.0/search -H 'Content-Type: application/json' -d '{"query_string":"freebird","limit":7}'

    @app.route('/')
    def index():
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())

        cache_handler = spotipy.cache_handler.CacheFileHandler(
            cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private',
                                                   cache_handler=cache_handler,
                                                   show_dialog=True)
        print("1", file=sys.stderr)
        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            print(request.args.get("code"), file=sys.stderr)
            auth_manager.get_access_token(request.args.get("code"))
            return redirect('/')

        print("2", file=sys.stderr)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            return f'<h2><a href="{auth_url}">Sign in</a></h2>'

        print("3", file=sys.stderr)
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
        print(test_names_arr, file=sys.stderr)
        return test_names_arr

    @app.route("/search", methods=["POST"])
    def search():
        print(request.json, file=sys.stderr)
        if "query_string" not in request.json or request.json["query_string"] == "":
            return "bad request!", 400
        else:
            text = request.json["query_string"]
        limit = request.json["limit"] if "limit" in request.json else 5
        print(text, file=sys.stderr)
        print("limit: " + str(limit))

        results = spotify.search(q=text, type="track", limit=limit)
        return search_result_parsing(results)

    @app.route("/confirm", methods=["POST"])
    def confirm():

        #        print("CONFIRM start", file=sys.stderr)
        #
        #        ####                      #######
        #        # Hard Coded Auth Manager call  #
        #        ####                      #######
        #        # playlist_id: 6bMWOcbmA9X1sl30boENAD
        #        auth_manager = spotipy.oauth2.SpotifyOAuth(
        #            scope="user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative",
        #            # show_dialog=True,
        #        )
        #        print("CONFIRM auth_manager", file=sys.stderr)
        #        # auth_manager = SpotifyOAuth(scope=scope, show_dialog=True)
        #        # auth_url = auth_manager.get_authorize_url()
        #
        #        # code: http://localhost:8080/?code=AQDQgZuzwL-DBZYjTGK3Tsqu2GxXS2wb3oJJpUky2fLaBxaSIRJjRwZGq88ouhxGimT1wfNTJ3KGSvl1asATzcYRkB5T1KIsquSErGmBHCPiiHg11Xwf7w4HcY0X0BGOFmm6rsuagoTbQgGJFtku60An-_JBEt4vxfGFPcLpCOjrlAPYXKTqtHWXIMW9wWj59A
        #        # song_id: 5EWPGh7jbTNO2wakv8LjUI
        #        auth_manager.get_access_token(
        #            "AQDM8VU4LOI1HP4zjjVvQj29LnIECvW3EDaEObFcpIsWKKOPO57O_gUWG-ISUT3ra5lPsXa7CjGFTFdq7ZcAG6vyeymCER_DofV3kt_V6AHAoJ6YOVOXJZpCVLpbvmnPHk9netrwOP13BI6r1ydF555vsPZ0WXE4qLlP816I_MF0NbZ8BUthUnYS0qjiTsJfU_ucp7R0h_PVlvF6TC1ad9MjK78qzsQ_VZ1gMeRf-weO-gHsN8ReuPeby-Vv4JBAy7znwoioL8cxpt11qVzl-69TdCs4icMz8R4fkk123YtMeAQpsMReSDRCaSKidKULwFQThNBRjIpQRTA"
        #        )
        #
        #        print("CONFIRM access token", file=sys.stderr)
        #        spotify2 = spotipy.Spotify(auth_manager=auth_manager)
        #
        #        print("CONFIRM spotipy2", file=sys.stderr)
        #        print(request.json, file=sys.stderr)
        # print(f'CONFIRM song URI: {request.json["song_uri"]}', file=sys.stderr)
        # results = spotify2.playlist_add_items(
        #     "6bMWOcbmA9X1sl30boENAD", request.json["song_uri"]
        # )
        # results = spotify2.playlist_add_items(
        #     "6bMWOcbmA9X1sl30boENAD", "spotify%3Atrack%3A5EWPGh7jbTNO2wakv8LjUI"
        # )

        # uri: spotify:track:1MY8GBPEOCVa2tuOWHngZc
        print("1", file=sys.stderr)
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        print("2", file=sys.stderr)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        print("3", file=sys.stderr)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        print("4", file=sys.stderr)
        spotify2 = spotipy.Spotify(auth_manager=auth_manager)
        print("5", file=sys.stderr)
        results = spotify2.playlist_add_items(
            "6bMWOcbmA9X1sl30boENAD", ["1MY8GBPEOCVa2tuOWHngZc"]
        )
        print(results, file=sys.stderr)

        return "very very gooooood request", 200

    return app
