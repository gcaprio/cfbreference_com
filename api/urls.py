from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import CollegeHandler, CoachHandler, CollegeYearHandler

college_handler = Resource(CollegeHandler)
collegeyear_handler = Resource(CollegeYearHandler)
coach_handler = Resource(CoachHandler)

urlpatterns = patterns('',
   url(r'^college/teams/(?P<slug>[^/]+)/$', college_handler),
   url(r'^college/teams/(?P<slug>[^/]+)/(?P<season>\d+)/$', collegeyear_handler),
   url(r'^coach/(?P<slug>[^/]+)/$', coach_handler),
)
