from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/links/')),
    url(r'^links/', include('links.urls')),
    url(r'^waitlist/', include('waitlist.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
