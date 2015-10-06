from django.conf.urls.defaults import patterns, include, url
#from bugslog.main import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from main.views import process_page, process_empty_slug,\
    my_login, my_logout
from django.conf import settings
from contact_us.views import contactpost
admin.autodiscover()


urlpatterns = patterns('', )

if not settings.PRODUCTION:
    urlpatterns += patterns('', url(r'^media-root/(?P<path>.*)$', 'django.views.static.serve',
                                    {'document_root': settings.MEDIA_ROOT}))

urlpatterns += patterns('',
    # Examples:
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # authentication:
    url(r'^login/', my_login),
    url(r'^logout/', my_logout),
    
    # admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # pages:
    url(r'^$', process_empty_slug),
    url(r'^contactpost/', contactpost),
    url(r'^.*/', process_page)
)






