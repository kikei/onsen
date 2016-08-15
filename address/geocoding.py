import logging
import requests

from onsen import settings

def normalize_decimal(t):
    t = t.replace(u"０", "0")
    t = t.replace(u"１", "1")
    t = t.replace(u"２", "2")
    t = t.replace(u"３", "3")
    t = t.replace(u"４", "4")
    t = t.replace(u"５", "5")
    t = t.replace(u"６", "6")
    t = t.replace(u"７", "7")
    t = t.replace(u"８", "8")
    t = t.replace(u"９", "9")
    t = t.replace(u"ー", "-")
    t = t.replace(u"　", " ")
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

    BASEURL = 'https://maps.googleapis.com/maps/api/geocode/json'

    params = {
        'latlng': "{},{}".format(latitude, longitude),
        'key': settings.GOOGLE_GEOCODING_KEY,
        'language': 'ja'
    }
    headers = {
        'User-Agent': settings.API_USER_AGENT
    }
    response = requests.get(BASEURL, params=params, headers=headers)
    
    result = response.json()
    address_ = result['results'][0]['formatted_address']

    # Skip contry name and postal code.
    address = ' '.join(address_.split(' ')[2:])
    
    address = normalize_decimal(address)
    
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

    BASEURL = 'https://maps.googleapis.com/maps/api/geocode/json'
    
    params = {
        'address': address,
        'key': settings.GOOGLE_GEOCODING_KEY,
        'language': 'ja'
    }
    headers = {
        'User-Agent': settings.API_USER_AGENT
    }
    
    response = requests.get(BASEURL, params=params, headers=headers)
    
    result = response.json()
    if len(result['results']) == 0:
        logger.error('results empty result={}'.format(result))
        return None
        
    location = result['results'][0]['geometry']['location']
    
    return { 'latitude': location['lat'],
             'longitude': location['lng'] }
