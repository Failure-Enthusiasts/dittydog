import json
import sys
import os
from flask import session
import spotipy


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

def get_spotify_api_client():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/') # TODO: find a way to tell the front end that it needs to refresh the token. We don't think this works as is
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify

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
            "vote_count": 0,
            "locked": False
        },
        results,
    )
    test_names_arr = list(test_names_arr)
    return test_names_arr

def update_song_vote(internal_playlist, ind, dir):
    internal_playlist[ind]['vote_count'] += 1 if (dir == 'up') else -1
    return internal_playlist

def find_index(internal_playlist, song_uri):
    for i in range(len(internal_playlist)):
        if internal_playlist[i]["song_uri"] == song_uri:
            return i
    return None

def build_internal_playlist(internal_playlist):
    ## TODO: add functionality to build a new playlist or select exisiting playlist
    spotify = get_spotify_api_client()
    playlist_id = spotify.user_playlist_create(spotify.current_user()["id"], f'{spotify.current_user()["display_name"]}, USE THE DITTYDOG APP TO ADD SONGS, YOU FOOL!', public=True, collaborative=False, description='')["uri"]
    results = spotify.playlist_tracks(playlist_id)
    playlist_id_only = playlist_id.split(':')[2]
    print(f'Playlist URL: https://open.spotify.com/playlist/{playlist_id_only}', file=sys.stderr)
    internal_playlist = playlist_parsing(results["items"])
    print('\nINTERNAL PLAYLIST\n\n:' + str(results), file=sys.stderr)
    return internal_playlist, playlist_id_only