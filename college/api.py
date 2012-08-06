from tastypie.resources import ModelResource
from college.models import College, CollegeYear, Coach, CollegeCoach, Game
from tastypie import fields

class CollegeResource(ModelResource):
    
    seasons = fields.ToManyField('college.api.CollegeYearResource', 'collegeyear_set')
    
    class Meta:
        queryset = College.objects.filter(updated=True).order_by('name')
        resource_name = 'college'
        excludes = ['updated', 'id']
        allowed_methods = ['get']
        

class CollegeYearResource(ModelResource):
    college = fields.ToOneField(CollegeResource, 'college')
    games = fields.ToManyField('college.api.GameResource', 'game_set')

    class Meta:
        queryset = CollegeYear.objects.filter(college__updated=True).order_by('college__name')
        resource_name = 'college_year'
        excludes = ['id']
        allowed_methods = ['get']

class CoachResource(ModelResource):
    
    college_coaches = fields.ToManyField('college.api.CollegeCoachResource', 'collegecoach_set')
    
    class Meta:
        queryset = Coach.objects.all().order_by('-id')
        resource_name = 'coach'
        excludes = ['id']
        allowed_methods = ['get']

class CollegeCoachResource(ModelResource):
    coach = fields.ToOneField(CoachResource, 'coach')
    college_year = fields.ToOneField(CollegeYearResource, 'college_year')
    
    class Meta:
        queryset = CollegeCoach.objects.all().order_by('-id')
        resource_name = 'college_coach'
        excludes = ['updated', 'id']
        allowed_methods = ['get']

class GameResource(ModelResource):

    team1 = fields.ToOneField(CollegeYearResource, 'team1')
    team2 = fields.ToOneField(CollegeYearResource, 'team2')
    
    team1_name = fields.CharField(attribute='team1_name')
    team2_name = fields.CharField(attribute='team2_name')

    class Meta:
        queryset = Game.objects.filter(has_stats=True).order_by('-date')
        resource_name = 'game'
        excludes = ['id']
        allowed_methods = ['get']

    def dehydrate_ncaa_xml(self, bundle):
        return bundle.data['ncaa_xml'].strip()
