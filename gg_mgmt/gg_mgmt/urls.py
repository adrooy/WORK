from django.conf.urls import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gg_mgmt.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('accounts.urls')),
    url(r'^', include('forum.urls')),
    url(r'^', include('game.urls')),
    url(r'^', include('feedback.urls')),
    url(r'^', include('market.urls')),
    url(r'^', include('management.urls')),
    url(r'^', include('urls')),
)


urlpatterns += patterns('',
    url(r'^gg_mgmt/static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),
)
