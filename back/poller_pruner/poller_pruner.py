import time
import sys
import logging
import requests

# new
import os
import sys
import json
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
from flask_cors import CORS
import uuid


# ported over all the pruning/polling functions
# 1) Make sure old code works with all of this removed
# 2) Instead of passing session ID, need to make these take spotify as an object, built in old code, passed as object here
#   - make sure these functions don't break because of that
# 3) Test this code
# 4) Pass internal playlist across, and have old code send internal playlist here when updated
#  - When this code locks something, send update to old code. Later, REDIS
# 5) Make this a flask interface
#  - create the flask app here
# 6) Replace polling and pruning in old code with polling_and_pruning_outsourced, make sure it triggers at right time
# 7) Later, REDIS instead of passing internal playlist
# 8) Drop playlist_is_running from old code
# 9) Which of these functions are routes? Correct decorators?


# need playlist
internal_playlist = []
playlist_is_running = False

    @app.route("/polling_and_pruning", methods=["POST"])
    def polling_and_pruning():
        # start_playing()
        # polling_function()
        return json.dumps({'message':'Hello Im polling_and_pruning'})

    def start_playing():

        # once 5 votes are on one song, and there are 5 songs in the list, start
        # will be called in VOTE and CONFIRM endpoints
        global internal_playlist
        global playlist_is_running

        if playlist_is_running == False:
            vote_max = 0
            for song in internal_playlist:
                vote_max = max(song['vote_count'], vote_max)


            if len(internal_playlist) > 4 and vote_max > 4:
                playlist_is_running = True
                # Spotify API call to start playlist running
                spotify = get_spotify_api_client()
                try:
                    spotify.start_playback(context_uri="6bMWOcbmA9X1sl30boENAD")
                except:
                    print("Need premium", file=sys.stderr)
                # lock the first song
                if internal_playlist is not None:
                    internal_playlist[0]['locked'] = True

    def get_spotify_api_client():
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/') # TODO: find a way to tell the front end that it needs to refresh the token. We don't think this works as is
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        return spotify

    def polling_function():
        playing_song = playing_song_status()
        ## if none return
        print(playing_song, file=sys.stderr)

        if playing_song:
            # freeze upcoming song
                # check conditions - more than 50% done, OR duration left is less than 30 seconds, or...
            if playing_song['half_played'] or playing_song['time_remaining'] < 30000:
                upcoming_song_id = freeze_upcoming_song()
                
                # needs to be tested
                enqueued_songs = [playing_song['song_uri'], upcoming_song_id]
                
                # trigger the "delete played songs" action
                prune(enqueued_songs)

    def playing_song_status():
        spotify = get_spotify_api_client() #FIXME: replace with spotify PASS to this function from main code
        current_song = spotify.currently_playing(market=None, additional_types=None)
        # print("CURRENTLY PLAYING:\n" + str(current_song), file=sys.stderr)

        if not current_song:
            return
        playing_song = {}
        # current_song
        playing_song['song_uri'] = current_song['item']['uri']

        # current playing?
        playing_song['is_playing'] = current_song['is_playing']

        # time remaining?
        playing_song['time_remaining'] = current_song['item']['duration_ms'] - current_song['progress_ms']
        playing_song['half_played'] = 0.5 < (current_song['progress_ms'] / current_song['item']['duration_ms'])
        
        return playing_song

    def freeze_upcoming_song():
        global internal_playlist
        # internal_playlist[0]['locked'] = True
        internal_playlist[1]['locked'] = True
        # internal_playlist[2]['locked'] = True
        return internal_playlist[1]['song_uri']


    # any song containing the `locked` attribute that isn't currently playing or upcoming_song is removed from internal_playlist (assuming that these have already been played)
    def prune(enqueued_songs):
        print(str(enqueued_songs), file=sys.stderr)
        spotify = get_spotify_api_client()
        prune_these = []
        global internal_playlist
        for song in internal_playlist:
            if song['locked'] and song['song_uri'] not in enqueued_songs:
                prune_these.append(song['song_uri'])
                internal_playlist.remove(song)
        if len(prune_these) != 0:
            print('PRUNING', file=sys.stderr)
            spotify = get_spotify_api_client()
            spotify.playlist_remove_all_occurrences_of_items("6bMWOcbmA9X1sl30boENAD", prune_these)


i = 0



while True:
    # API request to 
    
    i += 9
    print(f"ITS BEeN {i} SeCoNdS")
    time.sleep(9)
    r = requests.post('http://dittydog-backend:8080/polling_and_pruning')
    print(f"The response: {r.json()}")
    
    #  http://spotify-backend/polling_and_pruning



