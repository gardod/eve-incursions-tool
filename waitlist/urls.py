from django.conf.urls import patterns, url


urlpatterns = patterns('waitlist.views',
    url(r'^$', 'index'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/$', 'view'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/join/$', 'join'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/leave/$', 'leave'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/status/$', 'status'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/remove/$', 'remove'),
)
