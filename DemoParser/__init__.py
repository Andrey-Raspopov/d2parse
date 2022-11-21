import logging
import copy
import ctypes
import json
import math
import os
import re
import time
from io import BytesIO, StringIO

import snappy
import DOTA_COMBATLOG_TYPES
import DOTA_UNIT_ORDER_TYPES
import DemoClass
import FileReader
import NewEntity
import PendingMessage
import Serializer
import StringTable
import messages
import utils
from DemoParser.MessageParser import parse_game_event_list_message, parse_service_message4, fill_basic_entity_info
from Field.Field import Field
from Field.FieldModelEnum import FieldModelEnum
from Field.FieldType import FieldType
from GameEvent import GameEvent
from PlayerInfo import PlayerInfo
from proto import demo_pb2, netmessages_pb2, dota_shared_enums_pb2

logger = logging.getLogger()
with open('data.json') as json_file:
    data = json.load(json_file)

item_dict = {}
for item_json in data['items']:
    item_dict[item_json['id']] = item_json['name']

ability_dict = {}
for ability_json in data['abilities']:
    ability_dict[int(ability_json['id'])] = ability_json['name']

KEY_DATA_TYPES = {
    1: "val_string",
    2: "val_float",
    3: "val_long",
    4: "val_short",
    5: "val_byte",
    6: "val_bool",
    7: "val_uint64"
}


def priority(cmd):
    if cmd == 4 or cmd == 44 or cmd == 45 or cmd == 8:
        return -10
    elif cmd == 55:
        return 5
    elif cmd == 207:
        return 10
    else:
        return 0


class DemoParser(object):

    def __init__(self, filename, verbosity=3, frames=None):
        self.filename = filename
        self.verbosity = verbosity
        self.frames = frames

        self.event_list = None
        self.event_lookup = {}

        self.combat_log_names = []

        self.tick = 0
        self.game_build = 0
        self.class_info = False
        self.class_id_size = None

        self.class_baselines = {}
        self.classes_by_id = {}
        self.classes_by_name = {}
        self.string_tables = {"tables": {}, "name_index": {}, "next_index": 0}
        self.entities = {}
        self.serializers = {}

        self.camera_middle_x = 3600
        self.camera_middle_y = 600

        self.radiant_heros, self.dire_heros = {}, {}

        self.hero1_pos, self.hero2_pos, self.hero3_pos, self.hero4_pos, self.hero5_pos = \
            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]

        self.hero1_angle, self.hero2_angle, self.hero3_angle, self.hero4_angle, self.hero5_angle = \
            0, 0, 0, 0, 0

        self.hero1_name, self.hero2_name, self.hero3_name, self.hero4_name, self.hero5_name = \
            None, None, None, None, None

        self.hero1_hp, self.hero2_hp, self.hero3_hp, self.hero4_hp, self.hero5_hp = \
            100, 100, 100, 100, 100

        self.hero1_hp_max, self.hero2_hp_max, self.hero3_hp_max, self.hero4_hp_max, self.hero5_hp_max = \
            100, 100, 100, 100, 100

        self.hero1_id, self.hero2_id, self.hero3_id, self.hero4_id, self.hero5_id = -1, -1, -1, -1, -1

        self.hero1_level, self.hero2_level, self.hero3_level, self.hero4_level, self.hero5_level = 1, 1, 1, 1, 1

        self.hero1_mana, self.hero2_mana, self.hero3_mana, self.hero4_mana, self.hero5_mana = \
            100, 100, 100, 100, 100

        self.hero1_mana_max, self.hero2_mana_max, self.hero3_mana_max, self.hero4_mana_max, self.hero5_mana_max = \
            100, 100, 100, 100, 100

        self.hero1_items_info, self.hero2_items_info, self.hero3_items_info, self.hero4_items_info, self.hero5_items_info = \
            None, None, None, None, None

        self.hero1_abilities_info, self.hero2_abilities_info, self.hero3_abilities_info, self.hero4_abilities_info, self.hero5_abilities_info = \
            None, None, None, None, None

        self.game_time = 0.0

        self.npcs = None
        self.buildings = None
        self.runes = None

        self.purchase_item = None
        self.purchase_item_delay = 0

        self.mouse_click_x, self.mouse_click_y = None, None
        self.mouse_click_delay = 0

        self.move_to_position_x, self.move_to_position_y = 0, 0
        self.move_to_position_delay = 0

        self.no_target_ability = None
        self.no_target_ability_delay = 0

        self.cast_target_tree = None
        self.cast_target_tree_delay = 0

        self.train_ability = None
        self.train_ability_delay = 0

        self.attack_target_x, self.attack_target_y = 0, 0
        self.attack_target_name = None
        self.attack_target_delay = 0

        self.move_to_target_x, self.move_to_target_y = 0, 0
        self.move_to_target_name = None
        self.move_to_target_delay = 0

        self.radiant_heros_modifiers, self.dire_heros_modifiers = {}, {}

        self.minimap_drag = False

    def run_hooks(self, message):
        if message.__class__ == demo_pb2.CDemoPacket or message.__class__ == demo_pb2.CDemoFullPacket:
            self.parse_demo_packet(message)
        elif message.__class__ == demo_pb2.CDemoStringTables:
            self.parse_string_table(message)
        elif message.__class__ == netmessages_pb2.CSVCMsg_UserMessage:
            self.parse_user_message(message)
        elif message.__class__ == netmessages_pb2.bi_GameEvent:
            self.parse_game_event(message)
        elif message.__class__ == netmessages_pb2.CSVCMsg_GameEventList:
            self.parse_game_event_list(message)
        elif message.__class__ == netmessages_pb2.CSVCMsg_CreateStringTable:
            pass
        elif message.__class__ == netmessages_pb2.CSVCMsg_UpdateStringTable:
            pass

    def parse_string_table(self, tables):
        for table in tables.tables:
            if table.table_name == "userinfo":
                self.parse_user_info_table(table)

            if table.table_name == "CombatLogNames":
                self.parse_combat_log_table(table)

    def parse_combat_log_table(self, table):
        self.combat_log_names = dict(enumerate(
            (item.str for item in table.items)))

    def parse_user_info_table(self, table):
        for item in table.items:
            if len(item.data) > 0:
                if len(item.data) == 140:
                    p = PlayerInfo()
                    ctypes.memmove(ctypes.addressof(p), item.data, 140)
                    p.str = item.str
                    self.run_hooks(p)

    def update_instance_baseline(self):
        if not self.class_info:
            return

        index = self.string_tables["name_index"]["instancebaseline"]
        table = self.string_tables["tables"][index]
        for item_index in table.items:
            item = table.items[item_index]
            if item.key != "":
                class_id = int(item.key)
                self.class_baselines[class_id] = item.value

    def parse_demo_packet(self, packet):
        if isinstance(packet, demo_pb2.CDemoFullPacket):
            p_data = packet.packet.data
        else:
            p_data = packet.data

        if isinstance(packet, demo_pb2.CDemoFullPacket):
            self.run_hooks(packet.string_table)

        reader = FileReader.FileReader(BytesIO(p_data))
        pending_message_list = []
        while reader.rem_bytes() > 0:
            cmd = reader.read_ubit_var()
            size = reader.read_var_uint32()
            message = reader.read_bytes(size)
            pending_message = PendingMessage.PendingMessage(self.tick, cmd, message)
            pending_message_list.append(pending_message)

        pending_message_list.sort(key=lambda msg: priority(msg.cmd))

        for pending_message in pending_message_list:
            cmd = pending_message.cmd
            message = pending_message.message
            try:
                if cmd == 4:
                    # TODO: add parser
                    logger.info('Cmd: 4')
                elif cmd == 6:
                    # TODO: add parser
                    logger.info('Cmd: 6')
                elif cmd == 7:
                    # TODO: add parser
                    logger.info('Cmd: 7')
                elif cmd == 40:
                    self.parse_server_info(message)
                elif cmd == 44:
                    self.parse_service_message(cmd, message)
                elif cmd == 45:
                    self.parse_service_message2(cmd, message)
                elif cmd == 51:
                    # TODO: add parser
                    logger.info('Cmd: 51')
                elif cmd == 55:
                    self.parse_service_message3(cmd, message)
                elif cmd == 145:
                    parse_service_message4(cmd, message)
                elif cmd == 207:
                    parse_game_event_list_message(message)
                elif cmd == 483:
                    self.parse_user_type_message(cmd, message)
                elif cmd == 547:
                    self.process_SpectatorPlayerUnitOrders(cmd, message)
                elif cmd == 554:
                    self.parse_combat_log_entities(message)
            except TypeError:
                print('Type')
            except KeyError:
                print("Key")

    def parse_combat_log_entities(self, message):
        combat_log_names_string_table = self.string_tables["tables"][16]
        string_table_items = combat_log_names_string_table.items
        for item_index in combat_log_names_string_table.items:
            item = combat_log_names_string_table.items[item_index]
            print(item.key)
            print(item.value)
        pb_message = dota_shared_enums_pb2.CMsgDOTACombatLogEntry()
        pb_message.ParseFromString(message)
        if DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_PURCHASE:
            pass
        elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_ITEM:
            pass
        elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_GOLD:
            pass
        elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_ABILITY:
            pass
        elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_MODIFIER_ADD:
            target_name = string_table_items[pb_message.target_name].key
            attacker_name = string_table_items[pb_message.attacker_name].key
            print(attacker_name)
            inflictor_name = string_table_items[pb_message.inflictor_name].key
            target_name = utils.ParseName(target_name)
            if pb_message.target_team == 2:
                if target_name not in self.radiant_heros_modifiers:
                    self.radiant_heros_modifiers[target_name] = []
                    self.radiant_heros_modifiers[target_name].append(inflictor_name)
                else:
                    if inflictor_name not in self.radiant_heros_modifiers[target_name]:
                        self.radiant_heros_modifiers[target_name].append(inflictor_name)
            elif pb_message.target_team == 3:
                if target_name not in self.dire_heros_modifiers:
                    self.dire_heros_modifiers[target_name] = []
                    self.dire_heros_modifiers[target_name].append(inflictor_name)
                else:
                    if inflictor_name not in self.dire_heros_modifiers[target_name]:
                        self.dire_heros_modifiers[target_name].append(inflictor_name)
        elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_MODIFIER_REMOVE:
            target_name = string_table_items[pb_message.target_name].key
            target_name = utils.ParseName(target_name)
            inflictor_name = string_table_items[pb_message.inflictor_name].key
            if pb_message.target_team == 2:
                if target_name != '':
                    if inflictor_name in self.radiant_heros_modifiers[target_name]:
                        self.radiant_heros_modifiers[target_name].remove(inflictor_name)
            elif pb_message.target_team == 3:
                if target_name != '':
                    if inflictor_name in self.dire_heros_modifiers[target_name]:
                        self.dire_heros_modifiers[target_name].remove(inflictor_name)

    def parse_user_type_message(self, cmd, message):
        pb_message = messages.DOTA_USER_MESSAGE_TYPES[cmd]()
        pb_message.ParseFromString(message)
        return pb_message

    def parse_service_message3(self, cmd, message):
        pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
        pb_message.ParseFromString(message)
        entity_reader = FileReader.FileReader(BytesIO(pb_message.entity_data))
        index = -1
        for u in range(0, pb_message.updated_entries):
            index += entity_reader.read_ubit_var() + 1

            cmd = entity_reader.read_bits(2)
            if cmd == 2:
                class_id = entity_reader.read_bits(self.class_id_size)
                serial = entity_reader.read_bits(17)
                entity_reader.read_var_uint32()
                demo_class = self.classes_by_id[class_id]
                baseline = self.class_baselines[class_id]
                e = NewEntity.NewEntity(index, serial, demo_class)
                self.entities[index] = e
                baseline_reader = FileReader.FileReader(BytesIO(bytes(baseline)))
                s = demo_class.serializer
                utils.ReadFields(baseline_reader, s, e.state)
                utils.ReadFields(entity_reader, s, e.state)
            elif cmd == 0:
                e = self.entities[index]
                op = utils.EntityOpUpdated

                if not e.active:
                    e.active = True
                    op |= utils.EntityOpEntered

                utils.ReadFields(entity_reader, e.demo_class.serializer, e.state)
            elif cmd == 1 or cmd == 3:
                op = utils.EntityOpLeft

                if cmd & 0x02 != 0:
                    op |= utils.EntityOpDeleted
                    self.entities[index] = None
        npcs = {}
        buildings = {}
        runes = {}
        for entity_index in self.entities:
            entity = self.entities[entity_index]
            entity_names_string_table = self.string_tables["tables"][7]

            if entity is not None:
                if entity.demo_class.name == "CDOTAPlayer":
                    pass
                elif entity.demo_class.name == "CDOTAGamerulesProxy":
                    e_map = utils.EntityMap(entity)
                    if 'm_pGameRulesm_fGameTime' in e_map:
                        self.game_time = int(-91.0 + e_map['m_pGameRulesm_fGameTime'])
                if entity.demo_class.name.startswith('CDOTA_Unit_Hero'):
                    entity_info = utils.GetHeroInfo(entity)
                    hero_name = utils.GetHeroName(entity.demo_class)
                    if hero_name is not None:
                        hero = {
                            'name': entity_info['hero_name'], 'id': entity_info['m_iPlayerID'],
                            'team_num': entity_info['m_iTeamNum'],
                            'pos': [entity_info['hero_location_x'], entity_info['hero_location_y']],
                            'hp': entity_info['m_iHealth'], 'hp_max': entity_info['m_iMaxHealth'],
                            'level': entity_info['m_iCurrentLevel'],
                            'angle': entity_info['angRotation'],
                            'mana': entity_info['m_flMana'], 'mana_max': entity_info['m_flMaxMana'],
                            'items_info': utils.GetItemsInfo(entity_info, self.entities,
                                                             entity_names_string_table),
                            'abilities_info': utils.GetabilitiesInfo(entity_info, self.entities,
                                                                     entity_names_string_table),
                            'selected': False, 'respawning': entity_info['m_bIsWaitingToSpawn']
                        }
                        if entity_info['m_iTeamNum'] == 2:
                            self.radiant_heros[hero_name] = hero
                        elif entity_info['m_iTeamNum'] == 3:
                            self.dire_heros[hero_name] = hero
                elif entity.demo_class.name.startswith('CDOTA_BaseNPC_Creep_Lane'):
                    entity_info = utils.GetNpcInfo(entity)

                    npcs[entity_info['m_nEntityId']] = {'team_num': entity_info['m_iTeamNum'],
                                                        'pos': [entity_info['location_x'],
                                                                entity_info['location_y']],
                                                        'hp': entity_info['m_iHealth'],
                                                        'hp_max': entity_info['m_iMaxHealth']
                                                        }
                elif entity.demo_class.name.startswith('CDOTA_BaseNPC_Tower'):
                    entity_info = utils.GetNpcInfo(entity)

                    npcs[entity_info['m_nEntityId']] = {'team_num': entity_info['m_iTeamNum'],
                                                        'pos': [entity_info['location_x'],
                                                                entity_info['location_y']],
                                                        'hp': entity_info['m_iHealth'],
                                                        'hp_max': entity_info['m_iMaxHealth']
                                                        }
                elif entity.demo_class.name.startswith('CDOTA_BaseNPC_Barracks'):
                    entity_info = utils.GetNpcInfo(entity)

                    buildings[entity_info['m_nEntityId']] = {'team_num': entity_info['m_iTeamNum'],
                                                             'pos': [entity_info['location_x'],
                                                                     entity_info['location_y']],
                                                             'hp': entity_info['m_iHealth'],
                                                             'hp_max': entity_info['m_iMaxHealth']
                                                             }
                elif entity.demo_class.name.startswith('CDOTA_BaseNPC_Fort'):
                    entity_info = utils.GetNpcInfo(entity)

                    buildings[entity_info['m_nEntityId']] = {'team_num': entity_info['m_iTeamNum'],
                                                             'pos': [entity_info['location_x'],
                                                                     entity_info['location_y']],
                                                             'hp': entity_info['m_iHealth'],
                                                             'hp_max': entity_info['m_iMaxHealth']
                                                             }
                elif entity.demo_class.name.startswith('CDOTA_Item_Rune'):
                    entity_info = utils.GetRuneInfo(entity, entity_names_string_table)
                    runes[entity_info['m_nEntityId']] = {'m_nEntityId': entity_info['location_x'],
                                                         'pos': [entity_info['location_x'],
                                                                 entity_info['location_y']],
                                                         'name': entity_info['name']
                                                         }
        self.npcs = copy.deepcopy(npcs)
        self.buildings = copy.deepcopy(buildings)
        self.runes = copy.deepcopy(runes)

    def parse_service_message2(self, cmd, message):
        pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
        pb_message.ParseFromString(message)
        table_id = pb_message.table_id
        num_changed_entries = pb_message.num_changed_entries
        string_data = pb_message.string_data
        string_table = self.string_tables["tables"][table_id]
        items = utils.ParseStringTable(string_data, num_changed_entries,
                                       string_table.name,
                                       string_table.user_data_fixed_size,
                                       string_table.user_data_size,
                                       string_table.user_data_size_bits,
                                       string_table.flags)
        for item in items:
            index = item.index
            if index in string_table.items:
                if item.key != "" and item.key != string_table.items[index].key:
                    string_table.items[index].key = item.key

                if len(item.value) > 0:
                    string_table.items[index].value = item.value

            else:
                string_table.items[index] = item
        if string_table.name == "instancebaseline":
            self.update_instance_baseline()

    def parse_service_message(self, cmd, message):
        pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
        pb_message.ParseFromString(message)
        buf = pb_message.string_data
        if pb_message.data_compressed:
            string_table_reader = FileReader.FileReader(BytesIO(buf))
            s = string_table_reader.read_bytes(4)

            string_value = ""
            for c in s:
                string_value += chr(c)

            if string_value != "LZSS":
                buf = snappy.decompress(buf)
        num_updates = pb_message.num_entries
        name = pb_message.name
        user_data_fixed_size = pb_message.user_data_fixed_size
        user_data_size = pb_message.user_data_size
        user_data_size_bits = pb_message.user_data_size_bits
        flags = pb_message.flags
        string_table = StringTable.StringTable(self.string_tables['next_index'], name,
                                               user_data_fixed_size, user_data_size, user_data_size_bits,
                                               flags)
        self.string_tables['next_index'] += 1
        items = utils.ParseStringTable(buf, num_updates, name, user_data_fixed_size,
                                       user_data_size, user_data_size_bits, flags)
        for item in items:
            string_table.items[item.index] = item
        self.string_tables["tables"][string_table.index] = string_table
        self.string_tables["name_index"][string_table.name] = string_table.index
        if string_table.name == "instancebaseline":
            self.update_instance_baseline()

    def parse_server_info(self, message):
        pb_message = netmessages_pb2.CSVCMsg_ServerInfo()
        pb_message.ParseFromString(message)
        self.class_id_size = int(math.log(float(pb_message.max_classes)) / math.log(2)) + 1
        p = re.compile(r'/dota_v(\d+)/')
        searches = p.search(pb_message.game_dir)
        self.game_build = int(searches.group(1))

    def process_SpectatorPlayerUnitOrders(self, cmd, message):
        pb_message = self.parse_user_type_message(cmd, message)
        order = DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(pb_message.order_type).name
        if order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_MOVE_TO_POSITION.name:
            with open('1', 'a') as f:
                dump = json.dumps(
                    {'entity': pb_message.entindex, 'x': -pb_message.position.x - (utils.MAP_HALF_SIZE / 2),
                     'y': pb_message.position.y + (utils.MAP_HALF_SIZE / 2)})
                f.write(dump)
                f.write('\n')
            self.move_to_position_x = -pb_message.position.x - (utils.MAP_HALF_SIZE / 2)
            self.move_to_position_y = pb_message.position.y + (utils.MAP_HALF_SIZE / 2)
            self.move_to_position_x = self.move_to_position_x / 4.0
            self.move_to_position_y = self.move_to_position_y / 4.0
            self.move_to_position_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_MOVE_TO_TARGET.name:
            target_entity = self.entities[pb_message.target_index]
            demo_class = target_entity.demo_class
            if demo_class.name.startswith('CDOTA_Unit_Hero'):
                target_entity_info = utils.GetHeroInfo(target_entity)
                target_pos = fill_basic_entity_info(target_entity_info, 'hero_name', 'hero_location_x',
                                                    'hero_location_y')
                self.fill_move_entity_info(target_entity_info, target_pos, 'hero_name')
            elif demo_class.name.startswith('CDOTA_BaseNPC'):
                target_entity_info = utils.GetNpcInfo(target_entity)
                target_pos = fill_basic_entity_info(target_entity_info, 'npc_name', 'location_x', 'location_y')
                self.fill_move_entity_info(target_entity_info, target_pos, 'npc_name')
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_PURCHASE_ITEM.name:
            purchase_item_name = item_dict[pb_message.ability_id]

            self.purchase_item = purchase_item_name
            self.purchase_item_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TRAIN_ABILITY.name:
            entity_names_string_table = self.string_tables["tables"][7]
            units_entity = self.entities[pb_message.units[0]]
            if units_entity is not None:
                units_class_name = units_entity.demo_class.name
                print(units_class_name)
            units_entity_info = utils.EntityMap(units_entity)
            print(units_entity_info)
            ability_entity = self.entities[pb_message.ability_id]
            if ability_entity is not None:
                ability_class_name = ability_entity.demo_class.name
                print(ability_class_name)
            ability_entity_info = utils.EntityMap(ability_entity)
            m_p_entitym_name_stringable_index = ability_entity_info["m_pEntitym_nameStringableIndex"]
            item_name = entity_names_string_table.items[m_p_entitym_name_stringable_index]
            self.train_ability = item_name.key
            self.train_ability_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_NO_TARGET.name:
            unit_entity = self.entities[pb_message.entindex]
            unit_entity_e_map = utils.EntityMap(unit_entity)
            entity_names_string_table = self.string_tables["tables"][7]
            ability_entity = self.entities[pb_message.ability_id]
            if ability_entity is not None:
                ability_class_name = ability_entity.demo_class.name
            ability_entity_e_map = utils.EntityMap(ability_entity)
            m_p_entitym_name_stringable_index = ability_entity_e_map["m_pEntitym_nameStringableIndex"]
            item_name = entity_names_string_table.items[m_p_entitym_name_stringable_index]
            self.no_target_ability = item_name.key
            self.no_target_ability_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_POSITION.name:
            entity_names_string_table = self.string_tables["tables"][7]
            for item_index in entity_names_string_table.items:
                item = entity_names_string_table.items[item_index]
            ability_entity = self.entities[pb_message.ability_id]
            ability_entity_e_map = utils.EntityMap(ability_entity)
            m_p_entitym_name_stringable_index = ability_entity_e_map["m_pEntitym_nameStringableIndex"]

            ability_item = entity_names_string_table.items[m_p_entitym_name_stringable_index]
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_TARGET_TREE.name:
            self.cast_target_tree = True
            self.cast_target_tree_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_TARGET.name:
            entity_names_string_table = self.string_tables["tables"][7]
            target_entity = self.entities[pb_message.target_index]
            target_entity_info = utils.GetHeroInfo(target_entity)
            target_pos = fill_basic_entity_info(target_entity_info, 'hero_name', 'hero_location_x', 'hero_location_y')
            for item_index in entity_names_string_table.items:
                item = entity_names_string_table.items[item_index]
            ability_entity = self.entities[pb_message.ability_id]
            ability_entity_e_map = utils.EntityMap(ability_entity)
            m_p_entitym_name_stringable_index = ability_entity_e_map["m_pEntitym_nameStringableIndex"]
            ability_item = entity_names_string_table.items[m_p_entitym_name_stringable_index]
            if ability_item.index == 399:
                os.system('spd-say "ability capture is appeared"')
                time.sleep(10000)
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_ATTACK_TARGET.name:
            target_entity = self.entities[pb_message.target_index]
            demo_class = target_entity.demo_class
            if demo_class.name.startswith('CDOTA_Unit_Hero'):
                target_entity_info = utils.GetHeroInfo(target_entity)
                target_pos = fill_basic_entity_info(target_entity_info, 'hero_name', 'hero_location_x',
                                                    'hero_location_y')
                self.attack_target_x = target_pos[0]
                self.attack_target_y = target_pos[1]
                self.attack_target_name = target_entity_info['hero_name']
                self.attack_target_delay = 3
            elif demo_class.name.startswith('CDOTA_BaseNPC'):
                target_entity_info = utils.GetNpcInfo(target_entity)
                target_name = target_entity_info['npc_name']
                target_pos = [target_entity_info['location_x'], target_entity_info['location_y']]
                target_team = target_entity_info['m_iTeamNum']

                self.attack_target_x = target_pos[0]
                self.attack_target_y = target_pos[1]
                self.attack_target_name = target_entity_info['npc_name']
                self.attack_target_delay = 3
        elif order == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_PICKUP_RUNE.name:
            entity_names_string_table = self.string_tables["tables"][7]
            target_entity = self.entities[pb_message.target_index]
            e_map = utils.EntityMap(target_entity)
        else:
            pass

    def fill_move_entity_info(self, target_entity_info, target_pos, entity_type):
        self.move_to_target_x = target_pos[0]
        self.move_to_target_y = target_pos[1]
        self.move_to_target_name = target_entity_info[entity_type]
        self.move_to_target_delay = 3

    def parse_user_message(self, message):
        cmd = message.msg_type
        if cmd not in messages.COMBINED_USER_MESSAGE_TYPES:
            raise IndexError("Unknown user message cmd: %s" % (cmd,))

        reader = FileReader.FileReader(StringIO(message.msg_data))
        message_type = messages.COMBINED_USER_MESSAGE_TYPES[cmd]
        user_message = reader.read_message(message_type, read_size=False)

        self.run_hooks(user_message)

    def parse_game_event_list(self, eventlist):
        self.event_list = eventlist

        for descriptor in eventlist.descriptors:
            self.event_lookup[descriptor.eventid] = descriptor

    def parse_game_event(self, event):
        """
        So CSVCMsg_GameEventList is a list of all events that can happen.
        A game event has an eventid which maps to a type of event that happened
        """
        if event.eventid in self.event_lookup:
            # Bash this into a nicer data format to work with
            event_type = self.event_lookup[event.eventid]
            ge = GameEvent(event_type.name)

            for i, key in enumerate(event.keys):
                key_type = event_type.keys[i]
                ge.keys[key_type.name] = getattr(key, KEY_DATA_TYPES[key.type])

            self.run_hooks(ge)

    def parse(self):
        """
        Parse a replay
        """
        with open(self.filename, 'rb') as f:
            p = f.read()
            reader = FileReader.FileReader(BytesIO(p))

            header = reader.read(8)
            reader.read(8)
            if header.decode('utf-8') != "PBDEMS2\x00":
                raise ValueError("Invalid replay - incorrect header")

            BytesIO(f.read())

            frame = 0
            more = True
            while more and reader.remaining > 0:
                cmd = reader.read_vint32()
                tick = reader.read_vint32()

                compressed = False

                if cmd & demo_pb2.DEM_IsCompressed:
                    compressed = True
                    cmd = cmd & ~demo_pb2.DEM_IsCompressed

                if cmd not in messages.MESSAGE_TYPES:
                    raise KeyError("Unknown message type found")

                message_type = messages.MESSAGE_TYPES[cmd]
                message, b = reader.read_message(message_type, compressed)

                if tick == 4294967295:
                    tick = 0

                self.tick = tick

                if message_type == demo_pb2.CDemoSendTables:
                    message = self.demo_send_tables(message)
                elif message_type == demo_pb2.CDemoClassInfo:
                    self.demo_class_info(message)
                elif message_type == demo_pb2.CDemoSyncTick:
                    continue

                self.run_hooks(message)

                frame += 1
                if self.frames and frame > self.frames:
                    break

    def demo_class_info(self, message):
        classes = message.classes
        for c in classes:
            demo_class = DemoClass.DemoClass(c.class_id, c.network_name, self.serializers[c.network_name])

            self.classes_by_id[c.class_id] = demo_class
            self.classes_by_name[c.network_name] = demo_class
        self.class_info = True
        self.update_instance_baseline()

    def demo_send_tables(self, message):
        table_reader = FileReader.FileReader(BytesIO(message.data))
        size = table_reader.read_var_uint32()
        message = table_reader.read_bytes(size)
        pb_message = netmessages_pb2.CSVCMsg_FlattenedSerializer()
        pb_message.ParseFromString(message)
        patches = []
        for field_patch in utils.FieldPatches:
            if field_patch.should_apply(self.game_build):
                patches.append(field_patch)
        fields = {}
        field_types = {}
        for s in pb_message.serializers:
            serializer = Serializer.Serializer(pb_message, s)
            for field_index in s.fields_index:
                if field_index not in fields:
                    field = Field(pb_message, pb_message.fields[field_index])
                    if self.game_build <= 990:
                        field.parent_name = serializer.name

                    if field.var_type not in field_types:
                        field_types[field.var_type] = FieldType(name=field.var_type)

                    field.field_type = field_types[field.var_type]

                    if field.serializer_name is not None:
                        field.serializer = self.serializers[field.serializer_name]
                    elif field.field_type.base_type == "CBodyComponent":
                        field.serializer = self.serializers[field.serializer_name]
                    else:
                        field.serializer = None

                    for field_patch in patches:
                        field_patch.patch(field)

                    if field.serializer is not None or field.field_type.base_type == "CBodyComponent":
                        if (field.field_type.base_type in utils.pointerTypes) and utils.pointerTypes[field.field_type.base_type]:
                            field.set_model(FieldModelEnum.fieldModelFixedTable.value)
                        else:
                            field.set_model(FieldModelEnum.fieldModelVariableTable.value)
                    elif field.field_type.count > 0 and field.field_type.base_type != "char":
                        field.set_model(FieldModelEnum.fieldModelFixedArray.value)
                    elif field.field_type.base_type == "CUtlVector" or field.field_type.base_type == "CNetworkUtlVectorBase":
                        field.set_model(FieldModelEnum.fieldModelVariableArray.value)
                    else:
                        field.set_model(FieldModelEnum.fieldModelSimple.value)

                    fields[field_index] = field

                serializer.fields.append(fields[field_index])

            self.serializers[serializer.name] = serializer

            if serializer.name in self.classes_by_name:
                self.classes_by_name[serializer.name].serializer = serializer
        return message