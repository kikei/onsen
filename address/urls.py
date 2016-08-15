from django.conf.urls import url

from . import views

app_name = 'address'

urlpatterns = [
    url(r'inference$', views.inference, name='inference'),
    url(r'tolatlng$', views.get_latlng, name='latlng'),
    url(r'bylatlng$', views.get_address, name='address'),
]
