import helper_functions
import json
import redis

mycache = redis.Redis(host='redis', port=6379, db=0)


def get_cache_playlist(mycache):
    playlist_obj = json.loads(mycache.get(helper_functions.session_db_path('playlist')))
    return playlist_obj

def get_specific_cache_playlist(mycache, session):
    playlist_obj = mycache.get(helper_functions.specify_session_db_path('playlist', session))
    if playlist_obj is not None:
        return json.loads(playlist_obj)
    return playlist_obj


def set_cache_playlist(mycache, playlist_obj):
    mycache.set(helper_functions.session_db_path('playlist'), json.dumps(playlist_obj))
