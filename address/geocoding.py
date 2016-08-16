import json
import logging
import urllib.parse
import urllib.request

from onsen import settings

def normalize_address(t):
    t = t.replace("０", "0")
    t = t.replace("１", "1")
    t = t.replace("２", "2")
    t = t.replace("３", "3")
    t = t.replace("４", "4")
    t = t.replace("５", "5")
    t = t.replace("６", "6")
    t = t.replace("７", "7")
    t = t.replace("８", "8")
    t = t.replace("９", "9")
    t = t.replace("ー", "-")
    t = t.replace("　", " ")
    t = t.replace("丁目", "-")
    t = t.replace("番地", "-")
    return t

def latlng_to_address(latitude, longitude, logger=None):
    """
    Convert geolocation of latitude and longitude to address
    by using Google Maps Reverse Geocoding API.
    Refer: 
    https://developers.google.com/maps/documentation/geocoding/intro#ReverseGeocoding
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    BASEURL = 'https://maps.googleapis.com/maps/api/geocode/json?{}'

    query = urllib.parse.urlencode({
        'latlng': "{},{}".format(latitude, longitude),
        'key': settings.GOOGLE_GEOCODING_KEY,
        'language': 'ja'
    })
    req = urllib.request.Request(BASEURL.format(query))
    f = urllib.request.urlopen(req)
    content = f.read().decode('utf-8')
    result = json.loads(content)
    address_ = result['results'][0]['formatted_address']

    # Skip contry name and postal code.
    address = ' '.join(address_.split(' ')[2:])
    
    address = normalize_address(address)
    
    return address

def address_to_latlng(address, logger=None):
    """
    Convert address to geolocation of latitude and longitude
    by using Google Maps Geocoding API.
    Refer:
    https://developers.google.com/maps/documentation/geocoding/intro#geocoding
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    BASEURL = 'https://maps.googleapis.com/maps/api/geocode/json?{}'
    
    query = urllib.parse.urlencode({
        'address': address,
        'key': settings.GOOGLE_GEOCODING_KEY,
        'language': 'ja'
    })
    req = urllib.request.Request(BASEURL.format(query))
    f = urllib.request.urlopen(req)
    content = f.read().decode('utf-8')
    result = json.loads(content)
    if len(result['results']) == 0:
        logger.error('results empty result={}'.format(result))
        return None
        
    location = result['results'][0]['geometry']['location']
    
    return { 'latitude': location['lat'],
             'longitude': location['lng'] }
