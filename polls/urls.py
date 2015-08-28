from django.conf.urls import patterns, include, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^info/$', views.info),
    url(r'^documents/$', views.result),
    url(r'^clear/$', views.clear),
    url(r'^clear/vcf$', views.clear_vcf),
    url(r'^upload/$', views.upload_view),
    url(r'^tool/$', views.file_frmt_view_up),
    url(r'^authentication/$', views.authentication),

)

