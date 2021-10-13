import os
import sys

from flask import Flask, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # accepts: query_string in JSON of request body
    # returns: id, song_title, artist, album in JSON

    @app.route('/search', methods=["GET"])
    def search():
        print(request.json, file=sys.stderr)
        text = "call me maybe"
        print(text, file=sys.stderr)
        spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

        # https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.search
        results = spotify.search(q=text, type='track', limit=3)
        for track in results['tracks']['items']:
            print(track['name'], file=sys.stderr)
            print(track['type'], file=sys.stderr)
        return results

    return app
