import logging
import json

from django.http import HttpResponse, Http404
from django.shortcuts import render

from django.utils import timezone # for log

from onsen import settings
from .inference import Inference
from address.geocoding import address_to_latlng, latlng_to_address

logger = logging.getLogger('dev')

def render_json(request, data, status=None):
    json_str = json.dumps(data, indent=2)
    return HttpResponse(json_str,
                        content_type='application/json; charset=utf-8',
                        status=status)

def inference(request):
    name = request.GET.get('name')
    if name is None or len(name) < 3:
        raise Http404
    
    infer = Inference(settings.ADDRESS_CSV,
                      settings.ADDRESS_EXCLUDE_LIST,
                      settings.BING_CLIENT_ID,
                      settings.BING_ACCOUNT_KEY, logger=logger)
    logger.info('start inference now={}'.format(timezone.now()))
    addresses= infer.address_of(name)
    logger.info('end inference now={}'.format(timezone.now()))
    data = [ { "address": address.get_address(), "confidence": confidence }
             for address, confidence in addresses ]
    return render_json(request, data)

def get_latlng(request):
    address = request.GET.get('address')
    logger.debug('address={}'.format(address))
    if address is None or len(address) < 3:
        raise Http404

    latlng = address_to_latlng(address, logger=logger)
    if latlng is None:
        latlng = {}
    return render_json(request, latlng)

def get_address(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    logger.debug('latitude={}, longitude={}'.format(latitude, longitude))
    if latitude is None or longitude is None:
        raise Http404

    address = latlng_to_address(latitude, longitude, logger=logger)
    if address is None:
        address = {}
    return render_json(request, address)
