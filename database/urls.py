from django.conf.urls import url

from . import views

app_name = 'database'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^onsen/(?P<onsen_id>[0-9]+)$', views.onsen_detail, name='onsen_detail'),
    url(r'^onsen/map/(?P<latitude>[0-9]*\.[0-9]*),(?P<longitude>[0-9]*\.[0-9]*)$',
        views.mapview, name='map'),
    url(r'^onsen/search$', views.search, name="search"),
    url(r'^onsen/search/nearby$', views.search_nearby, name="search_nearby"),
    url(r'^onsen/search/(?P<latitude>[0-9]*\.[0-9]*),(?P<longitude>[0-9]*\.[0-9]*)$', views.search_by_location, name="search_location"),
    url(r'^onsen/form/entry$', views.onsen_entry_form, name='onsen_entry_form'),
    url(r'^onsen/form/edit$', views.onsen_form, name='onsen_form'),
    url(r'^api/onsen$', views.onsen_list, name='onsen_list'),
    url(r'^api/onsen/post$', views.onsen_post, name='onsen_post')
]
