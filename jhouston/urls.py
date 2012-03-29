from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^jserror/$', views.onerror),
    url(r'^jslog/$', views.onlog)
)
