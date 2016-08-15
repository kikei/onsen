import datetime

from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.utils import timezone
from django.contrib.gis.db import models

class EntryPoint(models.Model):
    name = models.CharField(max_length=16)
    latitude = models.FloatField()
    longitude = models.FloatField()

class Onsen(models.Model):
    name           = models.CharField(max_length=128)
    tel            = models.CharField(max_length=128, default='未登録')
    address        = models.CharField(max_length=256, default='未登録')
    traffic        = models.CharField(max_length=256, default='未登録')
    stay           = models.CharField(max_length=128, default='未登録')
    holiday        = models.CharField(max_length=64, default='未登録')
    daytrip        = models.CharField(max_length=128, default='未登録')
    price          = models.CharField(max_length=128, default='未登録')
    character      = models.CharField(max_length=64, default='未登録')
    indoor         = models.CharField(max_length=16, default='未登録')
    outdoor        = models.CharField(max_length=16, default='未登録')
    parking        = models.CharField(max_length=128, default='未登録')
    website        = models.CharField(max_length=256, default='未登録')
    amenity        = models.CharField(max_length=128, default='未登録')
    note           = models.CharField(max_length=1024, default='未登録')
    latitude       = models.FloatField()
    longitude      = models.FloatField()
    publish_date   = models.DateTimeField('date published')
    modified_date  = models.DateTimeField('date modified')
    location       = models.PointField(null=True, srid=4326)

    def is_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.publish_date <= now

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id"             : self.id,
            "name"           : self.name,
            "tel"            : self.tel,
            "address"        : self.address,
            "traffic"        : self.traffic,
            "stay"           : self.stay,
            "holiday"        : self.holiday,
            "daytrip"        : self.daytrip,
            "price"          : self.price,
            "character"      : self.character,
            "indoor"         : self.indoor,
            "outdoor"        : self.outdoor,
            "parking"        : self.parking,
            "website"        : self.website,
            "amenity"        : self.amenity,
            "note"           : self.note,
            "latitude"       : self.latitude,
            "longitude"      : self.longitude,
            "publish_date"   : self.publish_date.isoformat(),
            "modified_date"  : self.modified_date.isoformat()
        }

    def from_query(query):
        now = timezone.now()
        onsen = Onsen(name=query.get('name'),
                      address=normalize_decimal(query.get('address')),
                      tel=normalize_decimal(query.get('tel')),
                      traffic=normalize_decimal(query.get('traffic')),
                      stay=query.get('stay'),
                      holiday=normalize_decimal(query.get('holiday')),
                      daytrip=normalize_decimal(query.get('daytrip')),
                      price=normalize_decimal(query.get('price')),
                      character=query.get('character'),
                      indoor=query.get('indoor'),
                      outdoor=query.get('outdoor'),
                      parking=query.get('parking'),
                      website=query.get('website'),
                      amenity=query.get('amenity'),
                      note=query.get('note'),
                      latitude=query.get('latitude'),
                      longitude=query.get('longitude'),
                      publish_date=now,
                      modified_date=now)
        return onsen
    
    def update_by(self, query):
        for name in [ 'name', 'address', 'tel', 'traffic', 'stay',
                      'holiday', 'daytrip', 'price', 'character', 'indoor',
                      'outdoor', 'parking', 'website', 'amenity', 'note',
                      'latitude', 'longitude' ]:
            v = query.get(name)
            if v is not None:
                setattr(self, name, v)
        self.modified_date = timezone.now()
    
    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.location = GEOSGeometry('POINT({} {})'.format(longitude, latitude),
                                     srid=4326)


def normalize_decimal(t):
    if t is not None:
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
        t = t.replace(u"：", ":")
    return t
