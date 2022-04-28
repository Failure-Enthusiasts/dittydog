import time
import sys
import logging
import requests


i = 0

while True:
    # API request to 
    
    i += 9
    print(f"ITS BEeN {i} SeCoNdS")
    time.sleep(9)
    r = requests.post('http://dittydog-backend:8080/polling_and_pruning')
    print(f"The response: {r.json()}")
    
    #  http://spotify-backend/polling_and_pruning

