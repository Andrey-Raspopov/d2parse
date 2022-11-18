import copy
import re
import struct
from io import BytesIO
from typing import NewType

import numpy as np

from Field.Field import FieldModelEnum
from Field.FieldPatch import FieldPatch
from Field.FieldPath import FieldPath
from Field.FieldPathOp import FieldPathOp
from Field.FieldState import FieldState
from FileReader import FileReader
from HuffmanLeaf import HuffmanLeaf

from HuffmanNode import HuffmanNode
from QuantizedFloatDecoder import QuantizedFloatDecoder
from StringTableItem import StringTableItem

pointerTypes = {
    "PhysicsRagdollPose_t": True,
    "CBodyComponent": True,
    "CEntityIdentity": True,
    "CPhysicsComponent": True,
    "CRenderComponent": True,
    "CDOTAGamerules": True,
    "CDOTAGameManager": True,
    "CDOTASpectatorGraphManager": True,
    "CPlayerLocalData": True,
    "CPlayer_CameraServices": True,
}


def SetFieldState(s, fp, v):
    dummy_field_state = FieldState()

    x = s
    z = 0
    for i in range(fp.last + 1):
        z = fp.path[i]
        y = len(x.state)
        if y < z + 2:
            k = [None] * max(z + 2, y * 2)
            for j in range(0, len(x.state)):
                k[j] = copy.deepcopy(x.state[j])

            x.state = k

        if i == fp.last:
            if type(x.state[z]) != type(dummy_field_state):
                x.state[z] = v

            return

        if type(x.state[z]) != type(dummy_field_state):
            x.state[z] = FieldState()

        x = x.state[z]


def GetFieldState(s, fp):
    dummy_field_state = FieldState()

    x = s
    z = 0
    for i in range(fp.last + 1):
        z = fp.path[i]

        if len(x.state) < z + 2:
            return None

        if i == fp.last:
            return x.state[z]

        if type(x.state[z]) != type(dummy_field_state):
            return None

        x = x.state[z]

    # time.sleep(1)

    return None


def GetFieldPathsFromSerializer(s, fp, state):
    serializer = s

    results = []
    for i, f in enumerate(serializer.fields):
        fp.path[fp.last] = i

        result = GetFieldPathsFromField(f, fp, state)
        if len(result) != 0:
            if type(result[0]) != list:
                x_name = [path.path for path in result]

                for value in result:
                    results.append(value)
            else:
                x_name = [path.path for path in result[0]]

                for value in result[0]:
                    results.append(value)

    return results


def GetFieldPathsFromField(f, fp, state):
    dummy_field_state = FieldState()
    x = []

    if f.model == FieldModelEnum.fieldModelFixedArray.value:
        sub = GetFieldState(state, fp)
        if type(sub) == type(dummy_field_state):
            fp.last += 1
            for i, v in enumerate(sub.state):
                if v != None:
                    fp.path[fp.last] = i
                    x.append(copy.deepcopy(fp))

            fp.last -= 1
    elif f.model == FieldModelEnum.fieldModelFixedTable.value:
        sub = GetFieldState(state, fp)
        if type(sub) == type(dummy_field_state):
            fp.last += 1
            serializer_of_field = f.serializer
            x.append(GetFieldPathsFromSerializer(serializer_of_field, fp, sub))
            fp.last -= 1
    elif f.model == FieldModelEnum.fieldModelVariableArray.value:
        sub = GetFieldState(state, fp)
        if type(sub) == type(dummy_field_state):
            fp.last += 1
            for i, v in enumerate(sub.state):
                if v != None:
                    fp.path[fp.last] = i
                    x.append(copy.deepcopy(fp))

            fp.last -= 1
    elif f.model == FieldModelEnum.fieldModelVariableTable.value:
        sub = GetFieldState(state, fp)
        if type(sub) == type(dummy_field_state):
            fp.last += 2
            for i, v in enumerate(sub.state):
                if type(v) == type(dummy_field_state):
                    fp.path[fp.last - 1] = i
                    serializer_of_field = f.serializer
                    x.append(GetFieldPathsFromSerializer(serializer_of_field, fp, v))

            fp.last -= 2
    elif f.model == FieldModelEnum.fieldModelSimple.value:
        x.append(copy.deepcopy(fp))

    return x


def GetNameForFieldPathFromSerializer(s, fp, pos):
    field_of_serializer = s.fields[fp.path[pos]]
    result = GetNameForFieldPathFromField(field_of_serializer, fp, pos + 1)
    result = "".join(result)

    return result


def GetNameForFieldPathFromField(f, fp, pos):
    x = [f.var_name]

    if f.model == FieldModelEnum.fieldModelFixedArray.value:
        if fp.last == pos:
            result = "%04d" % (fp.path[pos])
            x.append(result)
    elif f.model == FieldModelEnum.fieldModelFixedTable.value:
        if fp.last >= pos:
            serializer_of_field = f.serializer
            result = GetNameForFieldPathFromSerializer(serializer_of_field, fp, pos)
            x.append(result)
    elif f.model == FieldModelEnum.fieldModelVariableArray.value:
        if fp.last == pos:
            result = "%04d" % (fp.path[pos])
            x.append(result)
    elif f.model == FieldModelEnum.fieldModelVariableTable.value:
        if fp.last != pos - 1:
            result = "%04d" % (fp.path[pos])
            x.append(result)

            if fp.last != pos:
                serializer_of_field = f.serializer
                result = GetNameForFieldPathFromSerializer(serializer_of_field, fp, pos + 1)
                x.append(result)

    return x


def EntityMap(entity):
    demo_class = entity.demo_class
    serializer = demo_class.serializer

    fp = FieldPath()
    values = {}
    field_paths = GetFieldPathsFromSerializer(serializer, fp, entity.state)

    m_iPlayerID = None
    m_cellX = None
    for field_path in field_paths:
        entity_result = GetNameForFieldPathFromSerializer(serializer, field_path, 0)
        value = GetFieldState(entity.state, field_path)
        if value == None:
            value = "None"

        if entity_result == 'm_iPlayerID':
            # print("value: ", value)
            m_iPlayerID = value

        if entity_result == 'CBodyComponentm_cellX':
            m_cellX = value

        values[entity_result] = GetFieldState(entity.state, field_path)

    return values


def ParseName(name):
    name_list = name.split('_')[3:]
    # name = ''.join(name_list)
    # name_split = re.sub( r"([A-Z])", r" \1", name).split()
    # for i in range(len(name_split)):
    #    name_split[i] = name_split[i].lower()

    name = "_".join(name_list)

    return name


def GetHeroName(demo_class):
    demo_class_name = demo_class.name
    result = demo_class_name.startswith('CDOTA_Unit_Hero')
    if result == True:
        hero_name_list = demo_class_name.split('_')[3:]
        hero_name = ''.join(hero_name_list)
        hero_name_split = re.sub(r"([A-Z])", r" \1", hero_name).split()
        for i in range(len(hero_name_split)):
            hero_name_split[i] = hero_name_split[i].lower()

        hero_name = "_".join(hero_name_split)

        return hero_name
    else:
        return None


def GetNpcName(demo_class):
    demo_class_name = demo_class.name
    result = demo_class_name.startswith('CDOTA_BaseNPC')
    if result == True:
        npc_name_list = demo_class_name.split('_')[2:]
        npc_name = ''.join(npc_name_list)
        npc_name_split = re.sub(r"([A-Z])", r" \1", npc_name).split()
        for i in range(len(npc_name_split)):
            npc_name_split[i] = npc_name_split[i].lower()

        npc_name = "_".join(npc_name_split)

        return npc_name
    else:
        return None


def GetItemInfo(item_handle, entities, entity_names_string_table):
    handle_mask = (1 << 14) - 1

    item_name = None
    item_cool = 0
    item_num = 0
    if item_handle != 16777215:
        item_handle &= handle_mask

        if item_handle in entities:
            item_entity = entities[item_handle]
            if item_entity != None:
                item_E_Map = EntityMap(item_entity)

                if item_E_Map["m_pEntitym_nameStringableIndex"] != -1:
                    m_pEntitym_nameStringableIndex = item_E_Map["m_pEntitym_nameStringableIndex"]
                    item_name = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                    item_name = item_name.key
                    item_name = item_name.split('_')[1:]
                    item_name = "_".join(item_name)
                    # print("item_name: ", item_name)
                    if item_name.split('_')[0] == "recipe":
                        item_name = "recipe"

                    item_cool = item_E_Map["m_fCooldown"]
                    item_num = item_E_Map["m_iInitialCharges"]

    return item_name, item_cool, item_num


def GetItemsInfo(entity_info, entities, entity_names_string_table):
    # print("entity_info['m_hItems0003']: ", entity_info['m_hItems0003'])
    item_name_0, item_cool_0, item_num_0 = GetItemInfo(entity_info['m_hItems0000'], entities, entity_names_string_table)
    item_name_1, item_cool_1, item_num_1 = GetItemInfo(entity_info['m_hItems0001'], entities, entity_names_string_table)
    item_name_2, item_cool_2, item_num_2 = GetItemInfo(entity_info['m_hItems0002'], entities, entity_names_string_table)
    item_name_3, item_cool_3, item_num_3 = GetItemInfo(entity_info['m_hItems0003'], entities, entity_names_string_table)
    item_name_4, item_cool_4, item_num_4 = GetItemInfo(entity_info['m_hItems0004'], entities, entity_names_string_table)
    item_name_5, item_cool_5, item_num_5 = GetItemInfo(entity_info['m_hItems0005'], entities, entity_names_string_table)

    return {
        "item0": {"item_name": item_name_0, "item_cool": item_cool_0, "item_num": item_num_0},
        "item1": {"item_name": item_name_1, "item_cool": item_cool_1, "item_num": item_num_1},
        "item2": {"item_name": item_name_2, "item_cool": item_cool_2, "item_num": item_num_2},
        "item3": {"item_name": item_name_3, "item_cool": item_cool_3, "item_num": item_num_3},
        "item4": {"item_name": item_name_4, "item_cool": item_cool_4, "item_num": item_num_4},
        "item5": {"item_name": item_name_5, "item_cool": item_cool_5, "item_num": item_num_5}
    }


def GetAbilityInfo(ability_handle, entities, entity_names_string_table):
    handle_mask = (1 << 14) - 1

    ability_name = None
    ability_cool = 0
    ability_level = 0
    if ability_handle != 16777215:
        ability_handle &= handle_mask

        ability_entity = entities[ability_handle]
        if ability_entity != None:
            ability_E_Map = EntityMap(ability_entity)
            # print("ability_E_Map: ", ability_E_Map)

            if ability_E_Map["m_pEntitym_nameStringableIndex"] != -1:
                m_pEntitym_nameStringableIndex = ability_E_Map["m_pEntitym_nameStringableIndex"]
                ability_name = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
                ability_name = ability_name.key

                ability_cool = ability_E_Map["m_fCooldown"]
                ability_level = ability_E_Map["m_iLevel"]
                # print("ability_name: ", ability_name)
                # print("ability_E_Map: ", ability_E_Map)

    return ability_name, ability_cool, ability_level


def GetabilitiesInfo(entity_info, entities, entity_names_string_table):
    # print("entity_info['m_hAbilities0003']: ", entity_info['m_hAbilities0003'])
    ability_name_0, ability_cool_0, ability_level_0 = GetAbilityInfo(entity_info['m_hAbilities0000'], entities,
                                                                     entity_names_string_table)
    ability_name_1, ability_cool_1, ability_level_1 = GetAbilityInfo(entity_info['m_hAbilities0001'], entities,
                                                                     entity_names_string_table)
    ability_name_2, ability_cool_2, ability_level_2 = GetAbilityInfo(entity_info['m_hAbilities0002'], entities,
                                                                     entity_names_string_table)
    ability_name_3, ability_cool_3, ability_level_3 = GetAbilityInfo(entity_info['m_hAbilities0003'], entities,
                                                                     entity_names_string_table)
    ability_name_4, ability_cool_4, ability_level_4 = GetAbilityInfo(entity_info['m_hAbilities0004'], entities,
                                                                     entity_names_string_table)
    ability_name_5, ability_cool_5, ability_level_5 = GetAbilityInfo(entity_info['m_hAbilities0005'], entities,
                                                                     entity_names_string_table)

    return {
        "ability0": {"ability_name": ability_name_0, "ability_cool": ability_cool_0, "ability_level": ability_level_0},
        "ability1": {"ability_name": ability_name_1, "ability_cool": ability_cool_1, "ability_level": ability_level_1},
        "ability2": {"ability_name": ability_name_2, "ability_cool": ability_cool_2, "ability_level": ability_level_2},
        "ability3": {"ability_name": ability_name_3, "ability_cool": ability_cool_3, "ability_level": ability_level_3},
        "ability4": {"ability_name": ability_name_4, "ability_cool": ability_cool_4, "ability_level": ability_level_4},
        "ability5": {"ability_name": ability_name_5, "ability_cool": ability_cool_5, "ability_level": ability_level_5}
    }


MAP_SIZE = 32768
MAP_HALF_SIZE = MAP_SIZE / 2
CELL_SIZE = 128


def GetHeroInfo(entity):
    E_Map = EntityMap(entity)
    # print("E_Map['m_hModifierParent']: ", E_Map['m_hModifierParent'])

    # for key in E_Map:
    #    print("key: ", key)
    #    print("E_Map[key]: ", E_Map[key])
    # print("")

    hero_name = GetHeroName(entity.demo_class)

    m_iPlayerID = None
    m_cellX = None
    m_cellY = None
    m_vecX = None
    m_vecY = None
    m_iCurrentXP = None
    m_iCurrentLevel = None
    m_iTeamNum = None
    angRotation = None

    m_hAbilities0000 = None
    m_hAbilities0001 = None
    m_hAbilities0002 = None
    m_hAbilities0003 = None
    m_hAbilities0004 = None
    m_hAbilities0005 = None

    m_hItems0000 = None
    m_hItems0001 = None
    m_hItems0002 = None
    m_hItems0003 = None
    m_hItems0004 = None
    m_hItems0005 = None

    m_bIsWaitingToSpawn = None

    if 'm_iPlayerID' in E_Map:
        m_iPlayerID = E_Map["m_iPlayerID"]

    if 'CBodyComponentm_cellX' in E_Map:
        m_cellX = E_Map["CBodyComponentm_cellX"]
        m_cellY = E_Map["CBodyComponentm_cellY"]

    if 'CBodyComponentm_vecX' in E_Map:
        m_vecX = E_Map["CBodyComponentm_vecX"]
        m_vecY = E_Map["CBodyComponentm_vecY"]

    if 'CBodyComponentm_angRotation' in E_Map:
        angRotation = E_Map["CBodyComponentm_angRotation"][1]

    if 'm_iMaxHealth' in E_Map:
        m_iHealth = E_Map["m_iHealth"]
        m_iMaxHealth = E_Map["m_iMaxHealth"]

    if 'm_iCurrentXP' in E_Map:
        m_iCurrentXP = E_Map["m_iCurrentXP"]

    if 'm_iCurrentLevel' in E_Map:
        m_iCurrentLevel = E_Map["m_iCurrentLevel"]

    if 'm_iTeamNum' in E_Map:
        m_iTeamNum = E_Map["m_iTeamNum"]

    if 'm_flMaxMana' in E_Map:
        m_flMana = E_Map["m_flMana"]
        m_flMaxMana = E_Map["m_flMaxMana"]

    if 'm_hAbilities0000' in E_Map:
        m_hAbilities0000 = E_Map["m_hAbilities0000"]
        m_hAbilities0001 = E_Map["m_hAbilities0001"]
        m_hAbilities0002 = E_Map["m_hAbilities0002"]
        m_hAbilities0003 = E_Map["m_hAbilities0003"]
        m_hAbilities0004 = E_Map["m_hAbilities0004"]
        m_hAbilities0005 = E_Map["m_hAbilities0005"]

    if 'm_hItems0000' in E_Map:
        m_hItems0000 = E_Map["m_hItems0000"]
        m_hItems0001 = E_Map["m_hItems0001"]
        m_hItems0002 = E_Map["m_hItems0002"]
        m_hItems0003 = E_Map["m_hItems0003"]
        m_hItems0004 = E_Map["m_hItems0004"]
        m_hItems0005 = E_Map["m_hItems0005"]

    if 'm_bIsWaitingToSpawn' in E_Map:
        m_bIsWaitingToSpawn = E_Map["m_bIsWaitingToSpawn"]

    x_temp = m_cellX * CELL_SIZE + m_vecX
    y_temp = m_cellY * CELL_SIZE + m_vecY
    hero_location_x = -x_temp + (MAP_HALF_SIZE / 2)
    hero_location_y = y_temp - (MAP_HALF_SIZE / 2)

    info = {"m_iPlayerID": m_iPlayerID,
            "hero_location_x": hero_location_x / 4.0,
            "hero_location_y": hero_location_y / 4.0,
            "angRotation": angRotation,
            "m_iCurrentXP": m_iCurrentXP,
            "m_iCurrentLevel": m_iCurrentLevel,
            "hero_name": hero_name,
            "m_iHealth": m_iHealth,
            "m_iMaxHealth": m_iMaxHealth,
            "m_iTeamNum": m_iTeamNum,
            "m_flMana": m_flMana,
            "m_flMaxMana": m_flMaxMana,
            "m_hAbilities0000": m_hAbilities0000,
            "m_hAbilities0001": m_hAbilities0001,
            "m_hAbilities0002": m_hAbilities0002,
            "m_hAbilities0003": m_hAbilities0003,
            "m_hAbilities0004": m_hAbilities0004,
            "m_hAbilities0005": m_hAbilities0005,
            "m_hItems0000": m_hItems0000,
            "m_hItems0001": m_hItems0001,
            "m_hItems0002": m_hItems0002,
            "m_hItems0003": m_hItems0003,
            "m_hItems0004": m_hItems0004,
            "m_hItems0005": m_hItems0005,
            "m_bIsWaitingToSpawn": m_bIsWaitingToSpawn
            }

    return info


def GetNpcInfo(entity):
    E_Map = EntityMap(entity)

    npc_name = GetNpcName(entity.demo_class)

    m_nEntityId = None
    m_cellX = None
    m_cellY = None
    m_vecX = None
    m_vecY = None
    m_iTeamNum = None
    m_hModel = None

    handle_mask = (1 << 14) - 1

    if 'm_nEntityId' in E_Map:
        m_nEntityId = E_Map["m_nEntityId"]
        m_nEntityId &= handle_mask

    if 'CBodyComponentm_cellX' in E_Map:
        m_cellX = E_Map["CBodyComponentm_cellX"]
        m_cellY = E_Map["CBodyComponentm_cellY"]

    if 'CBodyComponentm_vecX' in E_Map:
        m_vecX = E_Map["CBodyComponentm_vecX"]
        m_vecY = E_Map["CBodyComponentm_vecY"]

    if 'm_iMaxHealth' in E_Map:
        m_iHealth = E_Map["m_iHealth"]
        m_iMaxHealth = E_Map["m_iMaxHealth"]

    if 'm_iTeamNum' in E_Map:
        m_iTeamNum = E_Map["m_iTeamNum"]

    if 'CBodyComponentm_hModel' in E_Map:
        m_hModel = E_Map["CBodyComponentm_hModel"]
        m_hModel &= handle_mask

    x_temp = m_cellX * CELL_SIZE + m_vecX
    y_temp = m_cellY * CELL_SIZE + m_vecY
    location_x = -x_temp + (MAP_HALF_SIZE / 2)
    location_y = y_temp - (MAP_HALF_SIZE / 2)

    info = {
        "npc_name": npc_name,
        "m_nEntityId": m_nEntityId,
        "location_x": location_x / 4.0,
        "location_y": location_y / 4.0,
        "m_iHealth": m_iHealth,
        "m_iMaxHealth": m_iMaxHealth,
        "m_iTeamNum": m_iTeamNum,
        "m_hModel": m_hModel
    }

    return info


def GetRuneInfo(entity, entity_names_string_table):
    E_Map = EntityMap(entity)
    # for key in E_Map:
    # print("key: ", key)
    # print("E_Map[key]: ", E_Map[key])
    # print("")

    name = None
    m_nEntityId = None
    m_cellX = None
    m_cellY = None
    m_vecX = None
    m_vecY = None
    m_iTeamNum = None
    m_pEntitym_nameStringableIndex = None

    handle_mask = (1 << 14) - 1

    if 'm_nEntityId' in E_Map:
        m_nEntityId = E_Map["m_nEntityId"]
        m_nEntityId &= handle_mask

    if 'CBodyComponentm_cellX' in E_Map:
        m_cellX = E_Map["CBodyComponentm_cellX"]
        m_cellY = E_Map["CBodyComponentm_cellY"]

    if 'CBodyComponentm_vecX' in E_Map:
        m_vecX = E_Map["CBodyComponentm_vecX"]
        m_vecY = E_Map["CBodyComponentm_vecY"]

    if 'm_pEntitym_nameStringableIndex' in E_Map:
        m_pEntitym_nameStringableIndex = E_Map["m_pEntitym_nameStringableIndex"]
        # print("m_pEntitym_nameStringableIndex: ", m_pEntitym_nameStringableIndex)
        if m_pEntitym_nameStringableIndex != -1:
            name = entity_names_string_table.items[m_pEntitym_nameStringableIndex]
            # print("name: ", name)

    x_temp = m_cellX * CELL_SIZE + m_vecX
    y_temp = m_cellY * CELL_SIZE + m_vecY
    location_x = -x_temp + (MAP_HALF_SIZE / 2)
    location_y = y_temp - (MAP_HALF_SIZE / 2)

    info = {"m_nEntityId": m_nEntityId,
            "location_x": location_x / 4.0,
            "location_y": location_y / 4.0,
            "name": name
            }

    return info


def ParseStringTable(buf, num_updates, name, user_data_fixed_size, user_data_size, user_data_size_bits, flags):
    items = []

    r = FileReader(BytesIO(buf))
    index = -1
    keys = []
    if len(buf) != 0:
        for i in range(0, num_updates):
            key = ""
            value = []

            incr = r.read_boolean()
            if incr == True:
                index += 1
            else:
                index = r.read_var_uint32() + 1

            has_key = r.read_boolean()
            if has_key:
                useHistory = r.read_boolean()
                if useHistory:
                    pos = r.read_bits(5)
                    size = r.read_bits(5)

                    if int(pos) >= len(keys):
                        read_string = r.read_string().decode('utf-8')
                        key += read_string
                    else:
                        s = keys[pos]

                        if int(size) > len(s):
                            read_string = r.read_string().decode('utf-8')
                            key += s + read_string
                        else:
                            read_string = r.read_string().decode('utf-8')
                            key += s[0:size] + read_string
                else:
                    read_string = r.read_string().decode('utf-8')
                    key = read_string

                stringtableKeyHistorySize = 32

                if len(keys) >= stringtableKeyHistorySize:
                    for k in range(0, len(keys) - 1):
                        keys[k] = copy.deepcopy(keys[k + 1])

                    keys[len(keys) - 1] = ""
                    keys = keys[:len(keys) - 1]

                keys.append(key)

            has_value = r.read_boolean()
            if has_value:
                bit_size = 0
                if user_data_fixed_size:
                    bit_size = user_data_size_bits
                else:
                    if flags & 0x1 != 0:
                        value = r.read_boolean()

                    bit_size = r.read_bits(17) * 8

                value = r.read_bits_as_bytes(bit_size)

            # print("key: ", key)
            # print("value: ", value)
            new_item = StringTableItem(index, key, value)
            items.append(new_item)

        # print("")

    return items


def field_patch_func_1(f):
    case_list_1 = ["angExtraLocalAngles", "angLocalAngles", "m_angInitialAngles",
                   "m_angRotation", "m_ragAngles", "m_vLightDirection"]

    case_list_2 = ["dirPrimary", "localSound", "m_flElasticity", "m_location",
                   "m_poolOrigin", "m_ragPos", "m_vecEndPos", "m_vecLadderDir",
                   "m_vecPlayerMountPositionBottom", "m_vecPlayerMountPositionTop",
                   "m_viewtarget", "m_WorldMaxs", "m_WorldMins", "origin", "vecLocalOrigin"]

    if f.var_name in case_list_1:
        if f.parent_name == "CBodyComponentBaseAnimatingOverlay":
            f.encoder = "qangle_pitch_yaw"
        else:
            f.encoder = "QAngle"
    elif f.var_name in case_list_2:
        f.encoder = "normal"


def field_patch_func_2(f):
    if f.var_name in ["m_flMana", "m_flMaxMana"]:
        f.low_value = None
        f.high_value = 8192


def field_patch_func_3(f):
    if f.var_name in ["m_bItemWhiteList", "m_bWorldTreeState", "m_iPlayerIDsInControl", "m_iPlayerSteamID",
                      "m_ulTeamBannerLogo", "m_ulTeamBaseLogo", "m_ulTeamLogo"]:
        f.encoder = "fixed64"


def field_patch_func_4(f):
    if f.var_name in ["m_flSimulationTime", "m_flAnimTime"]:
        f.encoder = "simtime"
    elif f.var_name in ["m_flRuneTime"]:
        f.encoder = "runetime"


FieldPatches = [
    FieldPatch(0, 990, field_patch_func_1),
    FieldPatch(0, 954, field_patch_func_2),
    FieldPatch(1016, 1027, field_patch_func_3),
    FieldPatch(0, 0, field_patch_func_4),
]


def PlusOne(r, fp):
    fp.path[fp.last] += 1


def PlusTwo(r, fp):
    fp.path[fp.last] += 2


def PlusThree(r, fp):
    fp.path[fp.last] += 3


def PlusFour(r, fp):
    fp.path[fp.last] += 4


def PlusN(r, fp):
    fp.path[fp.last] += (int(r.read_ubit_var_field_path()) + 5)


def PushOneLeftDeltaZeroRightZero(r, fp):
    fp.last += 1
    fp.path[fp.last] = 0


def PushOneLeftDeltaZeroRightNonZero(r, fp):
    fp.last += 1
    fp.path[fp.last] = int(r.read_ubit_var_field_path())


def PushOneLeftDeltaOneRightZero(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] = 0


def PushOneLeftDeltaOneRightNonZero(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] = int(r.read_ubit_var_field_path())


def PushOneLeftDeltaNRightZero(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] = 0


def PushOneLeftDeltaNRightNonZero(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var_field_path()) + 2
    fp.last += 1
    fp.path[fp.last] = int(r.read_ubit_var_field_path()) + 1


def PushOneLeftDeltaNRightNonZeroPack6Bits(r, fp):
    fp.path[fp.last] += int(r.read_bits(3)) + 2
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(3)) + 1


def PushOneLeftDeltaNRightNonZeroPack8Bits(r, fp):
    fp.path[fp.last] += int(r.read_bits(4)) + 2
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(4)) + 1


def PushTwoLeftDeltaZero(r, fp):
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushTwoPack5LeftDeltaZero(r, fp):
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(5))


def PushThreeLeftDeltaZero(r, fp):
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushThreePack5LeftDeltaZero(r, fp):
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] = int(r.read_bits(5))


def PushTwoLeftDeltaOne(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushTwoPack5LeftDeltaOne(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))


def PushThreeLeftDeltaOne(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushThreePack5LeftDeltaOne(r, fp):
    fp.path[fp.last] += 1
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))


def PushTwoLeftDeltaN(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var()) + 2
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushTwoPack5LeftDeltaN(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var()) + 2
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))


def PushThreeLeftDeltaN(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var()) + 2
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())
    fp.last += 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushThreePack5LeftDeltaN(r, fp):
    fp.path[fp.last] += int(r.read_ubit_var()) + 2
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))
    fp.last += 1
    fp.path[fp.last] += int(r.read_bits(5))


def PushN(r, fp):
    n = int(r.read_ubit_var())
    fp.path[fp.last] += int(r.read_ubit_var())
    for i in range(0, n):
        fp.last += 1
        fp.path[fp.last] += int(r.read_ubit_var_field_path())


def PushNAndNonTopological(r, fp):
    for i in range(0, fp.last + 1):
        if r.read_boolean():
            fp.path[i] += int(r.read_var_int32()) + 1

    count = int(r.read_ubit_var())
    for i in range(0, count):
        fp.last += 1
        fp.path[fp.last] = int(r.read_ubit_var_field_path())


def PopOnePlusOne(r, fp):
    fp.path[fp.last] = 0
    fp.last -= 1
    fp.path[fp.last] += 1


def PopOnePlusN(r, fp):
    fp.path[fp.last] = 0
    fp.last -= 1
    fp.path[fp.last] += int(r.read_ubit_var_field_path()) + 1


def PopAllButOnePlusOne(r, fp):
    pop_num = fp.last
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[0] += 1


def PopAllButOnePlusN(r, fp):
    pop_num = fp.last
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[0] += int(r.read_ubit_var_field_path()) + 1


def PopAllButOnePlusNPack3Bits(r, fp):
    pop_num = fp.last
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[0] += int(r.read_bits(3)) + 1


def PopAllButOnePlusNPack6Bits(r, fp):
    pop_num = fp.last
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[0] += int(r.read_bits(6)) + 1


def PopNPlusOne(r, fp):
    pop_num = int(r.read_ubit_var_field_path())
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[fp.last] += 1


def PopNPlusN(r, fp):
    pop_num = int(r.read_ubit_var_field_path())
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    fp.path[fp.last] += int(r.read_var_int32())


def PopNAndNonTopographical(r, fp):
    pop_num = int(r.read_ubit_var_field_path())
    for i in range(0, pop_num):
        fp.path[fp.last] = 0
        fp.last -= 1

    for i in range(0, fp.last + 1):
        if r.read_boolean():
            fp.path[i] += int(r.read_var_int32())


def NonTopoComplex(r, fp):
    for i in range(0, fp.last + 1):
        if r.read_boolean():
            fp.path[i] += int(r.read_var_int32())


def NonTopoPenultimatePlusOne(r, fp):
    fp.path[fp.last - 1] += 1


def NonTopoComplexPack4Bits(r, fp):
    for i in range(0, fp.last + 1):
        if r.read_boolean():
            fp.path[i] += int(r.read_bits(4)) - 7


def FieldPathEncodeFinish(r, fp):
    fp.done = True


EntityOp = NewType('EntityOp', int)
EntityOpNone = EntityOp(0x00)
EntityOpCreated = EntityOp(0x01)
EntityOpUpdated = EntityOp(0x02)
EntityOpDeleted = EntityOp(0x04)
EntityOpEntered = EntityOp(0x08)
EntityOpLeft = EntityOp(0x10)
EntityOpCreatedEntered = EntityOp(EntityOpCreated | EntityOpEntered)
EntityOpUpdatedEntered = EntityOp(EntityOpUpdated | EntityOpEntered)
EntityOpDeletedLeft = EntityOp(EntityOpDeleted | EntityOpLeft)

entityOpNames = {
    EntityOpNone: "None",
    EntityOpCreated: "Created",
    EntityOpUpdated: "Updated",
    EntityOpDeleted: "Deleted",
    EntityOpEntered: "Entered",
    EntityOpLeft: "Left",
    EntityOpCreatedEntered: "Created+Entered",
    EntityOpUpdatedEntered: "Updated+Entered",
    EntityOpDeletedLeft: "Deleted+Left",
}

FieldPathTable = [FieldPathOp("PlusOne", 36271, PlusOne),
                  FieldPathOp("PlusTwo", 10334, PlusTwo),
                  FieldPathOp("PlusThree", 1375, PlusThree),
                  FieldPathOp("PlusFour", 646, PlusFour),
                  FieldPathOp("PlusN", 4128, PlusN),
                  FieldPathOp("PushOneLeftDeltaZeroRightZero", 35, PushOneLeftDeltaZeroRightZero),
                  FieldPathOp("PushOneLeftDeltaZeroRightNonZero", 3, PushOneLeftDeltaZeroRightNonZero),
                  FieldPathOp("PushOneLeftDeltaOneRightZero", 521, PushOneLeftDeltaOneRightZero),
                  FieldPathOp("PushOneLeftDeltaOneRightNonZero", 2942, PushOneLeftDeltaOneRightNonZero),
                  FieldPathOp("PushOneLeftDeltaNRightZero", 560, PushOneLeftDeltaNRightZero),
                  FieldPathOp("PushOneLeftDeltaNRightNonZero", 471, PushOneLeftDeltaNRightNonZero),
                  FieldPathOp("PushOneLeftDeltaNRightNonZeroPack6Bits", 10530, PushOneLeftDeltaNRightNonZeroPack6Bits),
                  FieldPathOp("PushOneLeftDeltaNRightNonZeroPack8Bits", 251, PushOneLeftDeltaNRightNonZeroPack8Bits),
                  FieldPathOp("PushTwoLeftDeltaZero", 0, PushTwoLeftDeltaZero),
                  FieldPathOp("PushTwoPack5LeftDeltaZero", 0, PushTwoPack5LeftDeltaZero),
                  FieldPathOp("PushThreeLeftDeltaZero", 0, PushThreeLeftDeltaZero),
                  FieldPathOp("PushThreePack5LeftDeltaZero", 0, PushThreePack5LeftDeltaZero),
                  FieldPathOp("PushTwoLeftDeltaOne", 0, PushTwoLeftDeltaOne),
                  FieldPathOp("PushTwoPack5LeftDeltaOne", 0, PushTwoPack5LeftDeltaOne),
                  FieldPathOp("PushThreeLeftDeltaOne", 0, PushThreeLeftDeltaOne),
                  FieldPathOp("PushThreePack5LeftDeltaOne", 0, PushThreePack5LeftDeltaOne),
                  FieldPathOp("PushTwoLeftDeltaN", 0, PushTwoLeftDeltaN),
                  FieldPathOp("PushTwoPack5LeftDeltaN", 0, PushTwoPack5LeftDeltaN),
                  FieldPathOp("PushThreeLeftDeltaN", 0, PushThreeLeftDeltaN),
                  FieldPathOp("PushThreePack5LeftDeltaN", 0, PushThreePack5LeftDeltaN),
                  FieldPathOp("PushN", 0, PushN),
                  FieldPathOp("PushNAndNonTopological", 310, PushNAndNonTopological),
                  FieldPathOp("PopOnePlusOne", 2, PopOnePlusOne),
                  FieldPathOp("PopOnePlusN", 0, PopOnePlusN),
                  FieldPathOp("PopAllButOnePlusOne", 1837, PopAllButOnePlusOne),
                  FieldPathOp("PopAllButOnePlusN", 149, PopAllButOnePlusN),
                  FieldPathOp("PopAllButOnePlusNPack3Bits", 300, PopAllButOnePlusNPack3Bits),
                  FieldPathOp("PopAllButOnePlusNPack6Bits", 634, PopAllButOnePlusNPack6Bits),
                  FieldPathOp("PopNPlusOne", 0, PopNPlusOne),
                  FieldPathOp("PopNPlusN", 0, PopNPlusN),
                  FieldPathOp("PopNAndNonTopographical", 1, PopNAndNonTopographical),
                  FieldPathOp("NonTopoComplex", 76, NonTopoComplex),
                  FieldPathOp("NonTopoPenultimatePlusOne", 271, NonTopoPenultimatePlusOne),
                  FieldPathOp("NonTopoComplexPack4Bits", 99, NonTopoComplexPack4Bits),
                  FieldPathOp("FieldPathEncodeFinish", 25474, FieldPathEncodeFinish)
                  ]


def Heapify(arr, n, i):
    largest = i  # Initialize largest as root
    l = 2 * i + 1  # left = 2*i + 1
    r = 2 * i + 2  # right = 2*i + 2

    # See if left child of root exists and is
    # greater than root
    if l < n and arr[i].weight == arr[l].weight:
        if arr[i].value >= arr[l].value:
            largest = l
    elif l < n and arr[i].weight < arr[l].weight:
        largest = l

    # See if right child of root exists and is
    # greater than root
    if r < n and arr[largest].weight == arr[r].weight:
        if arr[largest].value >= arr[r].value:
            largest = r
    elif r < n and arr[largest].weight < arr[r].weight:
        largest = r

    # Change root, if needed
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # swap

        # Heapify the root.
        Heapify(arr, n, largest)


# The main function to sort an array of given size
def HeapSort(arr):
    n = len(arr)

    # Build a maxheap.
    # Since last parent will be at ((n//2)-1) we can start at that location.
    for i in range(n // 2 - 1, -1, -1):
        Heapify(arr, n, i)

    # One by one extract elements
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # swap
        Heapify(arr, i, 0)


def ReadFieldPaths(r):
    trees = []
    for i, field_path_op in enumerate(FieldPathTable):
        if field_path_op.weight == 0:
            leaf = HuffmanLeaf(1, i)
        else:
            leaf = HuffmanLeaf(field_path_op.weight, i)

        trees.append(leaf)

    HeapSort(trees)
    n = len(trees)
    for i in range(0, n - 1):
        a = trees.pop(0)
        b = trees.pop(0)
        new_tree = HuffmanNode(a.weight + b.weight, i + 40, a, b)

        trees.append(new_tree)
        HeapSort(trees)

    fp = FieldPath()

    paths = []
    node_tree, next_tree = trees[0], trees[0]
    while not fp.done:
        flag = r.read_bits(1)
        if flag == 1:
            next_tree = node_tree.right
        else:
            next_tree = node_tree.left

        if type(next_tree) == type(HuffmanLeaf(0, 0)):
            node_tree = trees[0]
            next_value = next_tree.value

            # print("next_value: ", next_value)
            FieldPathTable[next_value].fn(r, fp)
            # print("fp.path: ", fp.path)
            if not fp.done:
                paths.append(copy.deepcopy(fp))
        else:
            node_tree = next_tree

    return paths


def GetDecoderForFieldPathFromSerializer(s, fp, pos):
    index = fp.path[pos]
    field = s.fields[index]
    decoder, f = GetDecoderForFieldPathFromField(field, fp, pos + 1)

    return decoder, f


def GetDecoderForFieldPathFromField(f, fp, pos):
    if f.model == FieldModelEnum.fieldModelFixedArray.value:
        decoder = f.decoder

        return decoder, f
    elif f.model == FieldModelEnum.fieldModelFixedTable.value:
        if fp.last == pos - 1:
            decoder = f.base_decoder

            return decoder, f
        else:
            decoder, f = GetDecoderForFieldPathFromSerializer(f.serializer, fp, pos)

            return decoder, f

    elif f.model == FieldModelEnum.fieldModelVariableArray.value:
        if fp.last == pos:
            decoder = f.child_decoder
        else:
            decoder = f.base_decoder

        return decoder, f
    elif f.model == FieldModelEnum.fieldModelVariableTable.value:
        if fp.last >= pos + 1:
            decoder, f = GetDecoderForFieldPathFromSerializer(f.serializer, fp, pos + 1)
            return decoder, f
        else:
            decoder = f.base_decoder

            return decoder, f
    else:
        decoder = f.decoder

        return decoder, f


def ReadFields(r, s, state):
    paths = ReadFieldPaths(r)
    path_list = [path.path for path in paths]
    for path in paths:
        decoder, field = GetDecoderForFieldPathFromSerializer(s, path, 0)
        val = None
        if decoder == "signedDecoder":
            n = r.bit_count
            val = r.read_var_int32()
        elif decoder == "noscaleDecoder":
            val = r.read_bits(32)
            val = int(bin(val), 2)
            val = struct.unpack('f', struct.pack('I', val))[0]
            val = round(val, 1)
        elif decoder == "unsignedDecoder":
            val = r.read_var_uint32()
        elif decoder == "booleanDecoder":
            val = r.read_boolean()
        elif decoder == "floatCoordDecoder_3":
            val = [None, None, None]
            for i in range(3):
                val[i] = r.read_coord()

        elif decoder == "QuantizedFloatDecoder":
            qfd = QuantizedFloatDecoder(field.bit_count, field.encode_flags,
                                        field.low_value, field.high_value)
            val = qfd.decode(r)
            val = round(val, 5)
        elif decoder == "defaultDecoder":
            val = r.read_var_uint32()
        elif decoder == "stringDecoder":
            val = r.read_string()
        elif decoder == "noscaleDecoder_3":
            val = [None, None, None]
            for i in range(3):
                value = r.read_bits(32)
                value = int(bin(value), 2)
                value = struct.unpack('f', struct.pack('I', value))[0]
                value = round(value, 1)
                val[i] = value

        elif decoder == "unsigned64Decoder":
            val = r.read_var_uint64()
        elif decoder == "simulationTimeDecoder":
            val = np.float32(r.read_var_uint32()) * (1.0 / 30)
        elif decoder == "floatCoordDecoder":
            val = r.read_coord()
        elif decoder == "QAngle_1":
            val = [0, 0, 0]
            n = field.bit_count

            val[0] = r.read_angle(n)
            val[1] = r.read_angle(n)
            val[2] = 0.0
        elif decoder == "QAngle_3":
            val = [0, 0, 0]

            rX = r.read_boolean()
            rY = r.read_boolean()
            rZ = r.read_boolean()
            if rX:
                val[0] = r.read_coord()

            if rY:
                val[1] = r.read_coord()

            if rZ:
                val[2] = r.read_coord()
        elif decoder == "vectorNormalDecoder":
            val = r.read_3bit_normal()
        elif decoder == "fixed64Decoder":
            val = r.read_le_uint64()

        # if val == 64576.31158:
        # if decoder == "QuantizedFloatDecoder":
        # print("decoder: ", decoder)
        # print("val: ", val)
        # print("")

        SetFieldState(state, path, val)
