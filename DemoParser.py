import copy
import ctypes
import functools
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
from Field.Field import Field
from Field.FieldModelEnum import FieldModelEnum
from Field.FieldType import FieldType
from GameEvent import GameEvent
from PlayerInfo import PlayerInfo
from proto import demo_pb2, netmessages_pb2, dota_shared_enums_pb2

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
    """
    A parser for Dota 2 .dem files based on deminfo2
    https://developer.valvesoftware.com/wiki/Dota_2_Demo_Format
    """

    def __init__(self, filename, verbosity=3, frames=None, hooks=None):
        self.filename = filename
        self.verbosity = verbosity
        self.frames = frames

        self.eventlist = None
        self.event_lookup = {}

        self.combat_log_names = []

        self.internal_hooks = {
            demo_pb2.CDemoPacket: self.parse_demo_packet,
            demo_pb2.CDemoFullPacket: self.parse_demo_packet,
            demo_pb2.CDemoStringTables: self.parse_string_table,
            netmessages_pb2.CSVCMsg_UserMessage: self.parse_user_message,
            netmessages_pb2.bi_GameEvent: self.parse_game_event,
            netmessages_pb2.CSVCMsg_GameEventList: self.parse_game_event_list,
            netmessages_pb2.CSVCMsg_CreateStringTable: self.create_string_table,
            netmessages_pb2.CSVCMsg_UpdateStringTable: self.update_string_table,
        }

        self.hooks = hooks or {}

        self.error = functools.partial(self.log, 1)
        self.important = functools.partial(self.log, 2)
        self.info = functools.partial(self.log, 3)
        self.debug = functools.partial(self.log, 4)
        self.worthless = functools.partial(self.log, 5)
        self.current_b = None

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

    def log(self, level, message):
        """
        Log a message if our verbosity permits it
        """
        if level <= self.verbosity:
            print(message)

    def run_hooks(self, packet):
        """
        Run any additional functions that want to process this type of packet.
        These can be internal parser hooks, or external hooks that process
        information
        """
        if packet.__class__ in self.internal_hooks:
            self.internal_hooks[packet.__class__](packet)

        if packet.__class__ in self.hooks:
            self.hooks[packet.__class__](packet)

    def create_string_table(self, message):
        pass

    def update_string_table(self, message):
        pass

    def parse_string_table(self, tables):
        """
        Need to pull out player information from string table
        """
        for table in tables.tables:
            if table.table_name == "userinfo":
                for item in table.items:
                    if len(item.data) > 0:
                        if len(item.data) == 140:
                            p = PlayerInfo()
                            ctypes.memmove(ctypes.addressof(p), item.data, 140)
                            p.str = item.str
                            self.run_hooks(p)

            if table.table_name == "CombatLogNames":
                self.combat_log_names = dict(enumerate(
                    (item.str for item in table.items)))

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
            # print("cmd 2: " , cmd)

            message = pending_message.message
            try:
                if cmd == 40:

                    pb_message = netmessages_pb2.CSVCMsg_ServerInfo()
                    # pb_message_string = pb_message.ParseFromString(message)

                    self.class_id_size = int(math.log(float(pb_message.max_classes)) / math.log(2)) + 1

                    p = re.compile('/dota_v(\d+)/')
                    searches = p.search(pb_message.game_dir)
                    self.game_build = 1110
                elif cmd == 44:
                    # print("SVC_Messages_svc_CreateStringTable")

                    pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)

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
                elif cmd == 45:
                    # print("CSVCMsg_UpdateStringTable")
                    pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)

                    table_id = pb_message.table_id
                    num_changed_entries = pb_message.num_changed_entries
                    string_data = pb_message.string_data

                    string_list = [int(data) for data in string_data]

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
                elif cmd == 55:
                    # print("SVC_Messages_svc_PacketEntities")
                    pb_message = messages.SVC_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)

                    entity_reader = FileReader.FileReader(BytesIO(pb_message.entity_data))

                    index = -1
                    # print("pb_message.updated_entries: ", pb_message.updated_entries)
                    for u in range(0, pb_message.updated_entries):
                        index += entity_reader.read_ubit_var() + 1

                        op = utils.EntityOpNone

                        cmd = entity_reader.read_bits(2)
                        # print("entity cmd: ", cmd)
                        if cmd == 2:
                            class_id = entity_reader.read_bits(self.class_id_size)

                            serial = entity_reader.read_bits(17)

                            temp = entity_reader.read_var_uint32()

                            demo_class = self.classes_by_id[class_id]

                            baseline = self.class_baselines[class_id]
                            baseline_list = [int(c) for c in baseline]

                            e = NewEntity.NewEntity(index, serial, demo_class)

                            self.entities[index] = e
                            # op = EntityOpCreated | EntityOpEntered

                            baseline_reader = FileReader.FileReader(BytesIO(bytes(baseline)))

                            s = demo_class.serializer
                            # print("")

                            utils.ReadFields(baseline_reader, s, e.state)
                            utils.ReadFields(entity_reader, s, e.state)

                            op = utils.EntityOpCreated | utils.EntityOpEntered
                        elif cmd == 0:
                            e = self.entities[index]
                            op = utils.EntityOpUpdated

                            if e.active == False:
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
                        handle_mask = (1 << 14) - 1
                        entity_names_string_table = self.string_tables["tables"][7]
                        modifier_names_string_table = self.string_tables["tables"][12]
                        active_modifiers_string_table = self.string_tables["tables"][13]

                        # print("modifier_names_string_table.items: ", modifier_names_string_table.items)
                        # print("active_modifiers_string_table.items: ", active_modifiers_string_table.items)
                        # for item_index in modifier_names_string_table.items:
                        # item = modifier_names_string_table.items[item_index]
                        # print("item_index: ", item_index)
                        # print("item.key: ", item.key)
                        # print("item.value: ", item.value)
                        # value = item.value
                        # print("value.decode('utf-8'): ", value.decode('utf-8'))

                        # time.sleep(10)
                        # print("")

                        if entity != None:
                            # print("entity.demo_class.name: ", entity.demo_class.name)
                            if entity.demo_class.name == "CDOTAPlayer":
                                pass
                                # E_Map = utils.EntityMap(entity)
                                # for key in E_Map:
                                #    print("key: ", key)
                                #    print("E_Map[key]: ", E_Map[key])
                                # print("")
                            elif entity.demo_class.name == "CDOTAGamerulesProxy":
                                E_Map = utils.EntityMap(entity)

                                if 'm_pGameRulesm_fGameTime' in E_Map:
                                    # print("E_Map['m_pGameRulesm_fGameTime']: ", E_Map['m_pGameRulesm_fGameTime'])
                                    self.game_time = int(-91.0 + E_Map['m_pGameRulesm_fGameTime'])

                                # for key in E_Map:
                                # print("key: ", key)
                                # print("E_Map[key]: ", E_Map[key])

                                # print("")

                            if entity.demo_class.name.startswith('CDOTA_Unit_Hero'):
                                entity_info = utils.GetHeroInfo(entity)

                                hero_name = utils.GetHeroName(entity.demo_class)
                                # print("hero_name: ", hero_name)

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
                                # print("CDOTA_Item_Rune")
                                # print("self.game_time: ", self.game_time)
                                entity_info = utils.GetRuneInfo(entity, entity_names_string_table)

                                # if entity_info['name'] != None:
                                # print("entity_info['name'].index: ", entity_info['name'].index)
                                # print("entity_info['name'].key: ", entity_info['name'].key)
                                # print("entity_info['name'].value: ", entity_info['name'].value)

                                runes[entity_info['m_nEntityId']] = {'m_nEntityId': entity_info['location_x'],
                                                                     'pos': [entity_info['location_x'],
                                                                             entity_info['location_y']],
                                                                     'name': entity_info['name']
                                                                     }
                                # print("")

                    self.npcs = copy.deepcopy(npcs)
                    self.buildings = copy.deepcopy(buildings)
                    self.runes = copy.deepcopy(runes)
                    # print("")
                elif cmd == 145:
                    # print("UM_ParticleManager")
                    pb_message = messages.USER_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)
                    # print("pb_message: ", pb_message)
                    # print("")
                elif cmd == 207:
                    print("SVCMsg_GameEventList")
                    pb_message = netmessages_pb2.CSVCMsg_GameEventList()
                    pb_message_string = pb_message.ParseFromString(message)
                    # print("pb_message: ", pb_message)
                    # print("")
                elif cmd == 483:
                    # print("onCDOTAUserMsg_OverheadEvent")
                    pb_message = messages.DOTA_USER_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)
                    # print("pb_message: ", pb_message)
                    # print("")
                elif cmd == 547:
                    # print("DOTAUserMsg_SpectatorPlayerUnitOrders")
                    pb_message = messages.DOTA_USER_MESSAGE_TYPES[cmd]()
                    pb_message_string = pb_message.ParseFromString(message)

                    order_type_name = DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(pb_message.order_type).name
                    # print("order_type_name: ", order_type_name)
                    # print("pb_message: ", pb_message)
                    # print("")

                    if DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_MOVE_TO_POSITION.name:
                        print("DOTA_UNIT_ORDER_MOVE_TO_POSITION")

                        order_type_name = DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(pb_message.order_type).name
                        # print("order_type_name: ", order_type_name)
                        # print("position: ", pb_message.position)
                        print("position.x: ", pb_message.position.x)
                        print("position.y: ", pb_message.position.y)

                        self.move_to_position_x = -pb_message.position.x - (utils.MAP_HALF_SIZE / 2)
                        self.move_to_position_y = pb_message.position.y + (utils.MAP_HALF_SIZE / 2)

                        self.move_to_position_x = self.move_to_position_x / 4.0
                        self.move_to_position_y = self.move_to_position_y / 4.0

                        self.move_to_position_delay = 3

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_MOVE_TO_TARGET.name:
                        print("DOTA_UNIT_ORDER_MOVE_TO_TARGET")

                        target_entity = self.entities[pb_message.target_index]
                        demo_class = target_entity.demo_class
                        '''
                        target_name:  necrolyte
                        target_pos:  [-323.0, 441.7421875]
                        target_team:  2
                        '''

                        # self.move_to_target_name = None
                        if demo_class.name.startswith('CDOTA_Unit_Hero') == True:
                            target_entity_info = utils.GetHeroInfo(target_entity)
                            target_name = target_entity_info['hero_name']
                            target_pos = [target_entity_info['hero_location_x'], target_entity_info['hero_location_y']]
                            target_team = target_entity_info['m_iTeamNum']

                            self.move_to_target_x = target_pos[0]
                            self.move_to_target_y = target_pos[1]
                            self.move_to_target_name = target_entity_info['hero_name']
                            self.move_to_target_delay = 3
                        elif demo_class.name.startswith('CDOTA_BaseNPC') == True:
                            target_entity_info = utils.GetNpcInfo(target_entity)
                            target_name = target_entity_info['npc_name']
                            target_pos = [target_entity_info['location_x'], target_entity_info['location_y']]
                            target_team = target_entity_info['m_iTeamNum']

                            self.move_to_target_x = target_pos[0]
                            self.move_to_target_y = target_pos[1]
                            self.move_to_target_name = target_entity_info['npc_name']
                            self.move_to_target_delay = 3

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_PURCHASE_ITEM.name:
                        print("DOTA_UNIT_ORDER_PURCHASE_ITEM")

                        purchase_item_name = item_dict[pb_message.ability_id]

                        self.purchase_item = purchase_item_name
                        self.purchase_item_delay = 3

                        print("purchase item name: ", purchase_item_name)
                        print("")

                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TRAIN_ABILITY.name:
                        print("DOTA_UNIT_ORDER_TRAIN_ABILITY")

                        entity_names_string_table = self.string_tables["tables"][7]

                        units_entity = self.entities[pb_message.units[0]]
                        if units_entity != None:
                            units_class_name = units_entity.demo_class.name

                        units_entity_info = utils.EntityMap(units_entity)

                        ability_entity = self.entities[pb_message.ability_id]
                        if ability_entity != None:
                            ability_class_name = ability_entity.demo_class.name

                        ability_entity_info = utils.EntityMap(ability_entity)

                        m_pEntitym_nameStringableIndex = ability_entity_info["m_pEntitym_nameStringableIndex"]
                        item_name = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                        # print("train ability name: ", item_name.key)

                        self.train_ability = item_name.key
                        self.train_ability_delay = 3

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_NO_TARGET.name:
                        print("DOTA_UNIT_ORDER_CAST_NO_TARGET")

                        unit_entity = self.entities[pb_message.entindex]
                        unit_entity_E_Map = utils.EntityMap(unit_entity)

                        entity_names_string_table = self.string_tables["tables"][7]

                        ability_entity = self.entities[pb_message.ability_id]
                        if ability_entity != None:
                            ability_class_name = ability_entity.demo_class.name

                        ability_entity_E_Map = utils.EntityMap(ability_entity)

                        m_pEntitym_nameStringableIndex = ability_entity_E_Map["m_pEntitym_nameStringableIndex"]

                        item_name = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                        print("use ability name: ", item_name.key)

                        self.no_target_ability = item_name.key
                        self.no_target_ability_delay = 3

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_POSITION.name:
                        print("DOTA_UNIT_ORDER_CAST_POSITION")

                        '''
                        DOTA_UNIT_ORDER_CAST_POSITION = 5;
                        DOTA_UNIT_ORDER_CAST_TARGET = 6;
                        DOTA_UNIT_ORDER_CAST_TARGET_TREE = 7;
                        DOTA_UNIT_ORDER_CAST_NO_TARGET = 8;
                        DOTA_UNIT_ORDER_CAST_TOGGLE = 9;
                        '''
                        print("pb_message: ", pb_message)
                        print("pb_message.position: ", pb_message.position)
                        print("pb_message.position.x: ", pb_message.position.x)
                        print("pb_message.position.y: ", pb_message.position.y)

                        entity_names_string_table = self.string_tables["tables"][7]
                        for item_index in entity_names_string_table.items:
                            item = entity_names_string_table.items[item_index]

                        ability_entity = self.entities[pb_message.ability_id]
                        ability_entity_E_Map = utils.EntityMap(ability_entity)
                        # print("ability_entity_E_Map: ", ability_entity_E_Map)
                        m_pEntitym_nameStringableIndex = ability_entity_E_Map["m_pEntitym_nameStringableIndex"]

                        ability_item = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                        print("ability_item.index: ", ability_item.index)
                        print("ability_item.key: ", ability_item.key)
                        print("ability_item.value: ", ability_item.value)

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_TARGET_TREE.name:
                        print("DOTA_UNIT_ORDER_CAST_TARGET_TREE")

                        # self.cast_target_tree = None
                        # self.cast_target_tree_delay = 0

                        # print("order_type_name: ", order_type_name)
                        # print("pb_message: ", pb_message)

                        self.cast_target_tree = True
                        self.cast_target_tree_delay = 3

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_CAST_TARGET.name:
                        print("DOTA_UNIT_ORDER_CAST_TARGET")

                        print("pb_message: ", pb_message)

                        entity_names_string_table = self.string_tables["tables"][7]

                        target_entity = self.entities[pb_message.target_index]
                        if target_entity != None:
                            target_class_name = target_entity.demo_class.name

                        target_entity_info = utils.GetHeroInfo(target_entity)
                        target_name = target_entity_info['hero_name']
                        target_pos = [target_entity_info['hero_location_x'], target_entity_info['hero_location_y']]
                        target_team = target_entity_info['m_iTeamNum']

                        print("target_name: ", target_name)
                        print("target_pos: ", target_pos)
                        print("target_team: ", target_team)
                        for item_index in entity_names_string_table.items:
                            item = entity_names_string_table.items[item_index]

                        ability_entity = self.entities[pb_message.ability_id]
                        ability_entity_E_Map = utils.EntityMap(ability_entity)
                        print("ability_entity_E_Map: ", ability_entity_E_Map)

                        m_pEntitym_nameStringableIndex = ability_entity_E_Map["m_pEntitym_nameStringableIndex"]

                        ability_item = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                        print("ability_item.index: ", ability_item.index)
                        print("ability_item.key: ", ability_item.key)
                        print("ability_item.value: ", ability_item.value)

                        if ability_item.index == 399:
                            os.system('spd-say "ability capture is appeared"')
                            time.sleep(10000)

                        print("")
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_ATTACK_TARGET.name:
                        print("DOTA_UNIT_ORDER_ATTACK_TARGET")
                        '''
                        entindex: 1
                        order_type: 4
                        units: 743
                        target_index: 195
                        queue: false
                        sequence_number: 771
                        flags: 0
                        '''

                        target_entity = self.entities[pb_message.target_index]
                        # print("target_entity.demo_class.name: ", target_entity.demo_class.name)
                        demo_class = target_entity.demo_class

                        if demo_class.name.startswith('CDOTA_Unit_Hero') == True:
                            target_entity_info = utils.GetHeroInfo(target_entity)
                            target_name = target_entity_info['hero_name']
                            target_pos = [target_entity_info['hero_location_x'], target_entity_info['hero_location_y']]
                            target_team = target_entity_info['m_iTeamNum']

                            self.attack_target_x = target_pos[0]
                            self.attack_target_y = target_pos[1]
                            self.attack_target_name = target_entity_info['hero_name']
                            self.attack_target_delay = 3
                        elif demo_class.name.startswith('CDOTA_BaseNPC') == True:
                            target_entity_info = utils.GetNpcInfo(target_entity)
                            target_name = target_entity_info['npc_name']
                            target_pos = [target_entity_info['location_x'], target_entity_info['location_y']]
                            target_team = target_entity_info['m_iTeamNum']

                            self.attack_target_x = target_pos[0]
                            self.attack_target_y = target_pos[1]
                            self.attack_target_name = target_entity_info['npc_name']
                            self.attack_target_delay = 3
                    elif DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(
                            pb_message.order_type).name == DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_PICKUP_RUNE.name:
                        print("DOTA_UNIT_ORDER_PICKUP_RUNE")
                        '''
                        self.game_time:  -1
                        pb_message:  entindex: 1
                        order_type: 15
                        units: 743
                        target_index: 429
                        queue: false
                        sequence_number: 82
                        flags: 0
                        '''
                        entity_names_string_table = self.string_tables["tables"][7]

                        target_entity = self.entities[pb_message.target_index]
                        # print("target_entity: ", target_entity)

                        print("self.game_time: ", self.game_time)
                        E_Map = utils.EntityMap(target_entity)
                        # for key in E_Map:
                        #    print("key: ", key)
                        #    print("E_Map[key]: ", E_Map[key])

                        # print("rune target_entity.demo_class.name: ", target_entity.demo_class.name)
                        # entity_info = utils.GetRuneInfo(target_entity, entity_names_string_table)

                        # print("rune entity_info: ", target_entity)
                        print("")
                    else:
                        print(DOTA_UNIT_ORDER_TYPES.DOTA_UNIT_ORDER_TYPES(pb_message.order_type).name)
                        print("pb_message: ", pb_message)
                        print("")
                elif cmd == 554:
                    # print("MsgDOTACombatLogEntry")

                    combat_log_names_string_table = self.string_tables["tables"][16]
                    string_table_items = combat_log_names_string_table.items

                    # print("string_table.index: ", string_table.index)
                    # print("string_table.name: ", string_table.name)
                    for item_index in combat_log_names_string_table.items:
                        item = combat_log_names_string_table.items[item_index]
                        # print("item.index: ", item.index)
                        # print("item.key: ", item.key)
                        # print("item.value: ", item.value)
                    # print()

                    pb_message = dota_shared_enums_pb2.CMsgDOTACombatLogEntry()
                    pb_message_string = pb_message.ParseFromString(message)
                    # print("pb_message: ", pb_message)
                    # print("string_table_items: ", string_table_items)

                    # print("utils.DOTA_COMBATLOG_TYPES(pb_message.type).name: ", utils.DOTA_COMBATLOG_TYPES(pb_message.type).name)
                    # print("string_table_items[pb_message.target_name].key: ", string_table_items[pb_message.target_name].key)
                    # print("string_table_items[pb_message.target_source_name].key: ", string_table_items[pb_message.target_source_name].key)
                    # print("string_table_items[pb_message.attacker_name].key: ", string_table_items[pb_message.attacker_name].key)
                    # print("string_table_items[pb_message.damage_source_name].key: ", string_table_items[pb_message.damage_source_name].key)
                    # print("string_table_items[pb_message.inflictor_name].key: ", string_table_items[pb_message.inflictor_name].key)

                    if DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_PURCHASE:
                        # print("buy item: ", string_table_items[pb_message.value].key)
                        pass
                    elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_ITEM:
                        # print("use item: ", string_table_items[pb_message.value].key)
                        pass
                    elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_GOLD:
                        # print("gold: ", pb_message.value)
                        pass
                    elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_ABILITY:
                        pass
                        '''
                        string_table_items[pb_message.target_name].key:  dota_unknown
                        string_table_items[pb_message.target_source_name].key:  dota_unknown
                        string_table_items[pb_message.attacker_name].key:  npc_dota_hero_nevermore
                        string_table_items[pb_message.damage_source_name].key:  dota_unknown
                        string_table_items[pb_message.inflictor_name].key:  nevermore_shadowraze3
                        '''

                        # print("pb_message.ability_level: ", pb_message.ability_level)
                        # print("pb_message.location_x: ", pb_message.location_x)
                        # print("pb_message.location_y: ", pb_message.location_y)
                    elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_MODIFIER_ADD:
                        print("DOTA_COMBATLOG_MODIFIER_ADD")
                        # print("string_table_items[pb_message.target_name].key: ", string_table_items[pb_message.target_name].key)
                        # print("string_table_items[pb_message.attacker_name].key: ", string_table_items[pb_message.attacker_name].key)
                        # print("string_table_items[pb_message.inflictor_name].key: ", string_table_items[pb_message.inflictor_name].key)
                        target_name = string_table_items[pb_message.target_name].key
                        attacker_name = string_table_items[pb_message.attacker_name].key
                        inflictor_name = string_table_items[pb_message.inflictor_name].key

                        # print("target_name 1: ", target_name)
                        target_name = utils.ParseName(target_name)
                        # print("target_name: ", target_name)
                        # print("inflictor_name: ", inflictor_name)

                        # for radiant_hero in self.radiant_heros.keys():
                        #    print("radiant_hero: ", radiant_hero)

                        # print("target_name: ", target_name)
                        # for dire_hero in self.dire_heros.keys():
                        #    print("dire_hero: ", dire_hero)
                        # print("pb_message.attacker_team: ", pb_message.attacker_team)
                        # print("pb_message.target_team: ", pb_message.target_team)

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

                        # print("")
                    elif DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES(
                            pb_message.type) == DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_TYPES.DOTA_COMBATLOG_MODIFIER_REMOVE:
                        print("DOTA_COMBATLOG_MODIFIER_REMOVE")
                        # print("pb_message: ", pb_message)
                        '''
                        pb_message:  type: DOTA_COMBATLOG_MODIFIER_REMOVE
                        target_name: 6
                        attacker_name: 2
                        inflictor_name: 3
                        is_attacker_illusion: false
                        is_attacker_hero: false
                        is_target_illusion: false
                        is_target_hero: true
                        is_visible_radiant: true
                        value: 0
                        health: 620
                        timestamp: 35.56646728515625
                        timestamp_raw: 36.10000228881836
                        modifier_duration: 3.0
                        attacker_team: 2
                        target_team: 2
                        stack_count: 0
                        hidden_modifier: false
                        target_is_self: false
                        modifier_elapsed_duration: 16.399749755859375
                        modifier_purged: false
                        aura_modifier: true
                        modifier_hidden: false
                        '''
                        # self.radiant_heros_modifiers, self.dire_heros_modifiers = {}, {}

                        target_name = string_table_items[pb_message.target_name].key
                        target_name = utils.ParseName(target_name)

                        inflictor_name = string_table_items[pb_message.inflictor_name].key

                        if pb_message.target_team == 2:
                            # print("self.radiant_heros_modifiers: ", self.radiant_heros_modifiers)
                            # print("inflictor_name: ", inflictor_name)
                            # print("inflictor_name in self.radiant_heros_modifiers: ", inflictor_name in self.radiant_heros_modifiers)
                            if target_name != '':
                                if inflictor_name in self.radiant_heros_modifiers[target_name]:
                                    self.radiant_heros_modifiers[target_name].remove(inflictor_name)
                        elif pb_message.target_team == 3:
                            if target_name != '':
                                if inflictor_name in self.dire_heros_modifiers[target_name]:
                                    self.dire_heros_modifiers[target_name].remove(inflictor_name)

                        print("")

                    # DOTA_COMBATLOG_MODIFIER_ADD = 2;
                    # DOTA_COMBATLOG_MODIFIER_REMOVE = 3;

                    '''
                    print("pb_message.is_attacker_illusion: ", pb_message.is_attacker_illusion)
                    print("pb_message.is_attacker_hero: ", pb_message.is_attacker_hero)
                    print("pb_message.is_target_illusion: ", pb_message.is_target_illusion)
                    print("pb_message.is_target_hero: ", pb_message.is_target_hero)
                    print("pb_message.is_visible_radiant: ", pb_message.is_visible_radiant)
                    print("pb_message.is_visible_dire: ", pb_message.is_visible_dire)
                    print("pb_message.value: ", pb_message.value)
                    print("pb_message.health: ", pb_message.health)
                    print("pb_message.timestamp: ", pb_message.timestamp)
                    print("pb_message.stun_duration: ", pb_message.stun_duration)
                    print("pb_message.slow_duration: ", pb_message.slow_duration)
                    print("pb_message.is_ability_toggle_on: ", pb_message.is_ability_toggle_on)
                    print("pb_message.is_ability_toggle_off: ", pb_message.is_ability_toggle_off)
                    print("pb_message.ability_level: ", pb_message.ability_level)
                    print("pb_message.location_x: ", pb_message.location_x)
                    print("pb_message.location_y: ", pb_message.location_y)
                    print("pb_message.gold_reason: ", pb_message.gold_reason)
                    print("pb_message.timestamp_raw: ", pb_message.timestamp_raw)
                    print("pb_message.modifier_duration: ", pb_message.modifier_duration)
                    print("pb_message.xp_reason: ", pb_message.xp_reason)
                    print("pb_message.last_hits: ", pb_message.last_hits)
                    print("pb_message.attacker_team: ", pb_message.attacker_team)
                    print("pb_message.target_team: ", pb_message.target_team)
                    print("pb_message.obs_wards_placed: ", pb_message.obs_wards_placed)
                    print("pb_message.assist_player0: ", pb_message.assist_player0)
                    print("pb_message.assist_player1: ", pb_message.assist_player1)
                    print("pb_message.assist_player2: ", pb_message.assist_player2)
                    print("pb_message.assist_player3: ", pb_message.assist_player3)
                    print("pb_message.stack_count: ", pb_message.stack_count)
                    print("pb_message.hidden_modifier: ", pb_message.hidden_modifier)
                    print("pb_message.is_target_building: ", pb_message.is_target_building)
                    print("pb_message.neutral_camp_type: ", pb_message.neutral_camp_type)
                    print("pb_message.rune_type: ", pb_message.rune_type)
                    print("pb_message.assist_players: ", pb_message.assist_players)
                    print("pb_message.is_heal_save: ", pb_message.is_heal_save)
                    print("pb_message.is_ultimate_ability: ", pb_message.is_ultimate_ability)
                    print("pb_message.attacker_hero_level: ", pb_message.attacker_hero_level)
                    print("pb_message.target_hero_level: ", pb_message.target_hero_level)
                    print("pb_message.xpm: ", pb_message.xpm)
                    print("pb_message.gpm: ", pb_message.gpm)
                    print("pb_message.target_is_self: ", pb_message.target_is_self)
                    print("pb_message.damage_type: ", pb_message.damage_type)
                    print("pb_message.invisibility_modifier: ", pb_message.invisibility_modifier)
                    print("pb_message.damage_category: ", pb_message.damage_category)
                    print("pb_message.networth: ", pb_message.networth)
                    print("pb_message.building_type: ", pb_message.building_type)
                    print("pb_message.modifier_elapsed_duration: ", pb_message.modifier_elapsed_duration)
                    print("pb_message.silence_modifier: ", pb_message.silence_modifier)
                    print("pb_message.heal_from_lifesteal: ", pb_message.heal_from_lifesteal)
                    print("pb_message.modifier_purged: ", pb_message.modifier_purged)
                    print("pb_message.spell_evaded: ", pb_message.spell_evaded)
                    print("pb_message.motion_controller_modifier: ", pb_message.motion_controller_modifier)
                    print("pb_message.long_range_kill: ", pb_message.long_range_kill)
                    print("pb_message.modifier_purge_ability: ", pb_message.modifier_purge_ability)
                    print("pb_message.modifier_purge_npc: ", pb_message.modifier_purge_npc)
                    print("pb_message.root_modifier: ", pb_message.root_modifier)
                    print("pb_message.total_unit_death_count: ", pb_message.total_unit_death_count)
                    print("pb_message.aura_modifier: ", pb_message.aura_modifier)
                    print("pb_message.armor_debuff_modifier: ", pb_message.armor_debuff_modifier)
                    print("pb_message.no_physical_damage_modifier: ", pb_message.no_physical_damage_modifier)
                    print("pb_message.modifier_ability: ", pb_message.modifier_ability)
                    print("pb_message.modifier_hidden: ", pb_message.modifier_hidden)
                    print("pb_message.unit_status_label: ", pb_message.unit_status_label)
                    print("pb_message.spell_generated_attack: ", pb_message.spell_generated_attack)
                    print("pb_message.at_night_time: ", pb_message.at_night_time)
                    print("pb_message.attacker_has_scepter: ", pb_message.attacker_has_scepter)
                    '''
                    # print("")
            except:
                pass

    def parse_user_message(self, message):
        cmd = message.msg_type
        if cmd not in messages.COMBINED_USER_MESSAGE_TYPES:
            raise IndexError("Unknown user message cmd: %s" % (cmd,))

        reader = FileReader.FileReader(StringIO(message.msg_data))
        message_type = messages.COMBINED_USER_MESSAGE_TYPES[cmd]
        user_message = reader.read_message(message_type, read_size=False)

        self.run_hooks(user_message)

    def parse_game_event_list(self, eventlist):
        self.eventlist = eventlist

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
        self.important("Parsing demo file '%s'" % (self.filename,))
        with open(self.filename, 'rb') as f:
            p = f.read()
            reader = FileReader.FileReader(BytesIO(p))

            filestamp = reader.read(8)

            Dummy = reader.read(8)
            if filestamp.decode('utf-8') != "PBDEMS2\x00":
                raise ValueError("Invalid replay - incorrect filestamp")

            buff = BytesIO(f.read())

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

                # print("tick: ", tick)
                print("cmd 1: ", cmd)

                if message_type == demo_pb2.CDemoSendTables:
                    # print("demo_pb2.CDemoSendTables")

                    table_reader = FileReader.FileReader(BytesIO(message.data))
                    size = table_reader.read_var_uint32()
                    message = table_reader.read_bytes(size)

                    pb_message = netmessages_pb2.CSVCMsg_FlattenedSerializer()
                    pb_message_string = pb_message.ParseFromString(message)

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

                                if field.serializer_name != None:
                                    field.serializer = self.serializers[field.serializer_name]
                                elif field.field_type.base_type == "CBodyComponent":
                                    field.serializer = self.serializers[field.serializer_name]
                                else:
                                    field.serializer = None

                                for field_patch in patches:
                                    field_patch.patch(field)

                                if field.serializer != None or field.field_type.base_type == "CBodyComponent":
                                    if (field.field_type.base_type in utils.pointerTypes) and utils.pointerTypes[
                                        field.field_type.base_type]:
                                        field.set_model(FieldModelEnum.fieldModelFixedTable.value)
                                    else:
                                        field.set_model(FieldModelEnum.fieldModelVariableTable.value)
                                elif field.field_type.count > 0 and field.field_type.base_type != "char":
                                    # print("elif field.field_type.count > 0")
                                    field.set_model(FieldModelEnum.fieldModelFixedArray.value)
                                elif field.field_type.base_type == "CUtlVector" or field.field_type.base_type == "CNetworkUtlVectorBase":
                                    # print("elif field.field_type.base_type == \"CUtlVector\"")
                                    field.set_model(FieldModelEnum.fieldModelVariableArray.value)
                                else:
                                    if field_index == 35:
                                        compare = field.serializer_name == ""
                                    field.set_model(FieldModelEnum.fieldModelSimple.value)

                                fields[field_index] = field

                            serializer.fields.append(fields[field_index])

                        self.serializers[serializer.name] = serializer

                        if serializer.name in self.classes_by_name:
                            self.classes_by_name[serializer.name].serializer = serializer
                elif message_type == demo_pb2.CDemoClassInfo:
                    classes = message.classes

                    for c in classes:
                        demo_class = DemoClass.DemoClass(c.class_id, c.network_name, self.serializers[c.network_name])

                        self.classes_by_id[c.class_id] = demo_class
                        self.classes_by_name[c.network_name] = demo_class

                    self.class_info = True

                    self.update_instance_baseline()
                elif message_type == demo_pb2.CDemoSyncTick:
                    continue

                self.run_hooks(message)

                frame += 1
                if self.frames and frame > self.frames:
                    break
