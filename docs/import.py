from database.models import Onsen
import json
from django.utils import timezone

content = open("docs/points.json").read()
contents = content.split("\n")
contents = list(filter(lambda x: x != "", contents))
jsons = list(map(json.loads, contents))

def extract_char(c):
    return c[c.find("泉質：")+3:]

mi = '未登録'

for j in jsons:
    name = j["name"]
    address = j["address"]
    character = extract_char(j["description"])
    latitude = j["location"][0]
    longitude = j["location"][1]
    onsen = Onsen(name=name, tel=mi, address=address, traffic=mi, business_hours=mi, holiday=mi, daytrip=mi, price=mi, character=character, indoor=mi, outdoor=mi, parking=mi, website=mi, note=mi, latitude=latitude, longitude=longitude, publish_date=timezone.now(), modified_date=timezone.now())
    onsen.save()
