from bs4 import BeautifulSoup
from app.models.killteam_unit import KillteamUnit


def parse_units(roster_file):
    soup = BeautifulSoup(roster_file, features="lxml")
    model_list = soup.findAll("selection", {"type": "model"})
    parsed_models = []
    parsed_unit_list = create_list_of_units(model_list, parsed_models) or None
    return parsed_unit_list


def create_list_of_units(model_list, parsed_models):
    for model in model_list:
        name = get_model_name(model)
        characteristics = get_characteristics(model)
        wargear = get_item_details(model, "Weapon")
        psyker_powers = get_item_details(model, "Psychic Power")
        keywords = get_keywords(model)
        abilities = get_abilities(model)
        cost = get_cost(model)

        parsed_model = KillteamUnit(
            name=name,
            movement=characteristics.get("M"),
            weapon_skill=characteristics.get("WS"),
            ballistic_skill=characteristics.get("BS"),
            strength=characteristics.get("S"),
            toughness=characteristics.get("T"),
            wounds=characteristics.get("W"),
            attacks=characteristics.get("A"),
            leadership=characteristics.get("Ld"),
            save=characteristics.get("Sv"),
            max_allowed=characteristics.get("Max"),
            keywords=keywords,
            psyker_powers=psyker_powers,
            wargear=wargear,
            abilities=abilities,
            point_cost=cost,
        )
        parsed_models.append(parsed_model)

    return parsed_models


def get_cost(model):
    list_of_costs = model.findAll("cost")
    total_cost = 0.0
    for cost in list_of_costs:
        total_cost = total_cost + float(cost.attrs.get("value"))
    return total_cost


def get_abilities(model):
    list_of_abilities = model.findAll("profile", {"typename": "Ability"})
    dict_of_abilities = {}
    for ability in list_of_abilities:
        name = ability.attrs.get("name")
        value = ability.find("characteristic").contents[0].strip().split()
        cleaned_value = " ".join(value)
        dict_of_abilities.update({name: cleaned_value})
    return dict_of_abilities


def get_keywords(model):
    categories = []
    list_of_categories = model.findAll("category")
    for category in list_of_categories:
        categories.append(category.attrs.get("name"))
    return categories


def get_item_details(model, search_type):
    search_filter = model.findAll("profile", {"typename": search_type})
    formatted_items = {}

    for item in search_filter:
        dict_of_characteristics = {}
        name = item.attrs.get("name")
        stats = item.findAll("characteristic")

        for characteristic in stats:
            if characteristic.contents:
                value = characteristic.contents[0].strip().split()
                cleaned_value = " ".join(value)
                dict_of_characteristics.update({name: cleaned_value})

        formatted_items.update(dict_of_characteristics)
    return formatted_items


def get_model_name(model):
    return model.attrs.get("name")


def get_characteristics(model):
    dict_of_characteristics = {}
    model_profile = model.find("profile", {"typename": "Model"})
    if model_profile:
        list_of_characteristics = model_profile.findAll("characteristic")
        for characteristic in list_of_characteristics:
            name = characteristic.attrs.get("name")
            value = characteristic.contents[0]
            dict_of_characteristics.update({name: value})
    return dict_of_characteristics
