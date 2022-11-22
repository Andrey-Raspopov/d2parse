import messages
from proto import netmessages_pb2


def parse_game_event_list_message(message):
    pb_message = netmessages_pb2.CSVCMsg_GameEventList()
    pb_message.ParseFromString(message)


def parse_service_message4(cmd, message):
    pb_message = messages.USER_MESSAGE_TYPES[cmd]()
    pb_message.ParseFromString(message)


def fill_basic_entity_info(
    target_entity_info, entity_type, location_type_x, location_type_y
):
    target_name = target_entity_info[entity_type]
    target_pos = [
        target_entity_info[location_type_x],
        target_entity_info[location_type_y],
    ]
    target_team = target_entity_info["m_iTeamNum"]
    return target_pos




