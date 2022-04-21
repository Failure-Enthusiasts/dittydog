import time
import sys
import logging
import requests


i = 0

while True:
    # API request to 
    time.sleep(9)
    i += 9
    print(f"ITS BEeN {i} SeCoNdS")
    # r = requests.post('http://spotify-backend:80/polling_and_pruning') #might not need port
    # r = requests.post('spotify-backend/polling_and_pruning') #might not need port
    # r = requests.post('http://spotify-backend/polling_and_pruning') #might not need port
    # r = requests.post('spotify-backend://localhost:80/polling_and_pruning') #might not need port

    # FIXME: 4/20 - next week, figure out the right address to hit the other container
        # try this: dittydog-backend
        
    # redis://localhost:6379
    print(f"The response: {r.json()}")
    
    #  http://spotify-backend/polling_and_pruning

