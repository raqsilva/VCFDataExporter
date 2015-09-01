from django.conf.urls import patterns, include, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^documents/$', views.result),
    url(r'^clear/$', views.clear),
    url(r'^clear/vcf$', views.clear_vcf),
    url(r'^authentication/$', views.authentication),
    url(r'^exac/$', views.exac_view),
    url(r'^esp/$', views.esp_view),
    url(r'^1000GP/$', views.GP_view),
    url(r'^upload/$', views.upload_view),

)

