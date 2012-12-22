from django.db import models
from django import forms
import datetime
from django.template.defaultfilters import slugify
from django.conf import settings

CURRENT_SEASON = getattr(settings, 'CURRENT_SEASON', datetime.date.today().year) 

STATUS_CHOICES = (
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
)

POSITION_TYPE_CHOICES = (
    ('O', 'Offense'),
    ('D', 'Defense'),
    ('S', 'Special Teams'),
)

SIDE_CHOICES = (
    ('O', 'Own'),
    ('P', 'Opponents'),
)

RESULT_CHOICES = (
    ('W', 'Win'),
    ('L', 'Loss'),
    ('T', 'Tie'),
)

GAME_TYPE_CHOICES = (
    ('H', 'Home'),
    ('A', 'Away'),
    ('N', 'Neutral Site'),
)

PLAY_CHOICES = (
    ('R', 'Run'),
    ('P', 'Pass'),
    ('F', 'Field Goal'),
    ('X', 'Extra Point'),
    ('N', 'Penalty'),
    ('K', 'Kickoff'),
    ('U', 'Punt'),
    ('T', 'Turnover'),
)

DIVISION_CHOICES = (
    ('B', 'Bowl Subdivision'),
    ('C', 'Championship Subdivision'),
    ('D', 'Division II'),
    ('T', 'Division III'),
)

class State(models.Model):
    id = models.CharField(max_length=2, editable=False, primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/" % self.id.lower()
    
class StateForm(forms.Form):
    name = forms.ModelChoiceField(queryset=State.objects.all().order_by('name'))

class City(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    state = models.ForeignKey(State, null=True, blank=True)
    
    def __unicode__(self):
        if self.state:
            return "%s, %s" % (self.name, self.state.id)
        else:
            return self.name
    
    def get_absolute_url(self):
        return "/states/%s/%s/" % (self.state.id.lower(), self.slug)
    
    class Meta:
        verbose_name_plural = 'cities'
    

class Week(models.Model):
    season = models.IntegerField()
    week_num = models.IntegerField()
    end_date = models.DateField()
    
    def __unicode__(self):
        return "Week %s, %s" % (self.week_num, self.season)
    
    def week_games_url(self):
        return "/seasons/%s/week/%s/" % (self.season, self.week_num)

class Conference(models.Model):
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=90)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/conferences/%s/' % self.abbrev.lower()

class College(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(max_length=90)
    drive_slug = models.CharField(max_length=90)
#    city = models.ForeignKey(City, blank=True) #
    state = models.ForeignKey(State, blank=True)
    official_url = models.CharField(max_length=120, blank=True)
    official_rss = models.CharField(max_length=120, blank=True)
    updated = models.BooleanField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/teams/%s/' % self.slug
    
    def current_record(self):
        current_season = self.collegeyear_set.get(season=datetime.date.today()).year
        return "(%d-%d)" % (current_season.wins, current_season.losses)
    
    class Meta:
        ordering = ['name', 'state']
        

class CollegeYear(models.Model):
    college = models.ForeignKey(College)
    season = models.IntegerField()
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)
    conference_wins = models.IntegerField(default=0)
    conference_losses = models.IntegerField(default=0)
    conference_ties = models.IntegerField(default=0)
    freshmen = models.IntegerField(default=0)
    sophomores = models.IntegerField(default=0)
    juniors = models.IntegerField(default=0)
    seniors = models.IntegerField(default=0)
    conference = models.ForeignKey(Conference, null=True, blank=True)
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)
    
    def __unicode__(self):
        return "%s - %s" % (self.college.name, str(self.season))
    
    def game_count(self):
        return self.wins+self.losses+self.ties
    
    def get_ncaa_week_url(self):
        return 'http://web1.ncaa.org/football/exec/rankingSummary?year=%d&org=%d&week=' % (self.season, self.college.id)
    
    def get_absolute_url(self):
        return "/teams/%s/%s/" % (self.college.slug, self.season)
    
    def get_conference_url(self):
        if self.conference:
            return "/conferences/%s/%s/" % (self.conference.abbrev, self.season)
    
    def coaching_staff_url(self):
        return self.get_absolute_url()+'coaches/'
    
    def record(self):
        if self.ties:
            return "%s-%s-%s" % (self.wins, self.losses, self.ties)
        else:
            return "%s-%s" % (self.wins, self.losses)
    
    def conference_record(self):
        if self.conference_ties:
            return "%s-%s-%s" % (self.conference_wins, self.conference_losses, self.conference_ties)
        else:
            return "%s-%s" % (self.conference_wins, self.conference_losses)
    
    def coach_total(self):
        return len(self.collegecoach_set.filter(end_date__isnull=True))
    
    class Meta:
        ordering = ['college', '-season']

class Coach(models.Model):
    ncaa_name = models.CharField(max_length=90)
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    slug = models.CharField(max_length=75, editable=False)
    college = models.ForeignKey(College, null=True, blank=True, related_name='School')
    grad_year = models.IntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    years = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)
    losses = models.IntegerField(default=0, blank=True)
    ties = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return self.first_name + " " + self.last_name
    
    def save(self):
        super(Coach, self).save()
        self.slug = '%s-%s-%s' % (str(self.id), slugify(self.first_name), slugify(self.last_name))
        super(Coach, self).save()
    
    def get_absolute_url(self):
        return '/coaches/detail/%s/' % self.slug
    
    def full_name(self):
        return self.first_name + " " + self.last_name
    
    def current_school(self):
        try:
            current_school = self.collegecoach_set.get(collegeyear__season__exact = CURRENT_SEASON, end_date = None).collegeyear.college
        except:
            current_school = None
        return current_school
    
    def seasons_at_school(self,school):
        return [sorted([cy.collegeyear.season for cy in self.collegecoach_set.all() if cy.collegeyear.college == school])]
        
    
    def seasons_at_current_school(self):
        return len([cy.collegeyear.college.id for cy in self.collegecoach_set.all() if cy.collegeyear.college.id == self.current_school().id])
    
    def current_job(self):
        if self.current_school():
            cy = self.collegecoach_set.filter(collegeyear__college=self.current_school).order_by('start_date')[0].jobs_display()
            return cy
        else:
            return None
    
    def head_coach_experience(self):
        if 1 in sum([[j.id for j in job.jobs.all() if j.id == 1] for job in self.collegecoach_set.all()],[]):
            return "Yes"
        else:
            return "No"
        
    def years_since_2000(self):
        return self.collegecoach_set.all().count()
    
    def years_at_alma_mater_since_2000(self):
        return len([a for a in self.collegecoach_set.all() if self.college == a.collegeyear.college])
    
    def states_coached_in(self):
        states = {}
        state_list = [s.collegeyear.college.state.id for s in self.collegecoach_set.all()]
        [states.setdefault(e,500) for e in state_list if e not in states]
        return states
    
    def coaching_peers(self):
        from django.db import connection
        cursor = connection.cursor()
        year_ids = [str(c.collegeyear.id) for c in self.collegecoach_set.all()]
        if len(year_ids) > 0:
            cursor.execute("SELECT distinct college_coach.id FROM college_coach INNER JOIN college_collegecoach ON college_coach.id=college_collegecoach.coach_id WHERE college_collegecoach.collegeyear_id IN (%s)" % ','.join(year_ids))
            results = cursor.fetchall()
            ids = [c[0] for c in results]
            return Coach.objects.filter(id__in=ids).exclude(id=self.id)
        else:
            return Coach.objects.none()
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'Coaches'

class CoachForm(forms.Form):
    name = forms.CharField(max_length=50, initial='Last name')

class CoachDetailForm(forms.Form):
    coaches = forms.ModelChoiceField(queryset=Coach.objects.none())
    def __init__(self, coaches, *args, **kwargs):
        super(CoachDetailForm, self).__init__(*args, **kwargs)
        self.fields["coaches"].queryset = coaches

class CoachingJob(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    
    def __unicode__(self):
        return self.name

class CollegeCoach(models.Model):
    coach = models.ForeignKey(Coach)
    collegeyear = models.ForeignKey(CollegeYear)
    jobs = models.ManyToManyField(CoachingJob)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_head_coach = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s: %s" % (self.coach, self.collegeyear)
        
    def get_absolute_url(self):
        return self.coach.get_absolute_url()
    
    def jobs_display(self):
        return ", ".join([x.name for x in self.jobs.all()])
    
    def is_current_job(self):
        if self.collegeyear.season == CURRENT_SEASON and self.end_date == None:
            return True
        else:
            return False
    
    def partial_season(self):
        if end_date:
            return True
        else:
            return False
    
    def feed_date(self):
        if self.start_date and self.end_date:
            return self.end_date
        elif self.start_date:
            return self.start_date
        elif self.end_date:
            return self.end_date
            
    def feed_action(self):
        if self.start_date and self.end_date:
            return "Departed"
        elif self.start_date:
            return "Hired"
        elif self.end_date:
            return "Departed"
            

    class Meta:
        ordering = ['coach__last_name','-collegeyear__season']
        verbose_name_plural = 'College coaches'

class CollegeTotal(models.Model):
    college = models.ForeignKey(College)
    season = models.IntegerField()
    third_down_attempts = models.IntegerField(default=0)
    third_down_conversions = models.IntegerField(default=0)
    fourth_down_attempts = models.IntegerField(default=0)
    fourth_down_conversions = models.IntegerField(default=0)
    first_downs_rushing = models.IntegerField(default=0)
    first_downs_passing = models.IntegerField(default=0)
    first_downs_penalty = models.IntegerField(default=0)
    first_downs_total = models.IntegerField(default=0)
    penalties = models.IntegerField(default=0)
    penalty_yards = models.IntegerField(default=0)
    fumbles = models.IntegerField(default=0)
    fumbles_lost = models.IntegerField(default=0)
    rushes = models.IntegerField(default=0)
    rush_gain = models.IntegerField(default=0)
    rush_loss = models.IntegerField(default=0)
    rush_net = models.IntegerField(default=0)
    rush_touchdowns = models.IntegerField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)
    pass_attempts = models.IntegerField(default=0)
    pass_completions = models.IntegerField(default=0)
    pass_interceptions = models.IntegerField(default=0)
    pass_yards = models.IntegerField(default=0)
    pass_touchdowns = models.IntegerField(default=0)
    receptions = models.IntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)
    punts = models.IntegerField(default=0)
    punt_yards = models.IntegerField(default=0)
    punt_returns = models.IntegerField(default=0)
    punt_return_yards = models.IntegerField(default=0)
    punt_return_touchdowns = models.IntegerField(default=0)
    kickoff_returns = models.IntegerField(default=0)
    kickoff_return_yards = models.IntegerField(default=0)
    kickoff_return_touchdowns = models.IntegerField(default=0)
    touchdowns = models.IntegerField(default=0)
    pat_attempts = models.IntegerField(default=0)
    pat_made = models.IntegerField(default=0)
    two_point_conversion_attempts = models.IntegerField(default=0)
    two_point_conversions = models.IntegerField(default=0)
    field_goal_attempts = models.IntegerField(default=0)
    field_goals_made = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

class Position(models.Model):
    abbrev = models.CharField(max_length=5)
    name = models.CharField(max_length=25)
    plural_name = models.CharField(max_length=25)
    position_type = models.CharField(max_length=1, choices=POSITION_TYPE_CHOICES)

    def __unicode__(self):
        return self.abbrev

    def get_absolute_url(self):
        return '/recruits/positions/%s/' % self.abbrev.lower()


class BowlGame(models.Model):
    name = models.CharField(max_length=75)
    slug = models.CharField(max_length=75)
    city = models.ForeignKey(City)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return '/bowl-games/%s/' % self.slug
    

class Game(models.Model):
    season = models.IntegerField()
    team1 = models.ForeignKey(CollegeYear, related_name='team1')
    coach1 = models.ForeignKey(Coach, null=True, blank=True, related_name='first_coach')
    team2 = models.ForeignKey(CollegeYear, related_name='team2')
    coach2 = models.ForeignKey(Coach, null=True, blank=True, related_name='second_coach')
    date = models.DateField()
    week = models.ForeignKey(Week)
    t1_game_type = models.CharField(max_length=1, choices=GAME_TYPE_CHOICES)
    t1_result = models.CharField(max_length=1, choices=RESULT_CHOICES, blank=True)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)
    site = models.CharField(max_length=90, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    overtime = models.CharField(max_length=5, blank=True)
    ncaa_xml = models.CharField(max_length=120, blank=True)
    duration = models.TimeField(null=True, blank=True)
    has_drives = models.BooleanField()
    has_stats = models.BooleanField()
    has_player_stats = models.BooleanField()
    is_conference_game = models.BooleanField()
    is_bowl_game = models.BooleanField()
    bowl_game = models.ForeignKey(BowlGame, null=True, blank=True)
    
    def __unicode__(self):
        return '%s vs. %s, %s' % (self.team1, self.team2, self.date)
    
    def team1_name(self):
        return self.team1.college.name

    def team2_name(self):
        return self.team2.college.name
    
    def get_absolute_url(self):
        return '/teams/%s/vs/%s/%s/%s/%s/' % (self.team1.college.slug, self.team2.college.slug, self.date.year, self.date.month, self.date.day)

    def get_matchup_url(self):
        return '/teams/%s/vs/%s/' % (self.team1.college.slug, self.team2.college.slug)
    
    def get_reverse_url(self):
        return '/teams/%s/vs/%s/%s/%s/%s/' % (self.team2.college.slug, self.team1.college.slug, self.date.year, self.date.month, self.date.day)
        
    def get_ncaa_xml_url(self):
        return 'http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/%s.xml' % (self.season, self.ncaa_xml.strip())
    
    def get_ncaa_drive_url(self):
        return "http://web1.ncaa.org/mfb/driveSummary.jsp?acadyr=%s&h=%s&v=%s&date=%s&game=%s" % (self.season, self.team1.college.id, self.team2.id, self.date.strftime("%d-%b-%y").upper(), self.ncaa_xml.strip())
    
    def get_ncaa_scoring_url(self):
        return "http://web1.ncaa.org/mfb/scoreSummary.jsp?acadyr=%s&h=%s&v=%s&date=%s&game=%s" % (self.season, self.team1.college.id, self.team2.id, self.date.strftime("%d-%b-%y").upper(), self.ncaa_xml.strip())

    def get_play_by_play_url(self):
        return "http://web1.ncaa.org/mfb/driveSummary.jsp?expand=A&acadyr=%s&h=%s&v=%s&date=%s&game=%s" % (self.season, self.team1.college.id, self.team2.id, self.date.strftime("%d-%b-%y").upper(), self.ncaa_xml.strip())
    
    def margin(self):
        return self.team1_score-self.team2_score
    
    def display(self):
        if self.margin() > 0:
            return "%s %s, %s %s" % (self.team1.college, self.team1_score, self.team2.college, self.team2_score)
        else:
            return "%s %s, %s %s" % (self.team2.college, self.team2_score, self.team1.college, self.team1_score)

class QuarterScore(models.Model):
    "Represents a team's scoring during a quarter of a game. OT periods begin with 5."
    "Not implemented yet."
    game = models.ForeignKey(Game)
    team = models.ForeignKey(CollegeYear)
    season = models.IntegerField()
    quarter = models.IntegerField(default=CURRENT_SEASON)
    points = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return "%s - %s" (self.team, self.quarter)
    
class GameScore(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(CollegeYear)
    season = models.IntegerField()
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.description

class DriveOutcome(models.Model):
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=50, null=True)
    slug = models.SlugField(max_length=50, null=True)
    
    def __unicode__(self):
        return self.name

class GameDrive(models.Model):
    season = models.IntegerField()
    game = models.ForeignKey(Game)
    team = models.ForeignKey(CollegeYear)
    drive = models.IntegerField()
    quarter = models.PositiveSmallIntegerField()
    start_how = models.CharField(max_length=25)
    start_time = models.TimeField()
    start_position = models.IntegerField()
    start_side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    end_result = models.ForeignKey(DriveOutcome)
    end_time = models.TimeField()
    end_position = models.IntegerField(null=True)
    end_side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    plays = models.IntegerField()
    yards = models.IntegerField()
    time_of_possession = models.TimeField()
    
    def __unicode__(self):
        return "%s: %s drive %s" % (self.game, self.team, self.drive)

class GamePlay(models.Model):
    game = models.ForeignKey(Game)
    offensive_team = models.ForeignKey(CollegeYear)
    drive = models.ForeignKey(GameDrive, blank=True, null=True)
    quarter = models.PositiveSmallIntegerField()
    description = models.TextField()
    down = models.IntegerField()
    distance = models.IntegerField()

    def __unicode__(self):
        return "%s: %s: %s" % (self.game, self.offensive_team, self.description)

class GameDriveSeason(models.Model):
    season = models.IntegerField()
    team = models.ForeignKey(CollegeYear)
    outcome = models.ForeignKey(DriveOutcome)
    total = models.IntegerField(null=True)
    drives_total = models.IntegerField(null=True)
    
    def __unicode__(self):
        return "%s: %s %s" % (self.season, self.team, self.outcome)

    def pct_of_total(self):
        return float(float(self.total)/float(self.drives_total))*100

    
class GameOffense(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(CollegeYear)
    season = models.IntegerField()
    third_down_attempts = models.IntegerField(default=0)
    third_down_conversions = models.IntegerField(default=0)
    fourth_down_attempts = models.IntegerField(default=0)
    fourth_down_conversions = models.IntegerField(default=0)
    time_of_possession = models.TimeField(null=True)
    first_downs_rushing = models.IntegerField(default=0)
    first_downs_passing = models.IntegerField(default=0)
    first_downs_penalty = models.IntegerField(default=0)
    first_downs_total = models.IntegerField(default=0)
    penalties = models.IntegerField(default=0)
    penalty_yards = models.IntegerField(default=0)
    fumbles = models.IntegerField(default=0)
    fumbles_lost = models.IntegerField(default=0)
    rushes = models.IntegerField(default=0)
    rush_gain = models.IntegerField(default=0)
    rush_loss = models.IntegerField(default=0)
    rush_net = models.IntegerField(default=0)
    rush_touchdowns = models.IntegerField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)
    pass_attempts = models.IntegerField(default=0)
    pass_completions = models.IntegerField(default=0)
    pass_interceptions = models.IntegerField(default=0)
    pass_yards = models.IntegerField(default=0)
    pass_touchdowns = models.IntegerField(default=0)
    receptions = models.IntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)
    punts = models.IntegerField(default=0)
    punt_yards = models.IntegerField(default=0)
    punt_returns = models.IntegerField(default=0)
    punt_return_yards = models.IntegerField(default=0)
    punt_return_touchdowns = models.IntegerField(default=0)
    kickoff_returns = models.IntegerField(default=0)
    kickoff_return_yards = models.IntegerField(default=0)
    kickoff_return_touchdowns = models.IntegerField(default=0)
    touchdowns = models.IntegerField(default=0)
    pat_attempts = models.IntegerField(default=0)
    pat_made = models.IntegerField(default=0)
    two_point_conversion_attempts = models.IntegerField(default=0)
    two_point_conversions = models.IntegerField(default=0)
    field_goal_attempts = models.IntegerField(default=0)
    field_goals_made = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s - %s' % (self.game, self.team)
    
    def third_down_rate(self):
        return float(self.third_down_conversions)/float(self.third_down_attempts)
    
    def field_goal_rate(self):
        return float(self.field_goals_made)/float(self.field_goal_attempts)
    
    def penalty_yard_ratio(self):
        return float(self.penalty_yards)/float(self.total_yards)
    
    def yards_per_reception(self):
        return float(self.receiving_yards)/float(self.receptions)
    
    def yards_per_pass_attempt(self):
        return float(self.receiving_yards)/(self.pass_attempts)
    
    def rushing_first_downs_pct(self):
        return float(self.first_downs_rushing)/float(self.first_downs_total)*100

    """
    Returns a floating-point number representing the number
    of touchdowns per rushing attempt for a single game.
    """
    def touchdowns_per_rushes(self):
        return float(self.rush_touchdowns)/float(self.rushes)*100
    
    """
    Returns the opponent for a team's given Game Offense record.
    """
    def opponent(self):
        if self.team == self.game.team2:
            return self.game.team1
        else:
            return self.game.team2

class GameDefense(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(CollegeYear)
    season = models.IntegerField()
    safeties = models.IntegerField(default=0)
    unassisted_tackles = models.IntegerField(default=0)
    assisted_tackles = models.IntegerField(default=0)
    unassisted_tackles_for_loss = models.IntegerField(default=0)
    assisted_tackles_for_loss = models.IntegerField(default=0)
    tackles_for_loss_yards = models.IntegerField(default=0)
    unassisted_sacks = models.IntegerField(default=0)
    assisted_sacks = models.IntegerField(default=0)
    sack_yards = models.IntegerField(default=0)
    defensive_interceptions = models.IntegerField(default=0)
    defensive_interception_yards = models.IntegerField(default=0)
    defensive_interception_touchdowns = models.IntegerField(default=0)
    pass_breakups = models.IntegerField(default=0)
    fumbles_forced = models.IntegerField(default=0)
    fumbles_number = models.IntegerField(default=0)
    fumbles_yards = models.IntegerField(default=0)
    fumbles_touchdowns = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '%s - %s' % (self.game, self.team)

class Player(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    team = models.ForeignKey(CollegeYear)
    season = models.IntegerField()
    position = models.ForeignKey(Position)
    number = models.CharField(max_length=4)
    games_played = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.team)

    @models.permalink
    def get_absolute_url(self):
        return ('college.views.player_detail', (), {
            'team': self.team.college.slug,
            'season': self.season,
            'player': self.slug,
            'number': self.number,
            'position': self.position.abbrev
        })
        #return '/teams/%s/%s/players/%s/' % (self.team.college.slug, self.season, self.slug)
    
    def get_team_position_url(self):
        return '/teams/%s/%s/players/positions/%s/' % (self.team.college.slug, self.season, self.position.abbrev.lower())
    
    def get_team_class_url(self):
        return '/teams/%s/%s/players/class/%s/' % (self.team.college.slug, self.season, self.status.lower())
    
    class Meta:
        ordering = ['id']

class PlayerCollegeCareer(models.Model):
    player = models.ForeignKey(Player)
    first_season = models.ForeignKey(CollegeYear, related_name='first_season')
    last_season = models.ForeignKey(CollegeYear, related_name='last_season')
    total_games = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.player.name.full_name()

class PlayerGame(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    played = models.BooleanField()
    starter = models.BooleanField()
    total_plays = models.IntegerField()
    total_yards = models.IntegerField()
    
    def __unicode__(self):
        return self.player.name
    

class PlayerRush(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    rushes = models.IntegerField(default=0)
    gain = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    net = models.IntegerField(default=0)
    td = models.IntegerField(default=0)
    long_yards = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)
    
    class Meta:
        verbose_name_plural = "player rushing"

class PlayerPass(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    attempts = models.IntegerField(default=0)
    completions = models.IntegerField(default=0)
    interceptions = models.IntegerField(default=0)
    yards = models.IntegerField(default=0)
    td = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)
    pass_efficiency = models.FloatField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)
    
    def comp_att(self):
        return "%d of %d" % (self.completions, self.attempts)
    
    class Meta:
        verbose_name_plural = 'player passing'

class PlayerReceiving(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    receptions = models.IntegerField(default=0)
    yards = models.IntegerField(default=0)
    td = models.IntegerField(default=0)
    long_yards = models.IntegerField(default=0)
    average = models.FloatField(default=0)
    
    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerScoring(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    td = models.IntegerField(default=0)
    fg_att = models.IntegerField(default=0)
    fg_made = models.IntegerField(default=0)
    pat_att = models.IntegerField(default=0)
    pat_made = models.IntegerField(default=0)
    two_pt_att = models.IntegerField(default=0)
    two_pt_made = models.IntegerField(default=0)
    def_pat_att = models.IntegerField(default=0)
    def_pat_made = models.IntegerField(default=0)
    def_two_pt_att = models.IntegerField(default=0)
    def_two_pt_made = models.IntegerField(default=0)
    safeties = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)


class PlayerTackle(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    unassisted_tackles = models.IntegerField(default=0)
    assisted_tackles = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

    def total_tackles(self):
        return self.unassisted_tackles+self.assisted_tackles


class PlayerTacklesLoss(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    unassisted_tackles_for_loss = models.IntegerField(default=0)
    assisted_tackles_for_loss = models.IntegerField(default=0)
    tackles_for_loss_yards = models.IntegerField(default=0)
    unassisted_sacks = models.IntegerField(default=0)
    assisted_sacks = models.IntegerField(default=0)
    sack_yards = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)
    
    def total_sacks(self):
        return self.unassisted_sacks+self.assisted_sacks
    
    def total_tackles_for_loss(self):
        return self.unassisted_tackles_for_loss+self.assisted_tackles_for_loss
    
    class Meta:
        verbose_name_plural = 'player tackles for loss'

class PlayerPassDefense(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    interceptions = models.IntegerField(default=0)
    interception_yards = models.IntegerField(default=0)
    interception_td = models.IntegerField(default=0)
    pass_breakups = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)


class PlayerFumble(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    fumbles_forced = models.IntegerField(default=0)
    fumbles_number = models.IntegerField(default=0)
    fumbles_yards = models.IntegerField(default=0)
    fumbles_td = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerReturn(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    punt_returns = models.IntegerField(default=0)
    punt_return_yards = models.IntegerField(default=0)
    punt_return_td = models.IntegerField(default=0)
    kickoff_returns = models.IntegerField(default=0)
    kickoff_return_yards = models.IntegerField(default=0)
    kickoff_return_td = models.IntegerField(default=0)
    
    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerSummary(models.Model):
    player = models.ForeignKey(Player)
    rushes = models.IntegerField(null=True)
    rush_gain = models.IntegerField(null=True)
    rush_loss = models.IntegerField(null=True)
    rush_net = models.IntegerField(null=True)
    rush_td = models.IntegerField(null=True)
    pass_attempts = models.IntegerField(null=True)
    pass_complete = models.IntegerField(null=True)
    pass_intercept = models.IntegerField(null=True)
    pass_yards = models.IntegerField(null=True)
    pass_td = models.IntegerField(null=True)
    conversions = models.IntegerField(null=True)
    offense_plays = models.IntegerField(null=True)
    offense_yards = models.IntegerField(null=True)
    receptions = models.IntegerField(null=True)
    reception_yards = models.IntegerField(null=True)
    reception_td = models.IntegerField(null=True)

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.player.season)

class Poll(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    
    def __unicode__(self):
        return self.name
        

class PollResults(models.Model):
    poll = models.ForeignKey(Poll)
    week = models.ForeignKey(Week)
    team = models.ForeignKey(College)
    rank = models.IntegerField()
    
    def __unicode__(self):
        return "%s: %s %s" % (self.poll, self.week, self.team)
