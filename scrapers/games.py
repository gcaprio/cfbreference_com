import urllib
import time
from BeautifulSoup import BeautifulSoup
from college.models import *
from utils import update_college_year, populate_head_coaches
from django.template.defaultfilters import slugify
from scrapers.models import NCAAGame

def game_updater(year, teams, week, nostats=False):
    """
    Loads a team's games for a given year, creating new games as it finds them and updating scores. If needed,
    it will create new College records for opponents. The function accepts an optional QuerySet of teams. 
    It can be run in nostats mode, in which case the function updates only the score. If nostats=True, 
    after the game is updated the function calls other functions to update player and drive statistics. After completing,
    this function calls update_college_year for the given year, which updates the win-loss record of each team.
    
    >>> game_updater(2010, teams, 12)
    """
    if not teams:
        teams = CollegeYear.objects.filter(season=year, college__updated=True).order_by('id')
    
    games = []

    starting_time = datetime.datetime.now()
    print "Run Start"
    print starting_time.strftime("%Y-%m-%d %H:%M")

    last_team_end = datetime.datetime.now()
    counter = 1
    total_count = teams.count()
    for team in teams:
        print "%(counter)s out of %(total_count)s " % { 'counter': str(counter), 'total_count': str(total_count) }
        team_start = datetime.datetime.now()
        print team
        print "Team Start"
        print team_start.strftime("%Y-%m-%d %H:%M:%S")
        url = "http://web1.ncaa.org/football/exec/rankingSummary?org=%s&year=%s&week=%s" % (team.college.id, year, week)
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        try:
            tables = soup.findAll('table') # list
            t = tables[2] # BS.Tag
            rows = t.findAll('tr')[2:] #list
            for row in rows: # BS.Tag
                game_results = row.findAll('td')
                try:
                    game_file = game_results[0].find('a')['href'].split('game=')[1]
                    stringdate = game_results[0].find('a').contents[0][4:]
                    team1_score, team2_score = [int(x) for x in game_results[2].contents[0].split(' - ')]
                    if len(game_results[3].contents[0].strip().split(' ')) == 2:
                        t1_result, ot = game_results[3].contents[0].strip().split(' ')
                    else:
                        t1_result = game_results[3].contents[0].strip()
                        ot = None

                except:
                    game_file = None
                    stringdate = game_results[0].contents[0][4:]
                    team1_score = None
                    team2_score = None
                    t1_result = None
                    ot = None
                date = datetime.date(*(time.strptime(stringdate, '%m/%d/%Y')[0:3]))
                try:
                    t2 = int(game_results[1].find('a')['href'].split('=')[1].split('&')[0])
                    try:
                        if t2 == 115:   # hack job to cover for ncaa change
                            team2 = CollegeYear.objects.get(college__id=30416, season=year)
                        elif t2 == 357: # another one like the above - Lincoln Univ. PA
                            team2 = CollegeYear.objects.get(college__id=30417, season=year)
                        else:
                            team2 = CollegeYear.objects.get(college__id=t2, season=year)
                    except:
                        name = game_results[1].contents[0].replace("*","").strip().title()
                        slug = slugify(name)
                        new_college, created = College.objects.get_or_create(name=name, slug=slug)
                        team2 = CollegeYear.objects.get_or_create(college=new_college, season=year)
                except:
                    if len(game_results[1].contents) > 0 and game_results[1].contents[0] != '':
                        name = game_results[1].contents[0].replace("*","").replace("@","").strip().title()
                        slug = slugify(name)
                        new_college, created = College.objects.get_or_create(name=name, slug=slug)
                        team2, created = CollegeYear.objects.get_or_create(college=new_college, season=year)
                    else:
                        continue
                g, new_game = Game.objects.get_or_create(season=year, team1=team, team2=team2, date=date)
                g.team1_score = team1_score
                g.team2_score=team2_score
                g.t1_result=t1_result
                g.overtime=ot
                if game_file:
                    g.ncaa_xml = game_file.split('.xml')[0].strip()
                    games.append(g)
                    if not nostats:
                        load_ncaa_game_xml(g)
                        g.has_stats = True
                        player_game_stats(g)
                        g.has_player_stats = True
                        game_drive_loader(g)
                        g.has_drives = True
                else:
                    # make sure ncaa_xml attribute is set to null, not empty string
                    g.ncaa_xml = None
                    g.save()
                if ot:
                    g.ot = 't'
                if "@" in game_results[1].contents[0]:
                    g.t1_game_type = 'A'
                elif "^" in game_results[1].contents[0]:
                    g.t1_game_type = 'N'
                elif game_results[1].find('a') and "@" in game_results[1].find('a').contents[0]:
                    g.t1_game_type = 'A'
                elif game_results[1].find('a') and "^" in game_results[1].find('a').contents[0]:
                    g.t1_game_type = 'N'
                else:
                    g.t1_game_type = 'H'
                if new_game:
                    populate_head_coaches(g)
                g.save()
        except:
            next
        team_end = datetime.datetime.now()

        print "Team End"
        print team_end.strftime("%Y-%m-%d %H:%M:%S")
        print "Duration (Seconds)"
        duration = team_end - last_team_end
        print duration.seconds
        last_team_end = team_end
        counter = counter + 1

    update_college_year(year)

    run_end = datetime.datetime.now()
    total_duration = run_end - starting_time
    print "Run End"
    print run_end.strftime("%Y-%m-%d %H:%M:%S")
    print "Total Duration (mins)"
    print total_duration.seconds / 60

def update_player_game_stats(s):
    """
    Updates player game statistics for an entire season for games that have not already set them. 
    Not used as part of a weekly load of games.
    >>> update_player_game_stats(2009)
    """
    games = Game.objects.filter(has_player_stats=False, season=s, ncaa_xml__startswith=s)
    for game in games:
        player_game_stats(game)
        game.has_player_stats = True
        game.save()


def load_ncaa_game_xml(game):
    """
    Loader for NCAA game xml files. Accepts a Game object. The NCAA's xml needs to be cleaned up slightly by replacing
    elements with interior spaces with 0. Some game files contain inaccurate team IDs, mostly for smaller schools, 
    which explains the hard-coding below. On occasion, usually when a team schedules an NAIA opponent, the 
    NCAA may not have have an ID, which will raise an error.
    >>> game = Game.objects.get(id=793)
    >>> load_ncaa_game_xml(game)
    """
    ncaa_game = NCAAGame(game.get_ncaa_xml_url())
    
    try:
        if ncaa_game.game_xml.findall("/SCORE/VISITOR/NAME")[0].text == game.team1.college.drive_slug:
            visitor = game.team1
            home = game.team2
        else:
            visitor = game.team2
            home = game.team1
        game_v,created = Game.objects.get_or_create(team1=game.team2, team2=game.team1, date=game.date,season=game.season)
        try:
            game.attendance = ncaa_game.attendance
            game_v.attendance = ncaa_game.attendance
        except:
            pass
        try:
            game.duration = ncaa_game.duration
            game_v.duration = game.duration
        except:
            pass
        game.save()
        game_v.save()

        print "Saved %s" % game

        if not game.has_stats:
            home_time = ncaa_game.home_stats.time_of_possession.split(":") or None
            # home team offense - based on game.t1_game_type
            if home == game.team1:
                home_offense, created = GameOffense.objects.get_or_create(game=game, team=home)
            else:
                home_offense, created = GameOffense.objects.get_or_create(game=game_v, team=home)

            if game.date.year > 2006 and home_time[0] != '':
                home_offense.time_of_possession=datetime.time(0, int(home_time[0]), int(home_time[1]))
            else:
                home_offense.time_of_possession = None

            home_offense.third_down_attempts=ncaa_game.home_stats.third_down_attempts
            home_offense.third_down_conversions=ncaa_game.home_stats.third_down_conversions
            home_offense.fourth_down_attempts=ncaa_game.home_stats.fourth_down_attempts
            home_offense.fourth_down_conversions=ncaa_game.home_stats.fourth_down_conversions
            home_offense.first_downs_rushing=ncaa_game.home_stats.first_downs_rushing
            home_offense.first_downs_passing=ncaa_game.home_stats.first_downs_passing
            home_offense.first_downs_penalty=ncaa_game.home_stats.first_downs_penalty
            home_offense.first_downs_total=ncaa_game.home_stats.first_downs_total
            home_offense.penalties=ncaa_game.home_stats.penalties
            home_offense.penalty_yards=ncaa_game.home_stats.penalty_yards
            home_offense.fumbles=ncaa_game.home_stats.fumbles
            home_offense.fumbles_lost=ncaa_game.home_stats.fumbles_lost
            home_offense.rushes=ncaa_game.home_stats.rushes
            home_offense.rush_gain=ncaa_game.home_stats.rush_gain
            home_offense.rush_loss=ncaa_game.home_stats.rush_loss
            home_offense.rush_net=ncaa_game.home_stats.rush_net
            home_offense.rush_touchdowns=ncaa_game.home_stats.rush_touchdowns
            home_offense.total_plays=ncaa_game.home_stats.total_plays
            home_offense.total_yards=ncaa_game.home_stats.total_yards
            home_offense.pass_attempts=ncaa_game.home_stats.pass_attempts
            home_offense.pass_completions=ncaa_game.home_stats.pass_completions
            home_offense.pass_interceptions=ncaa_game.home_stats.pass_interceptions
            home_offense.pass_yards=ncaa_game.home_stats.pass_yards
            home_offense.pass_touchdowns=ncaa_game.home_stats.pass_touchdowns
            home_offense.receptions=ncaa_game.home_stats.receptions
            home_offense.receiving_yards=ncaa_game.home_stats.receiving_yards
            home_offense.receiving_touchdowns=ncaa_game.home_stats.receiving_touchdowns
            home_offense.punts=ncaa_game.home_stats.punts
            home_offense.punt_yards=ncaa_game.home_stats.punt_yards
            home_offense.punt_returns=ncaa_game.home_stats.punt_returns
            home_offense.punt_return_yards=ncaa_game.home_stats.punt_return_yards
            home_offense.punt_return_touchdowns=ncaa_game.home_stats.punt_return_touchdowns
            home_offense.kickoff_returns=ncaa_game.home_stats.kickoff_returns
            home_offense.kickoff_return_yards=ncaa_game.home_stats.kickoff_return_yards
            home_offense.kickoff_return_touchdowns=ncaa_game.home_stats.kickoff_return_touchdowns
            home_offense.touchdowns=ncaa_game.home_stats.touchdowns
            home_offense.pat_attempts=ncaa_game.home_stats.pat_attempts
            home_offense.pat_made=ncaa_game.home_stats.pat_made
            home_offense.two_point_conversion_attempts=ncaa_game.home_stats.two_point_conversion_attempts
            home_offense.two_point_conversions=ncaa_game.home_stats.two_point_conversions
            home_offense.field_goal_attempts=ncaa_game.home_stats.field_goal_attempts
            home_offense.field_goals_made=ncaa_game.home_stats.field_goals_made
            home_offense.points=ncaa_game.home_stats.points

            home_offense.save()
            print "Home Offense: %s" % home_offense

            # home team defense
            if home == game.team1:
                home_defense, created = GameDefense.objects.get_or_create(game = game, team=home)
            else:
                home_defense, created = GameDefense.objects.get_or_create(game = game_v, team=home)

            home_defense.safeties = ncaa_game.home_stats.safeties
            home_defense.unassisted_tackles = ncaa_game.home_stats.unassisted_tackles
            home_defense.assisted_tackles = ncaa_game.home_stats.assisted_tackles
            home_defense.unassisted_tackles_for_loss = ncaa_game.home_stats.unassisted_tackles_for_loss
            home_defense.assisted_tackles_for_loss = ncaa_game.home_stats.assisted_tackles_for_loss
            home_defense.tackles_for_loss_yards = ncaa_game.home_stats.tackles_for_loss_yards
            home_defense.unassisted_sacks = ncaa_game.home_stats.unassisted_sacks
            home_defense.assisted_sacks = ncaa_game.home_stats.assisted_sacks
            home_defense.sack_yards = ncaa_game.home_stats.sack_yards
            home_defense.defensive_interceptions = ncaa_game.home_stats.defensive_interceptions
            home_defense.defensive_interception_yards = ncaa_game.home_stats.defensive_interception_yards
            home_defense.defensive_interception_touchdowns = ncaa_game.home_stats.defensive_interception_touchdowns
            home_defense.pass_breakups = ncaa_game.home_stats.pass_breakups
            home_defense.fumbles_forced = ncaa_game.home_stats.fumbles_forced
            home_defense.fumbles_number = ncaa_game.home_stats.fumbles_number
            home_defense.fumbles_yards = ncaa_game.home_stats.fumbles_yards
            home_defense.fumbles_touchdowns = ncaa_game.home_stats.fumbles_touchdowns

            home_defense.save()
            print "Home Defense: %s" % home_defense

            # visiting team offense
            visitor_time = ncaa_game.visitor_stats.time_of_possession.split(":") or None
            if visitor == game.team2:
                visiting_offense, created = GameOffense.objects.get_or_create(game=game_v, team=visitor)
            else:
                visiting_offense, created = GameOffense.objects.get_or_create(game=game, team=visitor)

            if game.date.year > 2006:
                visiting_offense.time_of_possession=datetime.time(0, int(visitor_time[0]), int(visitor_time[1]))
            else:
                visiting_offense.time_of_possession=None

            visiting_offense.third_down_attempts=ncaa_game.visitor_stats.third_down_attempts
            visiting_offense.third_down_conversions=ncaa_game.visitor_stats.third_down_conversions
            visiting_offense.fourth_down_attempts=ncaa_game.visitor_stats.fourth_down_attempts
            visiting_offense.fourth_down_conversions=ncaa_game.visitor_stats.fourth_down_conversions
            visiting_offense.first_downs_rushing=ncaa_game.visitor_stats.first_downs_rushing
            visiting_offense.first_downs_passing=ncaa_game.visitor_stats.first_downs_passing
            visiting_offense.first_downs_penalty=ncaa_game.visitor_stats.first_downs_penalty
            visiting_offense.first_downs_total=ncaa_game.visitor_stats.first_downs_total
            visiting_offense.penalties=ncaa_game.visitor_stats.penalties
            visiting_offense.penalty_yards=ncaa_game.visitor_stats.penalty_yards
            visiting_offense.fumbles=ncaa_game.visitor_stats.fumbles
            visiting_offense.fumbles_lost=ncaa_game.visitor_stats.fumbles_lost
            visiting_offense.rushes=ncaa_game.visitor_stats.rushes
            visiting_offense.rush_gain=ncaa_game.visitor_stats.rush_gain
            visiting_offense.rush_loss=ncaa_game.visitor_stats.rush_loss
            visiting_offense.rush_net=ncaa_game.visitor_stats.rush_net
            visiting_offense.rush_touchdowns=ncaa_game.visitor_stats.rush_touchdowns
            visiting_offense.total_plays=ncaa_game.visitor_stats.total_plays
            visiting_offense.total_yards=ncaa_game.visitor_stats.total_yards
            visiting_offense.pass_attempts=ncaa_game.visitor_stats.pass_attempts
            visiting_offense.pass_completions=ncaa_game.visitor_stats.pass_completions
            visiting_offense.pass_interceptions=ncaa_game.visitor_stats.pass_interceptions
            visiting_offense.pass_yards=ncaa_game.visitor_stats.pass_yards
            visiting_offense.pass_touchdowns=ncaa_game.visitor_stats.pass_touchdowns
            visiting_offense.receptions=ncaa_game.visitor_stats.receptions
            visiting_offense.receiving_yards=ncaa_game.visitor_stats.receiving_yards
            visiting_offense.receiving_touchdowns=ncaa_game.visitor_stats.receiving_touchdowns
            visiting_offense.punts=ncaa_game.visitor_stats.punts
            visiting_offense.punt_yards=ncaa_game.visitor_stats.punt_yards
            visiting_offense.punt_returns=ncaa_game.visitor_stats.punt_returns
            visiting_offense.punt_return_yards=ncaa_game.visitor_stats.punt_return_yards
            visiting_offense.punt_return_touchdowns=ncaa_game.visitor_stats.punt_return_touchdowns
            visiting_offense.kickoff_returns=ncaa_game.visitor_stats.kickoff_returns
            visiting_offense.kickoff_return_yards=ncaa_game.visitor_stats.kickoff_return_yards
            visiting_offense.kickoff_return_touchdowns=ncaa_game.visitor_stats.kickoff_return_touchdowns
            visiting_offense.touchdowns=ncaa_game.visitor_stats.touchdowns
            visiting_offense.pat_attempts=ncaa_game.visitor_stats.pat_attempts
            visiting_offense.pat_made=ncaa_game.visitor_stats.pat_made
            visiting_offense.two_point_conversion_attempts=ncaa_game.visitor_stats.two_point_conversion_attempts
            visiting_offense.two_point_conversions=ncaa_game.visitor_stats.two_point_conversions
            visiting_offense.field_goal_attempts=ncaa_game.visitor_stats.field_goal_attempts
            visiting_offense.field_goals_made=ncaa_game.visitor_stats.field_goals_made
            visiting_offense.points=ncaa_game.visitor_stats.points

            visiting_offense.save()
            print "Visiting Offense: %s" % visiting_offense

            # visiting team defense
            if visitor == game.team2:
                visiting_defense, created = GameDefense.objects.get_or_create(game = game_v, team = game.team2)
            else:
                visiting_defense, created = GameDefense.objects.get_or_create(game = game, team = game.team2)

            visiting_defense.safeties = ncaa_game.visitor_stats.safeties
            visiting_defense.unassisted_tackles = ncaa_game.visitor_stats.unassisted_tackles
            visiting_defense.assisted_tackles = ncaa_game.visitor_stats.assisted_tackles
            visiting_defense.unassisted_tackles_for_loss = ncaa_game.visitor_stats.unassisted_tackles_for_loss
            visiting_defense.assisted_tackles_for_loss = ncaa_game.visitor_stats.assisted_tackles_for_loss
            visiting_defense.tackles_for_loss_yards = ncaa_game.visitor_stats.tackles_for_loss_yards
            visiting_defense.unassisted_sacks = ncaa_game.visitor_stats.unassisted_sacks
            visiting_defense.assisted_sacks = ncaa_game.visitor_stats.assisted_sacks
            visiting_defense.sack_yards = ncaa_game.visitor_stats.sack_yards
            visiting_defense.defensive_interceptions = ncaa_game.visitor_stats.defensive_interceptions
            visiting_defense.defensive_interception_yards = ncaa_game.visitor_stats.defensive_interception_yards
            visiting_defense.defensive_interception_touchdowns = ncaa_game.visitor_stats.defensive_interception_touchdowns
            visiting_defense.pass_breakups = ncaa_game.visitor_stats.pass_breakups
            visiting_defense.fumbles_forced = ncaa_game.visitor_stats.fumbles_forced
            visiting_defense.fumbles_number = ncaa_game.visitor_stats.fumbles_number
            visiting_defense.fumbles_yards = ncaa_game.visitor_stats.fumbles_yards
            visiting_defense.fumbles_touchdowns = ncaa_game.visitor_stats.fumbles_touchdowns

            visiting_defense.save()
            print "Visiting Defense: %s" % visiting_defense

            game.has_stats = True
            game.save()
            game_v.has_stats = True
            game_v.save()
            print "================================\n"

    except:
        print str(game.id) + ": Could not find game between %s and %s on %s" % (game.team1.college.name, game.team2.college.name, game.date)
        game.ncaa_xml = None
        game.save()
        raise

def game_drive_loader(game):
    """
    Accepts a single Game instance and scrapes a page containing drive information for both teams if the game's
    has_stats attribute is False. Some drive lists have improperly coded final drives, which can cause errors.
    >>> game = Game.objects.get(id=793)
    >>> game_drive_loader(game)
    """
    if game.has_drives == False:
        print game.get_ncaa_drive_url().strip()
        contents = urllib.urlopen(game.get_ncaa_drive_url().strip()).read()
        soup = BeautifulSoup(contents)
        rows = soup.findAll('table')[1].findAll("tr")[2:] # grabbing too many rows. need to tighten.
        for row in rows:
            cells = row.findAll('td')
            drive = int(cells[0].find("a").contents[0])
            slug = slugify(cells[2].contents[0])
            print slug
            try:
                team = CollegeYear.objects.get(season=game.season, college__slug=slug)
            except:
                team = CollegeYear.objects.get(season=game.season, college__drive_slug=str(cells[2].contents[0]))
            quarter = int(cells[1].contents[0])
            start_how = cells[3].contents[0]
            start_time = datetime.time(0, int(cells[4].contents[0].split(":")[0]), int(cells[4].contents[0].split(":")[1][:2]))
            try:
                start_position = int(cells[5].contents[0])
                start_side = "O"
            except:
                try:
                    start_position = int(cells[5].contents[0].split(" ")[1])
                    start_side = 'P'
                except:
                    start_position = 0
                    start_side = 'O'
            try:
                end_result = DriveOutcome.objects.get(abbrev=str(cells[6].contents[0]))
            except:
                continue
            end_time = datetime.time(0, int(cells[7].contents[0].split(":")[0]), int(cells[7].contents[0].split(":")[1]))
            if cells[8].contents and str(cells[8].contents[0]) != 'null':
                try:
                    end_position = int(cells[8].contents[0])
                    end_side = "O"
                except:
                    end_position = int(cells[8].contents[0].split(" ")[1])
                    end_side = 'P'
            else:
                end_position = None
                end_side = 'P'
            plays = int(cells[9].contents[0])
            yards = int(cells[10].contents[0])
            time_of_possession = datetime.time(0, int(cells[11].contents[0].split(":")[0]), int(cells[11].contents[0].split(":")[1]))
            try:
                d, created = GameDrive.objects.get_or_create(game=game, drive=drive, team=team, quarter=quarter,start_how=str(start_how), start_time=start_time, start_position=start_position, start_side=start_side, end_result=end_result, end_time=end_time, end_position=end_position, end_side=end_side, plays=plays, yards=yards,time_of_possession=time_of_possession, season=game.season)
            except:
                print "Could not save drive %s, %s, %s" % (drive, game, team)
        game.has_drives = True
        game.save()

def game_scores_loader(game):
    contents = urllib.urlopen(game.get_ncaa_scoring_url().strip()).read()
    soup = BeautifulSoup(contents)
    scores = soup.findAll('li')
    for score in scores:
        score_text = score.find('a').text
        slug = score_text.split(':', 2)[1].split(' ',2)[2]
        team = CollegeYear.objects.get(season=game.season, college__drive_slug=slug)
        s, created = GameScore.objects.get_or_create(game=game, team=team, season=game.season, description=score_text)
    game.has_scores = True
    game.save()    
    

def player_game_stats(game):
    """
    Accepts a single instance of Game and parses the game XML file for player stats if the game's has_player_stats
    attribute is False. As with the game stats parser, the elements that contain a space are first replaced with a 0.
    Not all players have both offensive and defensive stats, but this function checks for both.
    >>> game = Game.objects.get(id=793)
    >>> player_game_stats(game)
    """
    if not game.has_player_stats:
        html = urllib.urlopen(game.get_ncaa_xml_url()).read()
        soup = BeautifulSoup(html)
        f = soup.findAll(text="&#160;")
        for each in f:
            each.replaceWith("0")
        if game.t1_game_type != 'A':
            try:
                team = CollegeYear.objects.get(season=game.season, college__id=int(soup.teams.home.orgid.contents[0]))
                players = soup.teams.home.players.findAll('player')
            except:
                players = None
                pass
        else:
            try:
                team = CollegeYear.objects.get(season=game.season, college__id=int(soup.teams.visitor.orgid.contents[0]))
                players = soup.teams.visitor.players.findAll('player')
            except:
                players = None
                pass
        if players and team.college.updated == True:
            for p in players:
                uniform = str(p.find("uniform").contents[0])
                name = str(p.find("name").contents[0])
                try:
                    player = Player.objects.get(team=team, season=game.season, name=name, number=uniform)
                except:
                    player = None
                    pass
                if player:
                    if p.find("totplays"):
                        total_plays=p.find("totplays").contents[0]
                    else:
                        total_plays=None
                    if p.find("totyards"):
                        total_yards=p.find("totyards").contents[0]
                    else:
                        total_yards=None
                    if p.find("starter"):
                        starter = int(p.find("starter").contents[0])
                    else:
                        starter = False
                    pg, created = PlayerGame.objects.get_or_create(player=player, game=game, played=True, total_plays=total_plays, total_yards=total_yards, starter=starter)
                    if p.find("tackles"):
                        un_t = int(p.find("tackles").find("uatackles").contents[0])
                        a_t = int(p.find("tackles").find("atackles").contents[0])
                        pt, created = PlayerTackle.objects.get_or_create(player=player, game=game, unassisted_tackles=un_t, assisted_tackles=a_t)
                    if p.find("tfl"):
                        un_tfl = int(p.find("tfl").find("uatfl").contents[0])
                        a_tfl = int(p.find("tfl").find("atfl").contents[0])
                        tfl_yards = int(p.find("tfl").find("tflyards").contents[0])
                        un_sacks = int(p.find("tfl").find("uasacks").contents[0])
                        a_sacks = int(p.find("tfl").find("asacks").contents[0])
                        sack_yards = int(p.find("tfl").find("sackyards").contents[0])
                        ptfl, created = PlayerTacklesLoss.objects.get_or_create(player=player, game=game, unassisted_tackles_for_loss=un_tfl, assisted_tackles_for_loss=a_tfl, tackles_for_loss_yards=tfl_yards, unassisted_sacks=un_sacks, assisted_sacks=a_sacks,sack_yards=sack_yards)
                    if p.find("passdefense"):
                        int_no = int(p.find("passdefense").find("intnumber").contents[0])
                        int_yards = int(p.find("passdefense").find("intyards").contents[0])
                        int_td = int(p.find("passdefense").find("inttd").contents[0])
                        p_b = int(p.find("passdefense").find("passbreakups").contents[0])
                        pd, created = PlayerPassDefense.objects.get_or_create(player=player, game=game, interceptions=int_no, interception_yards=int_yards, interception_td=int_td, pass_breakups=p_b)
                    if p.find("fumbles"):
                        f_f = int(p.find("fumbles").find("fumblesforced").contents[0])
                        f_n = int(p.find("fumbles").find("fumblesnumber").contents[0])
                        f_y = int(p.find("fumbles").find("fumblesyards").contents[0])
                        f_t = int(p.find("fumbles").find("fumblestd").contents[0])
                        pf, created = PlayerFumble.objects.get_or_create(player=player, game=game, fumbles_forced=f_f, fumbles_number=f_n, fumbles_yards=f_y, fumbles_td=f_t)
                    if p.find("returns"):
                        p_r = int(p.find("returns").find("puntnumber").contents[0])
                        p_y = int(p.find("returns").find("puntyards").contents[0])
                        p_t = int(p.find("returns").find("punttd").contents[0])
                        ko_n = int(p.find("returns").find("konumber").contents[0])
                        ko_y = int(p.find("returns").find("koyards").contents[0])
                        ko_t = int(p.find("returns").find("kotd").contents[0])
                        pr, created = PlayerReturn.objects.get_or_create(player=player, game=game, punt_returns=p_r, punt_return_yards=p_y, punt_return_td=p_t, kickoff_returns=ko_n, kickoff_return_yards=ko_y, kickoff_return_td=ko_t)
                    if p.find("rushing"):
                        r_n = int(p.find("rushing").find("number").contents[0])
                        r_g = int(p.find("rushing").find("gain").contents[0])
                        r_l = int(p.find("rushing").find("loss").contents[0])
                        r_net = int(p.find("rushing").find("net").contents[0])
                        r_t = int(p.find("rushing").find("td").contents[0])
                        r_long = int(p.find("rushing").find("long").contents[0])
                        try:
                            r_avg = float(p.find("rushing").find("avg").contents[0])
                        except:
                            r_avg = None
                        r_tp = int(p.find("rushing").find("totplays").contents[0])
                        r_ty = int(p.find("rushing").find("totyards").contents[0])
                        pr, created = PlayerRush.objects.get_or_create(player=player, game=game, rushes=r_n, gain=r_g, loss=r_l, net=r_net, td=r_t, long_yards=r_long, average=r_avg, total_plays=r_tp, total_yards=r_ty)
                    if p.find("passing"):
                        p_att = int(p.find("passing").find("att").contents[0])
                        p_comp = int(p.find("passing").find("comp").contents[0])
                        p_int = int(p.find("passing").find("int").contents[0])
                        p_yards = int(p.find("passing").find("yards").contents[0])
                        p_td = int(p.find("passing").find("td").contents[0])
                        p_conv = int(p.find("passing").find("conv").contents[0])
                        p_tp = int(p.find("passing").find("totplays").contents[0])
                        p_ty = int(p.find("passing").find("totyards").contents[0])
                        p_eff = float(p.find("passing").find("passeff").contents[0])
                        pp, created = PlayerPass.objects.get_or_create(player=player, game=game, attempts=p_att, completions=p_comp, interceptions=p_int, yards=p_yards, td=p_td, conversions=p_conv, total_plays=p_tp, total_yards=p_ty, pass_efficiency=p_eff)
                    if p.find("receiving"):
                        r_number = int(p.find("receiving").find("number").contents[0])
                        r_yards = int(p.find("receiving").find("yards").contents[0])
                        r_td = int(p.find("receiving").find("td").contents[0])
                        r_lg = int(p.find("receiving").find("long").contents[0])
                        if p.find("receiving").find("avg"):
                            r_ag = float(p.find("receiving").find("avg").contents[0])
                        else:
                            r_ag = 0.0
                        prr, created = PlayerReceiving.objects.get_or_create(player=player, game=game, receptions=r_number, yards=r_yards, td=r_td, long_yards=r_lg, average=r_ag)
                    if p.find("scoring"):
                        s_td = int(p.find("scoring").find("td").contents[0])
                        fg_att = int(p.find("scoring").find("fgatt").contents[0])
                        fg_made = int(p.find("scoring").find("fgmade").contents[0])
                        pat_att = int(p.find("scoring").find("offkickatt").contents[0])
                        pat_made = int(p.find("scoring").find("offkickmade").contents[0])
                        tpt_att = int(p.find("scoring").find("offrpatt").contents[0])
                        tpt_made = int(p.find("scoring").find("offrpmade").contents[0])
                        d_pat_att = int(p.find("scoring").find("defkickatt").contents[0])
                        d_pat_made = int(p.find("scoring").find("defkickmade").contents[0])
                        d_tpt_att = int(p.find("scoring").find("defrpatt").contents[0])
                        d_tpt_made = int(p.find("scoring").find("defrpmade").contents[0])
                        saf = int(p.find("scoring").find("saf").contents[0])
                        pts = int(p.find("scoring").find("pts").contents[0])
                        ps, created = PlayerScoring.objects.get_or_create(player=player, game=game, td=s_td, fg_att=fg_att, fg_made=fg_made, pat_att=pat_att, pat_made=pat_made, two_pt_att=tpt_att, two_pt_made=tpt_made,def_pat_att=d_pat_att, def_pat_made=d_pat_made, def_two_pt_att=d_tpt_att, def_two_pt_made=d_tpt_made, safeties=saf, points=pts)
        game.has_player_stats = True
        game.save()

