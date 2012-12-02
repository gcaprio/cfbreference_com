from django.conf.urls.defaults import *

urlpatterns = patterns('rankings.views',
     url(r'^$', 'rankings_index'),
     url(r'^drive-outcomes/(?P<season>\d+)/$', 'drive_outcomes'),
     url(r'^(?P<rankingtype>[-a-z]+)/(?P<season>\d+)/$', 'rankings_season'),
     url(r'^(?P<rankingtype>[-a-z]+)/(?P<season>\d+)/week/(?P<week>\d+)/$', 'rankings_season'),
)