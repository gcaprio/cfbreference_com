from django.conf.urls.defaults import *
from django.contrib import admin
from feeds import CoachesFeed
from django.views.generic.simple import direct_to_template
from django.conf import settings

feeds = {
    'coaches': CoachesFeed,
}

admin.autodiscover()

urlpatterns = patterns('',
     (r'^admin/coach_totals/(?P<season>\d\d\d\d)/$', "college.views.admin_coach_totals"),
     (r'^admin/doc/', include('django.contrib.admindocs.urls')), 
     (r"^admin/", include(admin.site.urls)),
     url(r"^$", "college.views.homepage"),
     url(r"^", include("college.urls")),
     url(r"^rankings/", include("rankings.urls")),
     (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
     url(r"^blog/", include("blog.urls")),
     url(r"^robots.txt$", direct_to_template, { 'template':"robots.txt"}, name="robots")
)

urlpatterns += patterns('college.views',
     url(r'^coaches/$', 'coach_index'),
     url(r'^coaches/active/$', 'active_coaches'),
     url(r'^coaches/feeds/recent_hires/$', 'recent_hires_feed'),
     url(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/$', 'coach_detail', name="coach_detail"),
     url(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/vs/$', 'coach_vs', name="coach_vs"),
     url(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/vs/(?P<coach2>\d+-[-a-z]+)/$', 'coach_compare', name="coach_compare"),
     url(r'^coaches/assistants/$', 'assistant_index'),
     url(r'^coaches/common/(?P<coach>\d+-[-a-z]+)/(?P<coach2>\d+-[-a-z]+)/$', 'coach_common'),
     url(r'^coaches/departures/(?P<season>\d\d\d\d)/$', 'departures'),
     url(r'^coaches/hires/(?P<season>\d\d\d\d)/$', 'coaching_hires'),
)

# Server Static Content When Debugging & provide views for 500 & 404 errors
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
        url(r'^404/$', direct_to_template, {'template': '404.html'}, name='404'),
        url(r'^500/$', direct_to_template, {'template': '500.html'}, name='500'),
    )

