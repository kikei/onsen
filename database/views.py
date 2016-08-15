import json

from django.template import loader
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from django.shortcuts import render, get_object_or_404

from .models import EntryPoint, Onsen

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'entry_point_list'

    def get_queryset(self):
        return [
            EntryPoint(name='札幌市',latitude=43.06417,longitude=141.34694),
            EntryPoint(name='青森市',latitude=40.82444,longitude=140.74),
            EntryPoint(name='盛岡市',latitude=39.70361,longitude=141.1525),
            EntryPoint(name='仙台市',latitude=38.26889,longitude=140.87194),
            EntryPoint(name='秋田市',latitude=39.71861,longitude=140.1025),
            EntryPoint(name='山形市',latitude=38.24056,longitude=140.36333),
            EntryPoint(name='福島市',latitude=37.75,longitude=140.46778),
            EntryPoint(name='水戸市',latitude=36.34139,longitude=140.44667),
            EntryPoint(name='宇都宮市',latitude=36.56583,longitude=139.88361),
            EntryPoint(name='前橋市',latitude=36.39111,longitude=139.06083),
            EntryPoint(name='さいたま市',latitude=35.85694,longitude=139.64889),
            EntryPoint(name='千葉市',latitude=35.60472,longitude=140.12333),
            EntryPoint(name='新宿区',latitude=35.68944,longitude=139.69167),
            EntryPoint(name='横浜市',latitude=35.44778,longitude=139.6425),
            EntryPoint(name='新潟市',latitude=37.90222,longitude=139.02361),
            EntryPoint(name='富山市',latitude=36.69528,longitude=137.21139),
            EntryPoint(name='金沢市',latitude=36.59444,longitude=136.62556),
            EntryPoint(name='福井市',latitude=36.06528,longitude=136.22194),
            EntryPoint(name='甲府市',latitude=35.66389,longitude=138.56833),
            EntryPoint(name='長野市',latitude=36.65139,longitude=138.18111),
            EntryPoint(name='岐阜市',latitude=35.39111,longitude=136.72222),
            EntryPoint(name='静岡市',latitude=34.97694,longitude=138.38306),
            EntryPoint(name='名古屋市',latitude=35.18028,longitude=136.90667),
            EntryPoint(name='津市',latitude=34.73028,longitude=136.50861),
            EntryPoint(name='大津市',latitude=35.00444,longitude=135.86833),
            EntryPoint(name='京都市',latitude=35.02139,longitude=135.75556),
            EntryPoint(name='大阪市',latitude=34.68639,longitude=135.52),
            EntryPoint(name='神戸市',latitude=34.69139,longitude=135.18306),
            EntryPoint(name='奈良市',latitude=34.68528,longitude=135.83278),
            EntryPoint(name='和歌山市',latitude=34.22611,longitude=135.1675),
            EntryPoint(name='鳥取市',latitude=35.50361,longitude=134.23833),
            EntryPoint(name='松江市',latitude=35.47222,longitude=133.05056),
            EntryPoint(name='岡山市',latitude=34.66167,longitude=133.935),
            EntryPoint(name='広島市',latitude=34.39639,longitude=132.45944),
            EntryPoint(name='山口市',latitude=34.18583,longitude=131.47139),
            EntryPoint(name='徳島市',latitude=34.06583,longitude=134.55944),
            EntryPoint(name='高松市',latitude=34.34028,longitude=134.04333),
            EntryPoint(name='松山市',latitude=33.84167,longitude=132.76611),
            EntryPoint(name='高知市',latitude=33.55972,longitude=133.53111),
            EntryPoint(name='福岡市',latitude=33.60639,longitude=130.41806),
            EntryPoint(name='佐賀市',latitude=33.24944,longitude=130.29889),
            EntryPoint(name='長崎市',latitude=32.74472,longitude=129.87361),
            EntryPoint(name='熊本市',latitude=32.78972,longitude=130.74167),
            EntryPoint(name='大分市',latitude=33.23806,longitude=131.6125),
            EntryPoint(name='宮崎市',latitude=31.91111,longitude=131.42389),
            EntryPoint(name='鹿児島市',latitude=31.56028,longitude=130.55806),
            EntryPoint(name='那覇市',latitude=26.2125,longitude=127.68111),
        ]

# class DetailView(generic.DetailView):
#     model = Question
#     template_name = 'polls/detail.html'

# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'

from django.forms import Form
class MapWidget(Form):
    class Media:
        js = ( 'js/map_widget.js', )

class OnsenFormWidget(Form):
    class Media:
        js = ( 'js/onsen_form.js', )

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import *
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

def search(request):
    name = request.GET.get('name')
    onsens = Onsen.objects.filter(name__contains=name)
    start = 0
    end = 20
    count = len(onsens)
    return render(request, 'search.html', {
        'map_widget': MapWidget(),
        'onsen_list': onsens,
        'search': { 'start': start, 'end': end, 'count': count }
    })
    
def search_nearby(request):
    pass

def search_by_location(request, latitude, longitude):
    location = GEOSGeometry('Point({} {})'.format(longitude, latitude), srid=4326)
    onsens = Onsen.objects.annotate(distance=Distance('location', location)).order_by('distance')
    start = 0
    end = 20
    count = len(onsens)
    return render(request, 'search.html', {
        'map_widget': MapWidget(),
        'onsen_list': onsens,
        'search': { 'start': start, 'end': end, 'count': count }
    })

def mapview(request, latitude, longitude):
    return render(request, 'map_view.html', {
        'map_widget': MapWidget(),
        'latitude': latitude,
        'longitude': longitude,
    })

def render_json(request, data, status=None):
    json_str = json.dumps(data, indent=2)
    return HttpResponse(json_str,
                        content_type='application/json; charset=utf-8',
                        status=status)

def onsen_list(request):
    name   = request.GET.get('name')
    center = request.GET.get('center')
    radius = request.GET.get('zoom')

    if name is not None:
        onsens = Onsen.objects.filter(name__contains=name)
    elif center is not None and radus is not None:
        onsens = Onsen.objects.annotate(distance=Distance('location', center)).order_by('distance')
    else:
        onsens = Onsen.objects.all()
    data = list(map(lambda a: a.to_json(), onsens))
    return render_json(request, data)

def onsen_detail(request, onsen_id):
    onsen = get_object_or_404(Onsen, pk=onsen_id)
    return render(request, 'onsen_detail.html', {
        'map_widget': MapWidget(),
        'onsen': onsen,
    })

from address import geocoding

def onsen_entry_form(request):
    return render(request, 'entry_form.html', {
        'map_widget' : MapWidget(),
    })

def onsen_form(request):
    onsen_id = request.GET.get('id')
    if onsen_id is not None:
        onsen = get_object_or_404(Onsen, pk=onsen_id)
    else:
        onsen = Onsen.from_query(request.GET)
        if onsen.address is None and \
           onsen.latitude is not None and \
           onsen.longitude is not None:
            onsen.address = geocoding.latlng_to_address(onsen.latitude,
                                                        onsen.longitude)
    return render(request, 'onsen_form.html', {
        'form_widget' : OnsenFormWidget(),
        'onsen'       : onsen
    })

def onsen_post(request):
    if request.POST.get('name') is None or request.POST.get('address') is None:
        raise Http404

    if request.POST.get('id') is None:
        onsen = Onsen.from_query(request.POST)
        latlng = geocoding.address_to_latlng(onsen.address)
        onsen.set_location(latlng['latitude'], latlng['longitude'])
    else:
        onsen = get_object_or_404(Onsen, pk=request.POST.get('id'))
        address0 = onsen.address
        onsen.update_by(request.POST)
        if address0 != onsen.address:
            latlng = geocoding.address_to_latlng(onsen.address)
            onsen.set_location(latlng['latitude'], latlng['longitude'])
    onsen.save()
    to = reverse('database:onsen_detail', args=[onsen.id])
    return HttpResponseRedirect(to)
    
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
