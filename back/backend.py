import os
import sys
import json
from flask import Flask, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # accepts: query_string in JSON of request body
    # returns: id, song_title, artist, album in JSON

#     curl -X POST 0.0.0.0/search -H 'Content-Type: application/json' -d '{"query_string":"freebird","limit":7}'
    def search_result_parsing(results):
        test_names_arr = map(
                            lambda x: {
                                "song_name": x["name"],
                                "song_id": x["id"],
                                "album_name": x["album"]["name"],
                                "artist_name": x["artists"][0]["name"],
                                "duration": x["duration_ms"],
                                "img_link": x["album"]["images"][0]["url"]
                            },
                            results["tracks"]["items"]
                         )
        test_names_arr = json.dumps(list(test_names_arr))
        print(test_names_arr, file=sys.stderr)
        return test_names_arr

    @app.route("/search", methods=["POST"])
    def search():
        print(request.json, file=sys.stderr)
        if "query_string" not in request.json or request.json["query_string"] == "":
            return 'bad request!', 400
        else:
            text = request.json["query_string"]
        limit = request.json["limit"] if "limit" in request.json else 5
        print(text, file=sys.stderr)
        print("limit: " + str(limit))
        spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

        # https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.search
        results = spotify.search(q=text, type="track", limit=limit)
        return search_result_parsing(results)

    return app



