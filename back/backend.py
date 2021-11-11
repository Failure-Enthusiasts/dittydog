import os
import sys
import json
from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    @app.route("/hello")
    def hello():
        # https://github.com/plamere/spotipy/blob/master/examples/app.py
        scope = "user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative"
        auth_manager = SpotifyOAuth(scope=scope, show_dialog=True)
        auth_url = auth_manager.get_authorize_url()

        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    #     curl -X POST 0.0.0.0/search -H 'Content-Type: application/json' -d '{"query_string":"freebird","limit":7}'
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

        print("CONFIRM start", file=sys.stderr)

        ####                      #######
        # Hard Coded Auth Manager call  #
        ####                      #######
        # playlist_id: 6bMWOcbmA9X1sl30boENAD
        auth_manager = spotipy.oauth2.SpotifyOAuth(
            scope="user-read-currently-playing playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative",
            # show_dialog=True,
        )
        print("CONFIRM auth_manager", file=sys.stderr)
        # auth_manager = SpotifyOAuth(scope=scope, show_dialog=True)
        # auth_url = auth_manager.get_authorize_url()

        # code: http://localhost:8080/?code=AQDQgZuzwL-DBZYjTGK3Tsqu2GxXS2wb3oJJpUky2fLaBxaSIRJjRwZGq88ouhxGimT1wfNTJ3KGSvl1asATzcYRkB5T1KIsquSErGmBHCPiiHg11Xwf7w4HcY0X0BGOFmm6rsuagoTbQgGJFtku60An-_JBEt4vxfGFPcLpCOjrlAPYXKTqtHWXIMW9wWj59A
        # song_id: 5EWPGh7jbTNO2wakv8LjUI
        auth_manager.get_access_token(
            "AQBqTtIa_sYID9yWsT5R0CAopG9a5D_ws14u-XPaywsUOF7npQ_hg9Fo1cKGnEqmHdumSnWd71N0kt_vCuj9Y2w0mTWCfiUA7laQ9I-tQVqXsXzjfKhs6adZrewl5HRvb6B1E4SwpoYBtxGgx8TcaNm8PaOmclZaHc-QvkgP5tSwwyXryIDPJyM8AFZlt1tl9G7Tj-2K6PvRuBeAi0tpnXsTnoFGfTR7W9GpConz3nqkxMUTDRlbJnDxnWXHlvpQoBX3Pr9Z_20MTkKzkNK2TbfHo1GQQdCaevvyrYRq47hW75NeJCaqzEEoXoXsRje5e9G-mTuhtz4u1HY"
        )

        print("CONFIRM access token", file=sys.stderr)
        spotify2 = spotipy.Spotify(auth_manager=auth_manager)

        print("CONFIRM spotipy2", file=sys.stderr)
        print(request.json, file=sys.stderr)
        # print(f'CONFIRM song URI: {request.json["song_uri"]}', file=sys.stderr)
        # results = spotify2.playlist_add_items(
        #     "6bMWOcbmA9X1sl30boENAD", request.json["song_uri"]
        # )
        # results = spotify2.playlist_add_items(
        #     "6bMWOcbmA9X1sl30boENAD", "spotify%3Atrack%3A5EWPGh7jbTNO2wakv8LjUI"
        # )

        results = spotify2.playlist_add_items(
            "6bMWOcbmA9X1sl30boENAD", ["1MY8GBPEOCVa2tuOWHngZc"]
        )

        # uri: spotify:track:1MY8GBPEOCVa2tuOWHngZc
        print(results, file=sys.stderr)
        return "very very gooooood request", 200

    return app
