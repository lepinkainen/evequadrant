import evelink
import logging as log
# Objects

from api import *
from util import *

class CharacterFactory(object):
    @staticmethod
    def create_character(api, char_id):
        char = evelink.char.Char(char_id, api)
        character_sheet = char.character_sheet().result
        character_info = evelink.eve.EVE(api=api).character_info_from_id(char.char_id).result

        c = Character()
        c.cid = char_id
        c.name = character_sheet['name']
        c.corporation = character_sheet['corp']['name']
        c.corporation_id = character_sheet['corp']['id']
        c.age = character_sheet['create_ts']
        c.location = character_info['location']
        c.ship_id = character_info['ship']['type_id']
        c.ship_name = character_info['ship']['name']
        c.ship_type = character_info['ship']['type_name']
        c.balance = int(character_sheet['balance'])
        c.skillpoints = character_sheet['skillpoints']
        c.clone_skillpoints = character_sheet['clone']['skillpoints']
        c.skill_queue = char.skill_queue().result
        c.active_jobs = [v for v in char.industry_jobs().result.values() if v['delivered'] == False]
        c.active_orders = [order for order in char.orders().result.values() if order['status'] == 'active']
        c.assets = [asset for asset in char.assets().result.values()]

        return c


class Character(object):
    cid = None
    name = None
    corporation = None
    age = None
    location = None
    ship_name = None
    ship_type = None
    balance = None
    skillpoints = None
    clone_skillpoints = None
    active_jobs = None
    active_orders = None
    skill_queue = None
    assets = None

    def get_skill_queue(self):
        skills = [Skill(skill) for skill in self.skill_queue]
        log.debug("Skill queue %s", skills)
        return skills

    def get_assets(self):
        item_list = []

        asset_ids = set()

        # translate asset IDs in a efficient-ish manner
        for asset in self.assets:
            for item in asset['contents']:
                asset_ids.add(item['item_type_id'])

                for subitem in item.get('contents', []):
                    asset_ids.add(subitem['item_type_id'])


        mappings = typeids_to_string(asset_ids)

        for asset in self.assets:
            for item in asset['contents']:
                item_list.append(Asset(item, name=mappings[item['item_type_id']]))

                for subitem in item.get('contents', []):
                    a = Asset(subitem, name=mappings[subitem['item_type_id']])
                    a.in_container = True
                    item_list.append(a)

        return item_list


class Skill(object):
    rawdata = None
    name = None
    type_id = None
    level = None
    level_roman = None
    eta = None   # Time to completion
    done = None  # DateTime of completion

    def __init__(self, skill):
        log.debug("Skill object created: %s", skill)
        self.rawdata = skill
        self.type_id = skill['type_id']
        self.name = typeid_to_string(self.type_id)
        self.level = skill['level']
        self.level_roman = to_roman(self.level)
        self.eta = timestamp_to_string(skill['end_ts'])
        self.done = datetime.fromtimestamp(skill['end_ts'])

class Asset(object):
    container_id = None
    container_name = None
    location_id = None
    location_name = None
    type_id = None
    name = None
    quantity = None
    in_container = False

    def __init__(self, asset, name=None):
        self.type_id = asset['item_type_id']
        self.name = name or typeid_to_string(self.type_id)
        self.quantity = asset['quantity']
