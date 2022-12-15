class Game:
    def __init__(self):
        self.header = {"demo_file_stamp": None,
                       "network_protocol": None,
                       "server_name": None,
                       'client_name': None,
                       'map_name': None,
                       'game_directory': None,
                       'fullpackets_version': None,
                       'allow_clientside_entities': None,
                       'allow_clientside_particles': None,
                       'addons': None,
                       'demo_version_name': None,
                       'demo_version_guid': None,
                       'build_num': None}
        self.server_info = {}
