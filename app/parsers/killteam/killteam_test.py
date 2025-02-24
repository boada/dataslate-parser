from unittest import TestCase
from pathlib import Path
from app.utils.test_utils import fetch_and_parse_roster
from os import listdir
from os.path import isfile, join


class KillteamTest(TestCase):
    def setUp(self):
        self.base_path = Path.cwd() / "test_rosters" / "kill_team"
        self.chaos_kill_team_standard = str(self.base_path / "chaos_roster.ros")
        self.death_guard_kill_team_with_commander = str(
            self.base_path / "death_guard_with_commander.ros"
        )
        self.ability_example_name = "Death to the False Emperor"
        self.gametype = "killteam"
        self.new_bs_format = str(self.base_path / "test_roster_chaos_new.ros")
        self.commander_roster = str(self.base_path / "test_roster_commander.ros")
        self.psyker_roster = str(self.base_path / "psychic_roster_kt.ros")

    def test__killteam_loop_through_test_folder_and_parse(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse without errors
        expected: successfully parses all roster files in the test folder
        """
        parsed_rosters = []
        list_of_rosters = [
            file
            for file in listdir(str(self.base_path))
            if isfile(join(str(self.base_path), file))
        ]

        for roster in list_of_rosters:
            parsed_roster = fetch_and_parse_roster(
                roster_file=str(self.base_path) + "/" + roster
            )
            parsed_rosters.append(parsed_roster)

        self.assertTrue(parsed_rosters)

    def test__new_bs_format(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse without errors
        expected: successfully parses a single roster without errors
        """
        parsed_roster = fetch_and_parse_roster(roster_file=self.new_bs_format)
        self.assertTrue(parsed_roster)

    def test__chaos_test_roster_parses_13_models(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse without errors
        expected: successfully parses 13 units
        """
        parsed_roster = fetch_and_parse_roster(roster_file=self.new_bs_format)
        self.assertTrue(len(parsed_roster), 13)

    def test__aspiring_champion_parsed_correctly(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse without errors
        expected: parsed an aspiring champion correctly
        """
        parsed_roster = fetch_and_parse_roster(roster_file=self.new_bs_format)
        aspiring_champion = parsed_roster[0]
        self.assertEqual(len(aspiring_champion.abilities), 3)
        self.assertEqual(aspiring_champion.attacks, "2")
        self.assertEqual(aspiring_champion.ballistic_skill, "3+")
        self.assertEqual(aspiring_champion.leadership, "8")
        self.assertEqual(aspiring_champion.max_allowed, "1")
        self.assertEqual(aspiring_champion.movement, '6"')
        self.assertEqual(aspiring_champion.name, "Aspiring Champion")
        self.assertEqual(aspiring_champion.point_cost, 18.0)
        self.assertEqual(aspiring_champion.save, "3+")
        self.assertEqual(aspiring_champion.strength, "4")
        self.assertEqual(len(aspiring_champion.wargear), 5)
        self.assertEqual(aspiring_champion.weapon_skill, "3+")
        self.assertEqual(aspiring_champion.wounds, "1")

    def test__aspiring_champion_parsed_wargear_correctly(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse without errors
        expected: parsed an aspiring champion correctly
        """
        parsed_roster = fetch_and_parse_roster(roster_file=self.new_bs_format)
        aspiring_champion = parsed_roster[0]
        self.assertTrue(aspiring_champion.wargear.get("Power fist"))
        self.assertTrue(aspiring_champion.wargear.get("Frag grenade"))
        self.assertTrue(aspiring_champion.wargear.get("Krak grenade"))
        self.assertTrue(aspiring_champion.wargear.get("Plasma pistol - Standard"))
        self.assertTrue(aspiring_champion.wargear.get("Plasma pistol - Supercharge"))

    def test__commander_roster(self):
        parsed_roster = fetch_and_parse_roster(roster_file=self.commander_roster)
        self.assertTrue(parsed_roster)

    def test__psyker_roster(self):
        """
        method: fetch_and_parse_roster(killteam)
        prerequisite: given a unzipped roster file it will parse psyker powers without errors
        expected: parsed an exalted sorcerer correctly with 3 powers
        """
        parsed_roster = fetch_and_parse_roster(roster_file=self.psyker_roster)
        exalted_sorcerer = parsed_roster[0]
        expected_powers = 3
        self.assertTrue(parsed_roster)
        self.assertEqual(len(exalted_sorcerer.psyker_powers), expected_powers)
