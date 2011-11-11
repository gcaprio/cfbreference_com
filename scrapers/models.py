from lxml import etree
from datetime import datetime

class Utils(object):
    @staticmethod
    def clean_get(input):
        if input == u"\xa0":
            return "0"
        return input

class NCAAGameTeamStats(object):
    game_xml = None

    team_side_string = ""

    def get_xpath_statement(self, xpath):
        return xpath % self.team_side_string

    @property
    def quarters(self):
        return self.game_xml.findall(self.get_xpath_statement("/SCORE/%s/QUARTERS/QUARTER"))

    @property
    def time_of_possession(self):
        return self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOP")).text

    @property
    def third_down_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/THIRDDOWNS/ATT")).text))

    @property
    def third_down_conversions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/THIRDDOWNS/CONV")).text))

    @property
    def fourth_down_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FOURTHDOWNS/ATT")).text))

    @property
    def fourth_down_conversions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FOURTHDOWNS/CONV")).text))

    @property
    def first_downs_rushing(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FIRSTDOWNS/RUSH")).text))

    @property
    def first_downs_passing(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FIRSTDOWNS/PASS")).text))
    @property
    def first_downs_penalty(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FIRSTDOWNS/PENALTY")).text))
    @property
    def first_downs_total(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FIRSTDOWNS/TOTAL")).text))
    @property
    def penalties(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/PENALTIES/NUMBER")).text))
    @property
    def penalty_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/PENALTIES/YARDS")).text))
    @property
    def fumbles(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FUMBLES/NUMBER")).text))
    @property
    def fumbles_lost(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/FUMBLES/LOST")).text))
    @property
    def rushes(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/NUMBER")).text))
    @property
    def rush_gain(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/GAIN")).text))
    @property
    def rush_loss(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/LOSS")).text))
    @property
    def rush_net(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/NET")).text))
    @property
    def rush_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/TD")).text))
    @property
    def total_plays(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/TOTPLAYS")).text))
    @property
    def total_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RUSHING/TOTYARDS")).text))
    @property
    def pass_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSING/ATT")).text))
    @property
    def pass_completions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSING/COMP")).text))
    @property
    def pass_interceptions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSING/INT")).text))
    @property
    def pass_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSING/YARDS")).text))
    @property
    def pass_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSING/TD")).text))
    @property
    def receptions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RECEIVING/NUMBER")).text))
    @property
    def receiving_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RECEIVING/YARDS")).text))
    @property
    def receiving_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RECEIVING/TD")).text))
    @property
    def punts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PUNT/NUMBER")).text))
    @property
    def punt_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PUNT/YARDS")).text))
    @property
    def punt_returns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/PUNTNUMBER")).text))
    @property
    def punt_return_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/PUNTYARDS")).text))
    @property
    def punt_return_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/PUNTTD")).text))
    @property
    def kickoff_returns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/KONUMBER")).text))
    @property
    def kickoff_return_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/KOYARDS")).text))
    @property
    def kickoff_return_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/RETURNS/KOTD")).text))
    @property
    def touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/TD")).text))
    @property
    def pat_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/OFFKICKATT")).text))
    @property
    def pat_made(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/OFFKICKMADE")).text))
    @property
    def two_point_conversion_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/OFFRPATT")).text))
    @property
    def two_point_conversions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/OFFRPMADE")).text))
    @property
    def field_goal_attempts(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/FGATT")).text))
    @property
    def field_goals_made(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/FGMADE")).text))
    @property
    def points(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/PTS")).text))

    @property
    def safeties(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/SCORING/SAF")).text))
    @property
    def unassisted_tackles(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TACKLES/UATACKLES")).text))

    @property
    def assisted_tackles(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TACKLES/ATACKLES")).text))

    @property
    def unassisted_tackles_for_loss(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/UATFL")).text))

    @property
    def assisted_tackles_for_loss(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/ATFL")).text))

    @property
    def tackles_for_loss_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/TFLYARDS")).text))

    @property
    def unassisted_sacks(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/UASACKS")).text))

    @property
    def assisted_sacks(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/ASACKS")).text))

    @property
    def sack_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/TFL/SACKYARDS")).text))

    @property
    def defensive_interceptions(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSDEFENSE/INTNUMBER")).text))

    @property
    def defensive_interception_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSDEFENSE/INTYARDS")).text))

    @property
    def defensive_interception_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSDEFENSE/INTTD")).text))
    @property
    def pass_breakups(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/PASSDEFENSE/PASSBREAKUPS")).text))
    @property
    def fumbles_forced(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/FUMBLES/FUMBLESFORCED")).text))
    @property
    def fumbles_number(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/FUMBLES/FUMBLESNUMBER")).text))

    @property
    def fumbles_yards(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/FUMBLES/FUMBLESYARDS")).text))

    @property
    def fumbles_touchdowns(self):
        return int(Utils.clean_get(self.game_xml.find(self.get_xpath_statement("/TEAMS/%s/TOTALS/FUMBLES/FUMBLESTD")).text))

    def __init__(self, game_xml, team_side_string):
       self.game_xml = game_xml
       self.team_side_string = team_side_string

class NCAAGame(object):

    game_xml = None

    home_stats = None
    visitor_stats = None
    
    @property
    def attendance(self):
        return Utils.clean_get(self.game_xml.find("//ATTENDANCE").text)

    @property
    def duration(self):
        return Utils.clean_get(self.game_xml.find("//DURATION").text)

    @property
    def duration_timespan(self):
        duration_hours, duration_minutes = ncaa_game.duration.split(":")
        return datetime.time(int(duration_hours), int(duration_minutes), 0)

    def __init__(self, game_xml):
        self.game_xml = game_xml
        self.create_stats()

    def __init__(self, game_xml_file):
        self.game_xml = etree.parse(game_xml_file)
        self.create_stats()

    def create_stats(self):
        self.home_stats = NCAAGameTeamStats(self.game_xml, "HOME")
        self.visitor_stats = NCAAGameTeamStats(self.game_xml, "VISITOR")

