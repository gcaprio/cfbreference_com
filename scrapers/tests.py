import unittest

from lxml import etree
from models import NCAAGame

class ScrapersTestCase(unittest.TestCase):
    def clean_get(self, input):
        if input == u"\xa0":
            return "0"
        return input

    def testLoadingGameFromXML(self):
        ncaa_game = NCAAGame("fixtures/akron_vs_gardner-webb.xml")

        self.assertEqual("10046", ncaa_game.attendance)
        self.assertEqual(10046, int(ncaa_game.attendance))

        self.assertEqual("3:15", ncaa_game.duration)

        duration_hours, duration_minutes = ncaa_game.duration.split(":")
        self.assertEqual("3", duration_hours)
        self.assertEqual("15", duration_minutes)

        self.assertEquals(3, int(duration_hours))
        self.assertEquals(15, int(duration_minutes))

        self.assertEqual(6, len(ncaa_game.visitor_stats.quarters))

        self.assertEqual(6, len(ncaa_game.home_stats.quarters))

        home_top = ncaa_game.home_stats.time_of_possession.split(":") or None
        visitor_top = ncaa_game.visitor_stats.time_of_possession.split(":") or None

        self.assertEqual(2, len(home_top))
        self.assertEqual("29", home_top[0])
        self.assertEqual(29, int(home_top[0]))
        self.assertEqual("34", home_top[1])
        self.assertEqual(34, int(home_top[1]))

        self.assertEqual(2, len(visitor_top))
        self.assertEqual("30", visitor_top[0])
        self.assertEqual(30, int(visitor_top[0]))
        self.assertEqual("26", visitor_top[1])
        self.assertEqual(26, int(visitor_top[1]))

        self.assertEqual(12, ncaa_game.home_stats.third_down_attempts)
        self.assertEqual(6, ncaa_game.home_stats.third_down_conversions)

        self.assertEqual(1, ncaa_game.home_stats.fourth_down_attempts)
        self.assertEqual(1, ncaa_game.home_stats.fourth_down_conversions)

        self.assertEqual(13, ncaa_game.home_stats.first_downs_rushing)
        self.assertEqual(8, ncaa_game.home_stats.first_downs_passing)
        self.assertEqual(1, ncaa_game.home_stats.first_downs_penalty)
        self.assertEqual(22, ncaa_game.home_stats.first_downs_total)

        self.assertEqual(5, ncaa_game.home_stats.penalties)
        self.assertEqual(50, ncaa_game.home_stats.penalty_yards)

        self.assertEqual(3, ncaa_game.home_stats.fumbles)
        self.assertEqual(1, ncaa_game.home_stats.fumbles_lost)

        self.assertEqual(44, ncaa_game.home_stats.rushes)
        self.assertEqual(235, ncaa_game.home_stats.rush_gain)
        self.assertEqual(11, ncaa_game.home_stats.rush_loss)
        self.assertEqual(224, ncaa_game.home_stats.rush_net)
        self.assertEqual(4, ncaa_game.home_stats.rush_touchdowns)
        self.assertEqual(65, ncaa_game.home_stats.total_plays)
        self.assertEqual(389, ncaa_game.home_stats.total_yards)

        self.assertEqual(21, ncaa_game.home_stats.pass_attempts)
        self.assertEqual(14, ncaa_game.home_stats.pass_completions)
        self.assertEqual(1, ncaa_game.home_stats.pass_interceptions)
        self.assertEqual(165, ncaa_game.home_stats.pass_yards)
        self.assertEqual(1, ncaa_game.home_stats.pass_touchdowns)

        self.assertEqual(14, ncaa_game.home_stats.receptions)
        self.assertEqual(165, ncaa_game.home_stats.receiving_yards)
        self.assertEqual(1, ncaa_game.home_stats.receiving_touchdowns)

        self.assertEqual(3, ncaa_game.home_stats.punts)
        self.assertEqual(103, ncaa_game.home_stats.punt_yards)

        self.assertEqual(5, ncaa_game.home_stats.punt_returns)
        self.assertEqual(120, ncaa_game.home_stats.punt_return_yards)
        self.assertEqual(0, ncaa_game.home_stats.punt_return_touchdowns)
        self.assertEqual(2, ncaa_game.home_stats.kickoff_returns)
        self.assertEqual(15, ncaa_game.home_stats.kickoff_return_yards)
        self.assertEqual(0, ncaa_game.home_stats.kickoff_return_touchdowns)

        self.assertEqual(5, ncaa_game.home_stats.touchdowns)
        self.assertEqual(5, ncaa_game.home_stats.pat_attempts)
        self.assertEqual(4, ncaa_game.home_stats.pat_made)
        self.assertEqual(0, ncaa_game.home_stats.two_point_conversion_attempts)
        self.assertEqual(0, ncaa_game.home_stats.two_point_conversions)
        self.assertEqual(2, ncaa_game.home_stats.field_goal_attempts)
        self.assertEqual(1, ncaa_game.home_stats.field_goals_made)
        self.assertEqual(37, ncaa_game.home_stats.points)
        self.assertEqual(0, ncaa_game.home_stats.safeties)

        self.assertEqual(42, ncaa_game.home_stats.unassisted_tackles)
        self.assertEqual(33, ncaa_game.home_stats.assisted_tackles)

        self.assertEqual(4, ncaa_game.home_stats.unassisted_tackles_for_loss)
        self.assertEqual(4, ncaa_game.home_stats.assisted_tackles_for_loss)
        self.assertEqual(19, ncaa_game.home_stats.tackles_for_loss_yards)
        self.assertEqual(0, ncaa_game.home_stats.unassisted_sacks)
        self.assertEqual(0, ncaa_game.home_stats.assisted_sacks)
        self.assertEqual(15, ncaa_game.home_stats.sack_yards)

        self.assertEqual(1, ncaa_game.home_stats.defensive_interceptions)
        self.assertEqual(12, ncaa_game.home_stats.defensive_interception_yards)
        self.assertEqual(0, ncaa_game.home_stats.defensive_interception_touchdowns)
        self.assertEqual(3, ncaa_game.home_stats.pass_breakups)

        self.assertEqual(1, ncaa_game.home_stats.fumbles_forced)
        self.assertEqual(0, ncaa_game.home_stats.fumbles_number)
        self.assertEqual(0, ncaa_game.home_stats.fumbles_yards)
        self.assertEqual(0, ncaa_game.home_stats.fumbles_touchdowns)

        # Visitor Stats
        self.assertEqual(20, ncaa_game.visitor_stats.third_down_attempts)
        self.assertEqual(11, ncaa_game.visitor_stats.third_down_conversions)

        self.assertEqual(1, ncaa_game.visitor_stats.fourth_down_attempts)
        self.assertEqual(1, ncaa_game.visitor_stats.fourth_down_conversions)

        self.assertEqual(8, ncaa_game.visitor_stats.first_downs_rushing)
        self.assertEqual(14, ncaa_game.visitor_stats.first_downs_passing)
        self.assertEqual(2, ncaa_game.visitor_stats.first_downs_penalty)
        self.assertEqual(24, ncaa_game.visitor_stats.first_downs_total)

        self.assertEqual(2, ncaa_game.visitor_stats.penalties)
        self.assertEqual(30, ncaa_game.visitor_stats.penalty_yards)

        self.assertEqual(1, ncaa_game.visitor_stats.fumbles)
        self.assertEqual(0, ncaa_game.visitor_stats.fumbles_lost)

        self.assertEqual(37, ncaa_game.visitor_stats.rushes)
        self.assertEqual(122, ncaa_game.visitor_stats.rush_gain)
        self.assertEqual(21, ncaa_game.visitor_stats.rush_loss)
        self.assertEqual(101, ncaa_game.visitor_stats.rush_net)
        self.assertEqual(2, ncaa_game.visitor_stats.rush_touchdowns)
        self.assertEqual(80, ncaa_game.visitor_stats.total_plays)
        self.assertEqual(391, ncaa_game.visitor_stats.total_yards)

        self.assertEqual(43, ncaa_game.visitor_stats.pass_attempts)
        self.assertEqual(25, ncaa_game.visitor_stats.pass_completions)
        self.assertEqual(1, ncaa_game.visitor_stats.pass_interceptions)
        self.assertEqual(290, ncaa_game.visitor_stats.pass_yards)
        self.assertEqual(3, ncaa_game.visitor_stats.pass_touchdowns)

        self.assertEqual(25, ncaa_game.visitor_stats.receptions)
        self.assertEqual(290, ncaa_game.visitor_stats.receiving_yards)
        self.assertEqual(3, ncaa_game.visitor_stats.receiving_touchdowns)

        self.assertEqual(6, ncaa_game.visitor_stats.punts)
        self.assertEqual(223, ncaa_game.visitor_stats.punt_yards)

        self.assertEqual(4, ncaa_game.visitor_stats.punt_returns)
        self.assertEqual(74, ncaa_game.visitor_stats.punt_return_yards)
        self.assertEqual(0, ncaa_game.visitor_stats.punt_return_touchdowns)
        self.assertEqual(0, ncaa_game.visitor_stats.kickoff_returns)
        self.assertEqual(0, ncaa_game.visitor_stats.kickoff_return_yards)
        self.assertEqual(0, ncaa_game.visitor_stats.kickoff_return_touchdowns)

        self.assertEqual(5, ncaa_game.visitor_stats.touchdowns)
        self.assertEqual(5, ncaa_game.visitor_stats.pat_attempts)
        self.assertEqual(5, ncaa_game.visitor_stats.pat_made)
        self.assertEqual(0, ncaa_game.visitor_stats.two_point_conversion_attempts)
        self.assertEqual(0, ncaa_game.visitor_stats.two_point_conversions)
        self.assertEqual(1, ncaa_game.visitor_stats.field_goal_attempts)
        self.assertEqual(1, ncaa_game.visitor_stats.field_goals_made)
        self.assertEqual(38, ncaa_game.visitor_stats.points)
        self.assertEqual(0, ncaa_game.visitor_stats.safeties)

        self.assertEqual(46, ncaa_game.visitor_stats.unassisted_tackles)
        self.assertEqual(22, ncaa_game.visitor_stats.assisted_tackles)

        self.assertEqual(5, ncaa_game.visitor_stats.unassisted_tackles_for_loss)
        self.assertEqual(2, ncaa_game.visitor_stats.assisted_tackles_for_loss)
        self.assertEqual(10, ncaa_game.visitor_stats.tackles_for_loss_yards)
        self.assertEqual(0, ncaa_game.visitor_stats.unassisted_sacks)
        self.assertEqual(0, ncaa_game.visitor_stats.assisted_sacks)
        self.assertEqual(6, ncaa_game.visitor_stats.sack_yards)

        self.assertEqual(1, ncaa_game.visitor_stats.defensive_interceptions)
        self.assertEqual(17, ncaa_game.visitor_stats.defensive_interception_yards)
        self.assertEqual(0, ncaa_game.visitor_stats.defensive_interception_touchdowns)
        self.assertEqual(1, ncaa_game.visitor_stats.pass_breakups)

        self.assertEqual(2, ncaa_game.visitor_stats.fumbles_forced)
        self.assertEqual(0, ncaa_game.visitor_stats.fumbles_number)
        self.assertEqual(0, ncaa_game.visitor_stats.fumbles_yards)
        self.assertEqual(0, ncaa_game.visitor_stats.fumbles_touchdowns)