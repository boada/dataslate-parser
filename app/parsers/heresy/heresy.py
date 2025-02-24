from bs4 import BeautifulSoup

from app.models.armor_facing import ArmorFacing
from app.models.heresy_unit import HeresyUnit
from app.models.unit_group import UnitGroup


def parse_units(roster_file):
    soup = BeautifulSoup(roster_file, features="lxml")
    rule_whitelist = [
        "Rite of War",
        "Legion and Allegiance",
        "Use Playtest Rules",
        "Allegiance",
        "Legio",
        "Mournival Rules",
        "Solar Aux Superheavy",
    ]
    parsed_list = data_cleanse(rule_whitelist, soup)
    return parsed_list


def data_cleanse(rule_whitelist, soup):
    selections = soup.find("selections").find_all("selection", recursive=False)
    filter_out_non_unit_entries(rule_whitelist, selections)
    list_of_squads = get_squads(selections)
    parsed_list = create_parsed_list(list_of_squads)
    return parsed_list


def create_parsed_list(list_of_squads):
    parsed_list = []
    for squads in list_of_squads:
        armored, hybrid, parsed_squads, toughness = sort_units_by_statline(squads)

        parsed_list.append(
            UnitGroup(
                name=squads[0].get("unit_name"),
                list_of_units=parsed_squads,
                toughness=toughness,
                armored=armored,
                hybrid=hybrid,
            )
        )
    return parsed_list


def sort_units_by_statline(squads):
    toughness = []
    armored = []
    hybrid = []
    parsed_squads = []
    for unit in squads:
        parsed_squads.append(create_parsed_unit(unit))
    for parsed_unit in parsed_squads:
        if parsed_unit.stat_type == "toughness":
            toughness.append(parsed_unit)
        elif parsed_unit.stat_type == "armored":
            armored.append(parsed_unit)
        elif parsed_unit.stat_type == "hybrid":
            hybrid.append(parsed_unit)
    return armored, hybrid, parsed_squads, toughness


def create_parsed_unit(unit):
    parsed_model = HeresyUnit(
        name=unit.get("name"),
        unit_type=unit.get("unit type") or unit.get("type"),
        weapon_skill=unit.get("ws"),
        ballistic_skill=unit.get("bs"),
        strength=unit.get("s"),
        toughness=unit.get("t"),
        wounds=unit.get("w"),
        initiative=unit.get("i"),
        attacks=unit.get("a"),
        leadership=unit.get("ld"),
        save=unit.get("save"),
        wargear=unit.get("wargear"),
        weapon=unit.get("weapon"),
        stat_type=HeresyUnit.get_stat_type(
            unit_type=unit.get("unit type") or unit.get("type")
        ),
        abilities=unit.get("rules"),
        armor_facing=ArmorFacing(
            front=unit.get("front"),
            side=unit.get("side"),
            rear=unit.get("rear"),
            hp=unit.get("hp"),
        ),
    )
    return parsed_model


def get_squads(squads):
    list_of_squads = []
    for unit in squads:
        list_of_squads.append(parse_squad_characteristics(unit))
    return list_of_squads


def find_unit_attachments(unit, search_term):
    dict_of_attachments = {}
    weapons = unit.find_all(typename=search_term)

    for item in weapons:
        gear = get_characteristics(item, unit_name=None)
        name = gear.get("name")
        dict_of_attachments.update({name: gear})
    return dict_of_attachments


def parse_squad_characteristics(unit):
    parsed_profiles = []
    unit_name = unit.attrs.get("name")
    list_of_units = unit.find_all(typename="Unit")
    list_of_walkers = unit.find_all(typename="Walker")
    list_of_vehicles = unit.find_all(typename="Vehicle")
    list_of_profiles_in_squad = list_of_units + list_of_walkers + list_of_vehicles
    for profile in list_of_profiles_in_squad:
        parsed_unit = get_characteristics(profile, unit_name)
        parsed_unit.update({"weapon": find_unit_attachments(unit, "Weapon")})
        parsed_unit.update({"wargear": find_unit_attachments(unit, "Wargear Item")})
        parsed_unit.update({"rules": get_rules(unit)})
        parsed_profiles.append(parsed_unit)
    return parsed_profiles


def get_rules(unit):
    dict_of_rules = {}
    rules = unit.find_all(name="rule")
    for rule in rules:
        description = None
        name = rule.get("name")
        if rule.find(name="description"):
            description = rule.find(name="description").contents[0]
        dict_of_rules.update({name: description})
    return dict_of_rules


def get_characteristics(unit_type, unit_name):
    dict_of_characteristics = {}
    dict_of_characteristics.update({"unit_name": unit_name})
    model_name = unit_type.attrs.get("name").lower()
    dict_of_characteristics.update({"name": model_name})
    unit_characteristics = unit_type.find_all("characteristic")
    for characteristic in unit_characteristics:
        value = None
        name = characteristic.attrs.get("name").lower()
        if characteristic.contents:
            value = characteristic.contents[0].lower()
        dict_of_characteristics.update({name: value})
    return dict_of_characteristics


def filter_out_non_unit_entries(rule_whitelist, selections):
    dict_of_rules = {}
    for rule in rule_whitelist:
        for idx, selection in enumerate(selections):
            name = selection.attrs.get("name")
            if name == rule:
                dict_of_rules.update({name: selection})
                selections.pop(idx)
    return dict_of_rules
