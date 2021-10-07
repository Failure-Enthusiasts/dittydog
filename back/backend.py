import os
import sys

from flask import Flask, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/search')
    def search():
        # text = request.args.get['text']
        text = "call me maybe"
        print(text, file=sys.stderr)
        spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

        # https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.search
        results = spotify.search(q='song:' + text, type='track', limit=3)
        for track in results['tracks']['items']:
            print(track['name'], file=sys.stderr)
            print(track['type'], file=sys.stderr)
        return results

    return app
