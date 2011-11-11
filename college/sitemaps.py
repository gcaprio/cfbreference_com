from django.contrib.sitemaps import Sitemap
from models import College
from datetime import date

class CollegeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return College.objects.filter(updated=True).order_by('name')

    def lastmod(self, obj):
        return date(2010, 11, 22)

all_sitemaps = {'colleges': CollegeSitemap()}

