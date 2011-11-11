from college.models import College, CollegeYear, Game
from utils import *
from scrapers.games import game_updater, load_ncaa_game_xml, player_game_stats, game_drive_loader
from django.db.models import Q

def full_load(year, week):
    """
    Given a year and week, performs a full load of games including all player and game stats.
    >>> full_load(2010, 13)
    """
    game_updater(year, None, week)

def full_nostats_load(year, week):
    """
    Given a year and week, performs a full load of games, but just scores, not player and game stats. Useful for 
    updates on a Saturday before game xml files are available on ncaa.org.
    >>> full_nostats_load(2010, 13)
    """
    game_updater(year, None, week, nostats=True)

def partial_loader(year, id, week):
    """
    Given a year, team id and week, performs a full load beginning with that team, in ascending order of team id.
    >>> partial_loader(2010, 235, 13)
    """
    teams = CollegeYear.objects.filter(college__updated=True, season=year, college__id__gte=id).order_by('college_college.id')
    game_updater(year, teams, week)

def games_without_stats_loader(season):
    """
    Given a list of games that have been completed and partially loaded, adds game, player and drive stats.
    """
    stats_filter = Q(has_stats=False ) | Q(has_player_stats=False) | Q(has_drives=False)

    games = Game.objects.filter(stats_filter, season=season, ncaa_xml__startswith="2")
    for game in games:
        try:
            if not game.has_stats:
                load_ncaa_game_xml(game)
                game.has_stats = True
            if not game.has_player_stats:
                player_game_stats(game)
                game.has_player_stats = True
            if not game.has_drives:
                game_drive_loader(game)
                game.has_drives = True
            game.save()
        except:
            print game

def prepare_new_season(year):
    add_college_years(year)
    update_conference_membership(year)
    game_updater(year, None, 19)
    create_weeks(year)
    game_weeks(year)
    update_conf_games(year)
    games = Game.objects.filter(season=year, coach1__isnull=True, coach2__isnull=True)
    for game in games:
        populate_head_coaches(game)
