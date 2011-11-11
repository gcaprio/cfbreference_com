from django.utils.encoding import iri_to_uri
from django.http import HttpResponse

class HttpResponseSeeOther(HttpResponse):
    status_code = 303

    def __init__(self, location):
        HttpResponse.__init__(self)
        self['Location'] = iri_to_uri(location)