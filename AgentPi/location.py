##pip install geocoder
import geocoder
def getLocation(ip='me') :
    """
        get location of the pi from its ip address
    """
    myloc = geocoder.ip(ip)

    return [myloc.latlng[0],myloc.latlng[1]]

# pip install socket
import socket
def getMyIp() :
    """
        get the pi's ip address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

# If want to get IP , using getMyIp
# Call getLocation() also will return long and lat using own IP 

import requests
def getLocation2(): #More Accurate Location
    """
        improved get locaton request
    """
    URL = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + #API KEY
    param = {
        'considerIp': True,
    }
    response = requests.post(URL,param)
    response_data = response.json()
    return [response_data['location']['lat'],response_data['location']['lng']]
