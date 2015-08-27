from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'', include('polls.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/auth/$', views.auth_view),    
    url(r'^accounts/logout/$', views.logout),
    url(r'^accounts/invalid/$', views.invalid_login),
    url(r'^register/', views.register_user),
    url(r'^register_success/', views.register_success),
    url(r'^confirm/(?P<activation_key>\w+)/', views.register_confirm),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_confirm, name='reset_confirm'),
    url(r'^reset/$', views.reset, name='reset'),


) #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
