from django.conf.urls import patterns, url


urlpatterns = patterns('links.views',
    url(r'^$', 'index'),
    url(r'^howto/$', 'howto'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/$', 'view'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/edit/$', 'edit'),
    url(r'^(?P<name>[0-9A-Za-z_\-]+)/edit/commit/$', 'commit'),
)
