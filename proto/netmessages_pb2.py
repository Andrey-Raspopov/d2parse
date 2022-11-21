# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: netmessages.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import networkbasetypes_pb2 as networkbasetypes__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11netmessages.proto\x1a\x16networkbasetypes.proto\"}\n\x12\x43\x43LCMsg_ClientInfo\x12\x16\n\x0esend_table_crc\x18\x01 \x01(\x07\x12\x14\n\x0cserver_count\x18\x02 \x01(\r\x12\x0f\n\x07is_hltv\x18\x03 \x01(\x08\x12\x12\n\nfriends_id\x18\x05 \x01(\r\x12\x14\n\x0c\x66riends_name\x18\x06 \x01(\t\"J\n\x0c\x43\x43LCMsg_Move\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\x12\x16\n\x0e\x63ommand_number\x18\x04 \x01(\r\x12\x14\n\x0cnum_commands\x18\x05 \x01(\r\"\xc9\x01\n\x0e\x43MsgVoiceAudio\x12:\n\x06\x66ormat\x18\x01 \x01(\x0e\x32\x12.VoiceDataFormat_t:\x16VOICEDATA_FORMAT_STEAM\x12\x12\n\nvoice_data\x18\x02 \x01(\x0c\x12\x16\n\x0esequence_bytes\x18\x03 \x01(\x05\x12\x16\n\x0esection_number\x18\x04 \x01(\r\x12\x13\n\x0bsample_rate\x18\x05 \x01(\r\x12\"\n\x1auncompressed_sample_offset\x18\x06 \x01(\r\"O\n\x11\x43\x43LCMsg_VoiceData\x12\x1e\n\x05\x61udio\x18\x01 \x01(\x0b\x32\x0f.CMsgVoiceAudio\x12\x0c\n\x04xuid\x18\x02 \x01(\x06\x12\x0c\n\x04tick\x18\x03 \x01(\r\"A\n\x13\x43\x43LCMsg_BaselineAck\x12\x15\n\rbaseline_tick\x18\x01 \x01(\x05\x12\x13\n\x0b\x62\x61seline_nr\x18\x02 \x01(\x05\"*\n\x14\x43\x43LCMsg_ListenEvents\x12\x12\n\nevent_mask\x18\x01 \x03(\x07\"\\\n\x18\x43\x43LCMsg_RespondCvarValue\x12\x0e\n\x06\x63ookie\x18\x01 \x01(\x05\x12\x13\n\x0bstatus_code\x18\x02 \x01(\x05\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\r\n\x05value\x18\x04 \x01(\t\"m\n\x14\x43\x43LCMsg_FileCRCCheck\x12\x11\n\tcode_path\x18\x01 \x01(\x05\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x15\n\rcode_filename\x18\x03 \x01(\x05\x12\x10\n\x08\x66ilename\x18\x04 \x01(\t\x12\x0b\n\x03\x63rc\x18\x05 \x01(\x07\"+\n\x17\x43\x43LCMsg_LoadingProgress\x12\x10\n\x08progress\x18\x01 \x01(\x05\"0\n\x1a\x43\x43LCMsg_SplitPlayerConnect\x12\x12\n\nplayername\x18\x01 \x01(\t\"7\n\x15\x43\x43LCMsg_ClientMessage\x12\x10\n\x08msg_type\x18\x01 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\"-\n\x1d\x43\x43LCMsg_SplitPlayerDisconnect\x12\x0c\n\x04slot\x18\x01 \x01(\x05\"*\n\x14\x43\x43LCMsg_ServerStatus\x12\x12\n\nsimplified\x18\x01 \x01(\x08\"\x14\n\x12\x43\x43LCMsg_ServerPing\"Z\n\x14\x43\x43LCMsg_RequestPause\x12-\n\npause_type\x18\x01 \x01(\x0e\x32\x0f.RequestPause_t:\x08RP_PAUSE\x12\x13\n\x0bpause_group\x18\x02 \x01(\x05\"$\n\x14\x43\x43LCMsg_CmdKeyValues\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"*\n\x19\x43\x43LCMsg_RconServerDetails\x12\r\n\x05token\x18\x01 \x01(\x0c\"\x83\x03\n\x12\x43SVCMsg_ServerInfo\x12\x10\n\x08protocol\x18\x01 \x01(\x05\x12\x14\n\x0cserver_count\x18\x02 \x01(\x05\x12\x14\n\x0cis_dedicated\x18\x03 \x01(\x08\x12\x0f\n\x07is_hltv\x18\x04 \x01(\x08\x12\x0c\n\x04\x63_os\x18\x06 \x01(\x05\x12\x13\n\x0bmax_clients\x18\n \x01(\x05\x12\x13\n\x0bmax_classes\x18\x0b \x01(\x05\x12\x13\n\x0bplayer_slot\x18\x0c \x01(\x05\x12\x15\n\rtick_interval\x18\r \x01(\x02\x12\x10\n\x08game_dir\x18\x0e \x01(\t\x12\x10\n\x08map_name\x18\x0f \x01(\t\x12\x10\n\x08sky_name\x18\x10 \x01(\t\x12\x11\n\thost_name\x18\x11 \x01(\t\x12\x12\n\naddon_name\x18\x12 \x01(\t\x12>\n\x13game_session_config\x18\x13 \x01(\x0b\x32!.CSVCMsg_GameSessionConfiguration\x12\x1d\n\x15game_session_manifest\x18\x14 \x01(\x0c\"\xa4\x01\n\x11\x43SVCMsg_ClassInfo\x12\x18\n\x10\x63reate_on_client\x18\x01 \x01(\x08\x12+\n\x07\x63lasses\x18\x02 \x03(\x0b\x32\x1a.CSVCMsg_ClassInfo.class_t\x1aH\n\x07\x63lass_t\x12\x10\n\x08\x63lass_id\x18\x01 \x01(\x05\x12\x17\n\x0f\x64\x61ta_table_name\x18\x02 \x01(\t\x12\x12\n\nclass_name\x18\x03 \x01(\t\"\"\n\x10\x43SVCMsg_SetPause\x12\x0e\n\x06paused\x18\x01 \x01(\x08\"G\n\x11\x43SVCMsg_VoiceInit\x12\x0f\n\x07quality\x18\x01 \x01(\x05\x12\r\n\x05\x63odec\x18\x02 \x01(\t\x12\x12\n\x07version\x18\x03 \x01(\x05:\x01\x30\"\x1d\n\rCSVCMsg_Print\x12\x0c\n\x04text\x18\x01 \x01(\t\"\xdf\x03\n\x0e\x43SVCMsg_Sounds\x12\x16\n\x0ereliable_sound\x18\x01 \x01(\x08\x12+\n\x06sounds\x18\x02 \x03(\x0b\x32\x1b.CSVCMsg_Sounds.sounddata_t\x1a\x87\x03\n\x0bsounddata_t\x12\x10\n\x08origin_x\x18\x01 \x01(\x11\x12\x10\n\x08origin_y\x18\x02 \x01(\x11\x12\x10\n\x08origin_z\x18\x03 \x01(\x11\x12\x0e\n\x06volume\x18\x04 \x01(\r\x12\x13\n\x0b\x64\x65lay_value\x18\x05 \x01(\x02\x12\x17\n\x0fsequence_number\x18\x06 \x01(\x05\x12\x14\n\x0c\x65ntity_index\x18\x07 \x01(\x05\x12\x0f\n\x07\x63hannel\x18\x08 \x01(\x05\x12\r\n\x05pitch\x18\t \x01(\x05\x12\r\n\x05\x66lags\x18\n \x01(\x05\x12\x11\n\tsound_num\x18\x0b \x01(\r\x12\x18\n\x10sound_num_handle\x18\x0c \x01(\x07\x12\x16\n\x0espeaker_entity\x18\r \x01(\x05\x12\x13\n\x0brandom_seed\x18\x0e \x01(\x05\x12\x13\n\x0bsound_level\x18\x0f \x01(\x05\x12\x13\n\x0bis_sentence\x18\x10 \x01(\x08\x12\x12\n\nis_ambient\x18\x11 \x01(\x08\x12\x0c\n\x04guid\x18\x12 \x01(\r\x12\x19\n\x11sound_resource_id\x18\x13 \x01(\x06\"X\n\x10\x43SVCMsg_Prefetch\x12\x13\n\x0bsound_index\x18\x01 \x01(\x05\x12/\n\rresource_type\x18\x02 \x01(\x0e\x32\r.PrefetchType:\tPFT_SOUND\"5\n\x0f\x43SVCMsg_SetView\x12\x14\n\x0c\x65ntity_index\x18\x01 \x01(\x05\x12\x0c\n\x04slot\x18\x02 \x01(\x05\"@\n\x10\x43SVCMsg_FixAngle\x12\x10\n\x08relative\x18\x01 \x01(\x08\x12\x1a\n\x05\x61ngle\x18\x02 \x01(\x0b\x32\x0b.CMsgQAngle\"4\n\x16\x43SVCMsg_CrosshairAngle\x12\x1a\n\x05\x61ngle\x18\x01 \x01(\x0b\x32\x0b.CMsgQAngle\"\x8a\x01\n\x10\x43SVCMsg_BSPDecal\x12\x18\n\x03pos\x18\x01 \x01(\x0b\x32\x0b.CMsgVector\x12\x1b\n\x13\x64\x65\x63\x61l_texture_index\x18\x02 \x01(\x05\x12\x14\n\x0c\x65ntity_index\x18\x03 \x01(\x05\x12\x13\n\x0bmodel_index\x18\x04 \x01(\x05\x12\x14\n\x0clow_priority\x18\x05 \x01(\x08\"z\n\x13\x43SVCMsg_SplitScreen\x12?\n\x04type\x18\x01 \x01(\x0e\x32\x18.ESplitScreenMessageType:\x17MSG_SPLITSCREEN_ADDUSER\x12\x0c\n\x04slot\x18\x02 \x01(\x05\x12\x14\n\x0cplayer_index\x18\x03 \x01(\x05\"9\n\x14\x43SVCMsg_GetCvarValue\x12\x0e\n\x06\x63ookie\x18\x01 \x01(\x05\x12\x11\n\tcvar_name\x18\x02 \x01(\t\"<\n\x0c\x43SVCMsg_Menu\x12\x13\n\x0b\x64ialog_type\x18\x01 \x01(\x05\x12\x17\n\x0fmenu_key_values\x18\x02 \x01(\x0c\"N\n\x13\x43SVCMsg_UserMessage\x12\x10\n\x08msg_type\x18\x01 \x01(\x05\x12\x10\n\x08msg_data\x18\x02 \x01(\x0c\x12\x13\n\x0bpassthrough\x18\x03 \x01(\x05\"\xb0\x02\n\x11\x43SVCMsg_SendTable\x12\x0e\n\x06is_end\x18\x01 \x01(\x08\x12\x16\n\x0enet_table_name\x18\x02 \x01(\t\x12\x15\n\rneeds_decoder\x18\x03 \x01(\x08\x12,\n\x05props\x18\x04 \x03(\x0b\x32\x1d.CSVCMsg_SendTable.sendprop_t\x1a\xad\x01\n\nsendprop_t\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x10\n\x08var_name\x18\x02 \x01(\t\x12\r\n\x05\x66lags\x18\x03 \x01(\x05\x12\x10\n\x08priority\x18\x04 \x01(\x05\x12\x0f\n\x07\x64t_name\x18\x05 \x01(\t\x12\x14\n\x0cnum_elements\x18\x06 \x01(\x05\x12\x11\n\tlow_value\x18\x07 \x01(\x02\x12\x12\n\nhigh_value\x18\x08 \x01(\x02\x12\x10\n\x08num_bits\x18\t \x01(\x05\"\xd1\x01\n\x15\x43SVCMsg_GameEventList\x12\x38\n\x0b\x64\x65scriptors\x18\x01 \x03(\x0b\x32#.CSVCMsg_GameEventList.descriptor_t\x1a#\n\x05key_t\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x1aY\n\x0c\x64\x65scriptor_t\x12\x0f\n\x07\x65ventid\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12*\n\x04keys\x18\x03 \x03(\x0b\x32\x1c.CSVCMsg_GameEventList.key_t\"\xee\x05\n\x16\x43SVCMsg_PacketEntities\x12\x13\n\x0bmax_entries\x18\x01 \x01(\x05\x12\x17\n\x0fupdated_entries\x18\x02 \x01(\x05\x12\x10\n\x08is_delta\x18\x03 \x01(\x08\x12\x17\n\x0fupdate_baseline\x18\x04 \x01(\x08\x12\x10\n\x08\x62\x61seline\x18\x05 \x01(\x05\x12\x12\n\ndelta_from\x18\x06 \x01(\x05\x12\x13\n\x0b\x65ntity_data\x18\x07 \x01(\x0c\x12\x1a\n\x12pending_full_frame\x18\x08 \x01(\x08\x12 \n\x18\x61\x63tive_spawngroup_handle\x18\t \x01(\r\x12\'\n\x1fmax_spawngroup_creationsequence\x18\n \x01(\r\x12\x17\n\x0flast_cmd_number\x18\x0b \x01(\r\x12\x13\n\x0bserver_tick\x18\x0c \x01(\r\x12\x1b\n\x13serialized_entities\x18\r \x01(\x0c\x12H\n\x12\x63ommand_queue_info\x18\x0e \x01(\x0b\x32,.CSVCMsg_PacketEntities.command_queue_info_t\x12I\n\x13\x61lternate_baselines\x18\x0f \x03(\x0b\x32,.CSVCMsg_PacketEntities.alternate_baseline_t\x1a\xb2\x01\n\x14\x63ommand_queue_info_t\x12\x17\n\x0f\x63ommands_queued\x18\x01 \x01(\r\x12\"\n\x1a\x63ommand_queue_desired_size\x18\x02 \x01(\r\x12\x1d\n\x15starved_command_ticks\x18\x03 \x01(\r\x12\x1d\n\x15time_dilation_percent\x18\x04 \x01(\x02\x12\x1f\n\x17\x64iscarded_command_ticks\x18\x05 \x01(\r\x1a\x44\n\x14\x61lternate_baseline_t\x12\x14\n\x0c\x65ntity_index\x18\x01 \x01(\x05\x12\x16\n\x0e\x62\x61seline_index\x18\x02 \x01(\x05\"R\n\x14\x43SVCMsg_TempEntities\x12\x10\n\x08reliable\x18\x01 \x01(\x08\x12\x13\n\x0bnum_entries\x18\x02 \x01(\x05\x12\x13\n\x0b\x65ntity_data\x18\x03 \x01(\x0c\"\xe9\x01\n\x19\x43SVCMsg_CreateStringTable\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bnum_entries\x18\x02 \x01(\x05\x12\x1c\n\x14user_data_fixed_size\x18\x03 \x01(\x08\x12\x16\n\x0euser_data_size\x18\x04 \x01(\x05\x12\x1b\n\x13user_data_size_bits\x18\x05 \x01(\x05\x12\r\n\x05\x66lags\x18\x06 \x01(\x05\x12\x13\n\x0bstring_data\x18\x07 \x01(\x0c\x12\x19\n\x11uncompressed_size\x18\x08 \x01(\x05\x12\x17\n\x0f\x64\x61ta_compressed\x18\t \x01(\x08\"_\n\x19\x43SVCMsg_UpdateStringTable\x12\x10\n\x08table_id\x18\x01 \x01(\x05\x12\x1b\n\x13num_changed_entries\x18\x02 \x01(\x05\x12\x13\n\x0bstring_data\x18\x03 \x01(\x0c\"\x88\x01\n\x11\x43SVCMsg_VoiceData\x12\x1e\n\x05\x61udio\x18\x01 \x01(\x0b\x32\x0f.CMsgVoiceAudio\x12\x0e\n\x06\x63lient\x18\x02 \x01(\x05\x12\x11\n\tproximity\x18\x03 \x01(\x08\x12\x0c\n\x04xuid\x18\x04 \x01(\x06\x12\x14\n\x0c\x61udible_mask\x18\x05 \x01(\x05\x12\x0c\n\x04tick\x18\x06 \x01(\r\"K\n\x16\x43SVCMsg_PacketReliable\x12\x0c\n\x04tick\x18\x01 \x01(\x05\x12\x14\n\x0cmessagessize\x18\x02 \x01(\x05\x12\r\n\x05state\x18\x03 \x01(\x08\"T\n\x16\x43SVCMsg_FullFrameSplit\x12\x0c\n\x04tick\x18\x01 \x01(\x05\x12\x0f\n\x07section\x18\x02 \x01(\x05\x12\r\n\x05total\x18\x03 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\"U\n\x12\x43SVCMsg_HLTVStatus\x12\x0e\n\x06master\x18\x01 \x01(\t\x12\x0f\n\x07\x63lients\x18\x02 \x01(\x05\x12\r\n\x05slots\x18\x03 \x01(\x05\x12\x0f\n\x07proxies\x18\x04 \x01(\x05\")\n\x15\x43SVCMsg_ServerSteamID\x12\x10\n\x08steam_id\x18\x01 \x01(\x04\"$\n\x14\x43SVCMsg_CmdKeyValues\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\";\n\x19\x43SVCMsg_RconServerDetails\x12\r\n\x05token\x18\x01 \x01(\x0c\x12\x0f\n\x07\x64\x65tails\x18\x02 \x01(\t\";\n\x0e\x43MsgIPCAddress\x12\x15\n\rcomputer_guid\x18\x01 \x01(\x06\x12\x12\n\nprocess_id\x18\x02 \x01(\r\"\xa0\x01\n\x0e\x43MsgServerPeer\x12\x13\n\x0bplayer_slot\x18\x01 \x01(\x05\x12\x0f\n\x07steamid\x18\x02 \x01(\x06\x12\x1c\n\x03ipc\x18\x03 \x01(\x0b\x32\x0f.CMsgIPCAddress\x12\x15\n\rthey_hear_you\x18\x04 \x01(\x08\x12\x15\n\ryou_hear_them\x18\x05 \x01(\x08\x12\x1c\n\x14is_listenserver_host\x18\x06 \x01(\x08\"1\n\x10\x43SVCMsg_PeerList\x12\x1d\n\x04peer\x18\x01 \x03(\x0b\x32\x0f.CMsgServerPeer\"/\n\x1c\x43SVCMsg_ClearAllStringTables\x12\x0f\n\x07mapname\x18\x01 \x01(\t\"\x92\x02\n\x1fProtoFlattenedSerializerField_t\x12\x14\n\x0cvar_type_sym\x18\x01 \x01(\x05\x12\x14\n\x0cvar_name_sym\x18\x02 \x01(\x05\x12\x11\n\tbit_count\x18\x03 \x01(\x05\x12\x11\n\tlow_value\x18\x04 \x01(\x02\x12\x12\n\nhigh_value\x18\x05 \x01(\x02\x12\x14\n\x0c\x65ncode_flags\x18\x06 \x01(\x05\x12!\n\x19\x66ield_serializer_name_sym\x18\x07 \x01(\x05\x12 \n\x18\x66ield_serializer_version\x18\x08 \x01(\x05\x12\x15\n\rsend_node_sym\x18\t \x01(\x05\x12\x17\n\x0fvar_encoder_sym\x18\n \x01(\x05\"k\n\x1aProtoFlattenedSerializer_t\x12\x1b\n\x13serializer_name_sym\x18\x01 \x01(\x05\x12\x1a\n\x12serializer_version\x18\x02 \x01(\x05\x12\x14\n\x0c\x66ields_index\x18\x03 \x03(\x05\"\x92\x01\n\x1b\x43SVCMsg_FlattenedSerializer\x12\x30\n\x0bserializers\x18\x01 \x03(\x0b\x32\x1b.ProtoFlattenedSerializer_t\x12\x0f\n\x07symbols\x18\x02 \x03(\t\x12\x30\n\x06\x66ields\x18\x03 \x03(\x0b\x32 .ProtoFlattenedSerializerField_t\"!\n\x11\x43SVCMsg_StopSound\x12\x0c\n\x04guid\x18\x01 \x01(\x07\"y\n\x1e\x43\x42idirMsg_RebroadcastGameEvent\x12\x14\n\x0cposttoserver\x18\x01 \x01(\x08\x12\x0f\n\x07\x62uftype\x18\x02 \x01(\x05\x12\x16\n\x0e\x63lientbitcount\x18\x03 \x01(\r\x12\x18\n\x10receivingclients\x18\x04 \x01(\x04\"2\n\x1b\x43\x42idirMsg_RebroadcastSource\x12\x13\n\x0b\x65ventsource\x18\x01 \x01(\x05\"\x9b\x06\n\x16\x43MsgServerNetworkStats\x12\x11\n\tdedicated\x18\x01 \x01(\x08\x12\x11\n\tcpu_usage\x18\x02 \x01(\x05\x12\x16\n\x0ememory_used_mb\x18\x03 \x01(\x05\x12\x16\n\x0ememory_free_mb\x18\x04 \x01(\x05\x12\x0e\n\x06uptime\x18\x05 \x01(\x05\x12\x13\n\x0bspawn_count\x18\x06 \x01(\x05\x12\x13\n\x0bnum_clients\x18\x08 \x01(\x05\x12\x10\n\x08num_bots\x18\t \x01(\x05\x12\x16\n\x0enum_spectators\x18\n \x01(\x05\x12\x15\n\rnum_tv_relays\x18\x0b \x01(\x05\x12\x0b\n\x03\x66ps\x18\x0c \x01(\x02\x12+\n\x05ports\x18\x11 \x03(\x0b\x32\x1c.CMsgServerNetworkStats.Port\x12\x17\n\x0f\x61vg_latency_out\x18\x12 \x01(\x02\x12\x16\n\x0e\x61vg_latency_in\x18\x13 \x01(\x02\x12\x17\n\x0f\x61vg_packets_out\x18\x14 \x01(\x02\x12\x16\n\x0e\x61vg_packets_in\x18\x15 \x01(\x02\x12\x14\n\x0c\x61vg_loss_out\x18\x16 \x01(\x02\x12\x13\n\x0b\x61vg_loss_in\x18\x17 \x01(\x02\x12\x14\n\x0c\x61vg_data_out\x18\x18 \x01(\x02\x12\x13\n\x0b\x61vg_data_in\x18\x19 \x01(\x02\x12\x15\n\rtotal_data_in\x18\x1a \x01(\x04\x12\x18\n\x10total_packets_in\x18\x1b \x01(\x04\x12\x16\n\x0etotal_data_out\x18\x1c \x01(\x04\x12\x19\n\x11total_packets_out\x18\x1d \x01(\x04\x12/\n\x07players\x18\x1e \x03(\x0b\x32\x1e.CMsgServerNetworkStats.Player\x1a\"\n\x04Port\x12\x0c\n\x04port\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x1a\x84\x01\n\x06Player\x12\x0f\n\x07steamid\x18\x01 \x01(\x04\x12\x13\n\x0bremote_addr\x18\x02 \x01(\t\x12\x16\n\x0eping_stddev_ms\x18\x03 \x01(\x05\x12\x13\n\x0bping_avg_ms\x18\x04 \x01(\x05\x12\x17\n\x0fpacket_loss_pct\x18\x05 \x01(\x02\x12\x0e\n\x06is_bot\x18\x06 \x01(\x08\"\xd6\x01\n\x12\x43SVCMsg_HltvReplay\x12\r\n\x05\x64\x65lay\x18\x01 \x01(\x05\x12\x16\n\x0eprimary_target\x18\x02 \x01(\x05\x12\x16\n\x0ereplay_stop_at\x18\x03 \x01(\x05\x12\x17\n\x0freplay_start_at\x18\x04 \x01(\x05\x12\x1d\n\x15replay_slowdown_begin\x18\x05 \x01(\x05\x12\x1b\n\x13replay_slowdown_end\x18\x06 \x01(\x05\x12\x1c\n\x14replay_slowdown_rate\x18\x07 \x01(\x02\x12\x0e\n\x06reason\x18\x08 \x01(\x05\"\x81\x01\n\x12\x43\x43LCMsg_HltvReplay\x12\x0f\n\x07request\x18\x01 \x01(\x05\x12\x17\n\x0fslowdown_length\x18\x02 \x01(\x02\x12\x15\n\rslowdown_rate\x18\x03 \x01(\x02\x12\x16\n\x0eprimary_target\x18\x04 \x01(\x05\x12\x12\n\nevent_time\x18\x05 \x01(\x02\"(\n\x19\x43SVCMsg_Broadcast_Command\x12\x0b\n\x03\x63md\x18\x01 \x01(\t\"\xef\x01\n\x1d\x43\x43LCMsg_HltvFixupOperatorTick\x12\x0c\n\x04tick\x18\x01 \x01(\x05\x12\x12\n\nprops_data\x18\x02 \x01(\x0c\x12\x1b\n\x06origin\x18\x03 \x01(\x0b\x32\x0b.CMsgVector\x12\x1f\n\neye_angles\x18\x04 \x01(\x0b\x32\x0b.CMsgQAngle\x12\x15\n\robserver_mode\x18\x05 \x01(\x05\x12\x1c\n\x14\x63\x61meraman_scoreboard\x18\x06 \x01(\x08\x12\x17\n\x0fobserver_target\x18\x07 \x01(\x05\x12 \n\x0bview_offset\x18\x08 \x01(\x0b\x32\x0b.CMsgVector\"O\n\x1f\x43SVCMsg_HltvFixupOperatorStatus\x12\x0c\n\x04mode\x18\x01 \x01(\r\x12\x1e\n\x16override_operator_name\x18\x02 \x01(\t*\x8e\x03\n\x0c\x43LC_Messages\x12\x12\n\x0e\x63lc_ClientInfo\x10\x14\x12\x0c\n\x08\x63lc_Move\x10\x15\x12\x11\n\rclc_VoiceData\x10\x16\x12\x13\n\x0f\x63lc_BaselineAck\x10\x17\x12\x14\n\x10\x63lc_ListenEvents\x10\x18\x12\x18\n\x14\x63lc_RespondCvarValue\x10\x19\x12\x14\n\x10\x63lc_FileCRCCheck\x10\x1a\x12\x17\n\x13\x63lc_LoadingProgress\x10\x1b\x12\x1a\n\x16\x63lc_SplitPlayerConnect\x10\x1c\x12\x15\n\x11\x63lc_ClientMessage\x10\x1d\x12\x1d\n\x19\x63lc_SplitPlayerDisconnect\x10\x1e\x12\x14\n\x10\x63lc_ServerStatus\x10\x1f\x12\x12\n\x0e\x63lc_ServerPing\x10 \x12\x14\n\x10\x63lc_RequestPause\x10!\x12\x14\n\x10\x63lc_CmdKeyValues\x10\"\x12\x19\n\x15\x63lc_RconServerDetails\x10#\x12\x12\n\x0e\x63lc_HltvReplay\x10$*\x99\x05\n\x0cSVC_Messages\x12\x12\n\x0esvc_ServerInfo\x10(\x12\x1b\n\x17svc_FlattenedSerializer\x10)\x12\x11\n\rsvc_ClassInfo\x10*\x12\x10\n\x0csvc_SetPause\x10+\x12\x19\n\x15svc_CreateStringTable\x10,\x12\x19\n\x15svc_UpdateStringTable\x10-\x12\x11\n\rsvc_VoiceInit\x10.\x12\x11\n\rsvc_VoiceData\x10/\x12\r\n\tsvc_Print\x10\x30\x12\x0e\n\nsvc_Sounds\x10\x31\x12\x0f\n\x0bsvc_SetView\x10\x32\x12\x1c\n\x18svc_ClearAllStringTables\x10\x33\x12\x14\n\x10svc_CmdKeyValues\x10\x34\x12\x10\n\x0csvc_BSPDecal\x10\x35\x12\x13\n\x0fsvc_SplitScreen\x10\x36\x12\x16\n\x12svc_PacketEntities\x10\x37\x12\x10\n\x0csvc_Prefetch\x10\x38\x12\x0c\n\x08svc_Menu\x10\x39\x12\x14\n\x10svc_GetCvarValue\x10:\x12\x11\n\rsvc_StopSound\x10;\x12\x10\n\x0csvc_PeerList\x10<\x12\x16\n\x12svc_PacketReliable\x10=\x12\x12\n\x0esvc_HLTVStatus\x10>\x12\x15\n\x11svc_ServerSteamID\x10?\x12\x16\n\x12svc_FullFrameSplit\x10\x46\x12\x19\n\x15svc_RconServerDetails\x10G\x12\x13\n\x0fsvc_UserMessage\x10H\x12\x12\n\x0esvc_HltvReplay\x10I\x12\x19\n\x15svc_Broadcast_Command\x10J\x12\x1f\n\x1bsvc_HltvFixupOperatorStatus\x10K*L\n\x11VoiceDataFormat_t\x12\x1a\n\x16VOICEDATA_FORMAT_STEAM\x10\x00\x12\x1b\n\x17VOICEDATA_FORMAT_ENGINE\x10\x01*B\n\x0eRequestPause_t\x12\x0c\n\x08RP_PAUSE\x10\x00\x12\x0e\n\nRP_UNPAUSE\x10\x01\x12\x12\n\x0eRP_TOGGLEPAUSE\x10\x02*\x1d\n\x0cPrefetchType\x12\r\n\tPFT_SOUND\x10\x00*V\n\x17\x45SplitScreenMessageType\x12\x1b\n\x17MSG_SPLITSCREEN_ADDUSER\x10\x00\x12\x1e\n\x1aMSG_SPLITSCREEN_REMOVEUSER\x10\x01*\xb3\x01\n\x15\x45QueryCvarValueStatus\x12%\n!eQueryCvarValueStatus_ValueIntact\x10\x00\x12&\n\"eQueryCvarValueStatus_CvarNotFound\x10\x01\x12\"\n\x1e\x65QueryCvarValueStatus_NotACvar\x10\x02\x12\'\n#eQueryCvarValueStatus_CvarProtected\x10\x03*h\n\x0b\x44IALOG_TYPE\x12\x0e\n\nDIALOG_MSG\x10\x00\x12\x0f\n\x0b\x44IALOG_MENU\x10\x01\x12\x0f\n\x0b\x44IALOG_TEXT\x10\x02\x12\x10\n\x0c\x44IALOG_ENTRY\x10\x03\x12\x15\n\x11\x44IALOG_ASKCONNECT\x10\x04*+\n\x19SVC_Messages_LowFrequency\x12\x0e\n\tsvc_dummy\x10\xd8\x04*a\n\x16\x42idirectional_Messages\x12\x1b\n\x17\x62i_RebroadcastGameEvent\x10\x10\x12\x18\n\x14\x62i_RebroadcastSource\x10\x11\x12\x10\n\x0c\x62i_GameEvent\x10\x12*M\n#Bidirectional_Messages_LowFrequency\x12\x11\n\x0c\x62i_RelayInfo\x10\xbc\x05\x12\x13\n\x0e\x62i_RelayPacket\x10\xbd\x05*\xa1\x01\n\x11ReplayEventType_t\x12\x17\n\x13REPLAY_EVENT_CANCEL\x10\x00\x12\x16\n\x12REPLAY_EVENT_DEATH\x10\x01\x12\x18\n\x14REPLAY_EVENT_GENERIC\x10\x02\x12\'\n#REPLAY_EVENT_STUCK_NEED_FULL_UPDATE\x10\x03\x12\x18\n\x14REPLAY_EVENT_VICTORY\x10\x04\x42\x03\x80\x01\x00')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'netmessages_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\200\001\000'
  _CLC_MESSAGES._serialized_start=8000
  _CLC_MESSAGES._serialized_end=8398
  _SVC_MESSAGES._serialized_start=8401
  _SVC_MESSAGES._serialized_end=9066
  _VOICEDATAFORMAT_T._serialized_start=9068
  _VOICEDATAFORMAT_T._serialized_end=9144
  _REQUESTPAUSE_T._serialized_start=9146
  _REQUESTPAUSE_T._serialized_end=9212
  _PREFETCHTYPE._serialized_start=9214
  _PREFETCHTYPE._serialized_end=9243
  _ESPLITSCREENMESSAGETYPE._serialized_start=9245
  _ESPLITSCREENMESSAGETYPE._serialized_end=9331
  _EQUERYCVARVALUESTATUS._serialized_start=9334
  _EQUERYCVARVALUESTATUS._serialized_end=9513
  _DIALOG_TYPE._serialized_start=9515
  _DIALOG_TYPE._serialized_end=9619
  _SVC_MESSAGES_LOWFREQUENCY._serialized_start=9621
  _SVC_MESSAGES_LOWFREQUENCY._serialized_end=9664
  _BIDIRECTIONAL_MESSAGES._serialized_start=9666
  _BIDIRECTIONAL_MESSAGES._serialized_end=9763
  _BIDIRECTIONAL_MESSAGES_LOWFREQUENCY._serialized_start=9765
  _BIDIRECTIONAL_MESSAGES_LOWFREQUENCY._serialized_end=9842
  _REPLAYEVENTTYPE_T._serialized_start=9845
  _REPLAYEVENTTYPE_T._serialized_end=10006
  _CCLCMSG_CLIENTINFO._serialized_start=45
  _CCLCMSG_CLIENTINFO._serialized_end=170
  _CCLCMSG_MOVE._serialized_start=172
  _CCLCMSG_MOVE._serialized_end=246
  _CMSGVOICEAUDIO._serialized_start=249
  _CMSGVOICEAUDIO._serialized_end=450
  _CCLCMSG_VOICEDATA._serialized_start=452
  _CCLCMSG_VOICEDATA._serialized_end=531
  _CCLCMSG_BASELINEACK._serialized_start=533
  _CCLCMSG_BASELINEACK._serialized_end=598
  _CCLCMSG_LISTENEVENTS._serialized_start=600
  _CCLCMSG_LISTENEVENTS._serialized_end=642
  _CCLCMSG_RESPONDCVARVALUE._serialized_start=644
  _CCLCMSG_RESPONDCVARVALUE._serialized_end=736
  _CCLCMSG_FILECRCCHECK._serialized_start=738
  _CCLCMSG_FILECRCCHECK._serialized_end=847
  _CCLCMSG_LOADINGPROGRESS._serialized_start=849
  _CCLCMSG_LOADINGPROGRESS._serialized_end=892
  _CCLCMSG_SPLITPLAYERCONNECT._serialized_start=894
  _CCLCMSG_SPLITPLAYERCONNECT._serialized_end=942
  _CCLCMSG_CLIENTMESSAGE._serialized_start=944
  _CCLCMSG_CLIENTMESSAGE._serialized_end=999
  _CCLCMSG_SPLITPLAYERDISCONNECT._serialized_start=1001
  _CCLCMSG_SPLITPLAYERDISCONNECT._serialized_end=1046
  _CCLCMSG_SERVERSTATUS._serialized_start=1048
  _CCLCMSG_SERVERSTATUS._serialized_end=1090
  _CCLCMSG_SERVERPING._serialized_start=1092
  _CCLCMSG_SERVERPING._serialized_end=1112
  _CCLCMSG_REQUESTPAUSE._serialized_start=1114
  _CCLCMSG_REQUESTPAUSE._serialized_end=1204
  _CCLCMSG_CMDKEYVALUES._serialized_start=1206
  _CCLCMSG_CMDKEYVALUES._serialized_end=1242
  _CCLCMSG_RCONSERVERDETAILS._serialized_start=1244
  _CCLCMSG_RCONSERVERDETAILS._serialized_end=1286
  _CSVCMSG_SERVERINFO._serialized_start=1289
  _CSVCMSG_SERVERINFO._serialized_end=1676
  _CSVCMSG_CLASSINFO._serialized_start=1679
  _CSVCMSG_CLASSINFO._serialized_end=1843
  _CSVCMSG_CLASSINFO_CLASS_T._serialized_start=1771
  _CSVCMSG_CLASSINFO_CLASS_T._serialized_end=1843
  _CSVCMSG_SETPAUSE._serialized_start=1845
  _CSVCMSG_SETPAUSE._serialized_end=1879
  _CSVCMSG_VOICEINIT._serialized_start=1881
  _CSVCMSG_VOICEINIT._serialized_end=1952
  _CSVCMSG_PRINT._serialized_start=1954
  _CSVCMSG_PRINT._serialized_end=1983
  _CSVCMSG_SOUNDS._serialized_start=1986
  _CSVCMSG_SOUNDS._serialized_end=2465
  _CSVCMSG_SOUNDS_SOUNDDATA_T._serialized_start=2074
  _CSVCMSG_SOUNDS_SOUNDDATA_T._serialized_end=2465
  _CSVCMSG_PREFETCH._serialized_start=2467
  _CSVCMSG_PREFETCH._serialized_end=2555
  _CSVCMSG_SETVIEW._serialized_start=2557
  _CSVCMSG_SETVIEW._serialized_end=2610
  _CSVCMSG_FIXANGLE._serialized_start=2612
  _CSVCMSG_FIXANGLE._serialized_end=2676
  _CSVCMSG_CROSSHAIRANGLE._serialized_start=2678
  _CSVCMSG_CROSSHAIRANGLE._serialized_end=2730
  _CSVCMSG_BSPDECAL._serialized_start=2733
  _CSVCMSG_BSPDECAL._serialized_end=2871
  _CSVCMSG_SPLITSCREEN._serialized_start=2873
  _CSVCMSG_SPLITSCREEN._serialized_end=2995
  _CSVCMSG_GETCVARVALUE._serialized_start=2997
  _CSVCMSG_GETCVARVALUE._serialized_end=3054
  _CSVCMSG_MENU._serialized_start=3056
  _CSVCMSG_MENU._serialized_end=3116
  _CSVCMSG_USERMESSAGE._serialized_start=3118
  _CSVCMSG_USERMESSAGE._serialized_end=3196
  _CSVCMSG_SENDTABLE._serialized_start=3199
  _CSVCMSG_SENDTABLE._serialized_end=3503
  _CSVCMSG_SENDTABLE_SENDPROP_T._serialized_start=3330
  _CSVCMSG_SENDTABLE_SENDPROP_T._serialized_end=3503
  _CSVCMSG_GAMEEVENTLIST._serialized_start=3506
  _CSVCMSG_GAMEEVENTLIST._serialized_end=3715
  _CSVCMSG_GAMEEVENTLIST_KEY_T._serialized_start=3589
  _CSVCMSG_GAMEEVENTLIST_KEY_T._serialized_end=3624
  _CSVCMSG_GAMEEVENTLIST_DESCRIPTOR_T._serialized_start=3626
  _CSVCMSG_GAMEEVENTLIST_DESCRIPTOR_T._serialized_end=3715
  _CSVCMSG_PACKETENTITIES._serialized_start=3718
  _CSVCMSG_PACKETENTITIES._serialized_end=4468
  _CSVCMSG_PACKETENTITIES_COMMAND_QUEUE_INFO_T._serialized_start=4220
  _CSVCMSG_PACKETENTITIES_COMMAND_QUEUE_INFO_T._serialized_end=4398
  _CSVCMSG_PACKETENTITIES_ALTERNATE_BASELINE_T._serialized_start=4400
  _CSVCMSG_PACKETENTITIES_ALTERNATE_BASELINE_T._serialized_end=4468
  _CSVCMSG_TEMPENTITIES._serialized_start=4470
  _CSVCMSG_TEMPENTITIES._serialized_end=4552
  _CSVCMSG_CREATESTRINGTABLE._serialized_start=4555
  _CSVCMSG_CREATESTRINGTABLE._serialized_end=4788
  _CSVCMSG_UPDATESTRINGTABLE._serialized_start=4790
  _CSVCMSG_UPDATESTRINGTABLE._serialized_end=4885
  _CSVCMSG_VOICEDATA._serialized_start=4888
  _CSVCMSG_VOICEDATA._serialized_end=5024
  _CSVCMSG_PACKETRELIABLE._serialized_start=5026
  _CSVCMSG_PACKETRELIABLE._serialized_end=5101
  _CSVCMSG_FULLFRAMESPLIT._serialized_start=5103
  _CSVCMSG_FULLFRAMESPLIT._serialized_end=5187
  _CSVCMSG_HLTVSTATUS._serialized_start=5189
  _CSVCMSG_HLTVSTATUS._serialized_end=5274
  _CSVCMSG_SERVERSTEAMID._serialized_start=5276
  _CSVCMSG_SERVERSTEAMID._serialized_end=5317
  _CSVCMSG_CMDKEYVALUES._serialized_start=5319
  _CSVCMSG_CMDKEYVALUES._serialized_end=5355
  _CSVCMSG_RCONSERVERDETAILS._serialized_start=5357
  _CSVCMSG_RCONSERVERDETAILS._serialized_end=5416
  _CMSGIPCADDRESS._serialized_start=5418
  _CMSGIPCADDRESS._serialized_end=5477
  _CMSGSERVERPEER._serialized_start=5480
  _CMSGSERVERPEER._serialized_end=5640
  _CSVCMSG_PEERLIST._serialized_start=5642
  _CSVCMSG_PEERLIST._serialized_end=5691
  _CSVCMSG_CLEARALLSTRINGTABLES._serialized_start=5693
  _CSVCMSG_CLEARALLSTRINGTABLES._serialized_end=5740
  _PROTOFLATTENEDSERIALIZERFIELD_T._serialized_start=5743
  _PROTOFLATTENEDSERIALIZERFIELD_T._serialized_end=6017
  _PROTOFLATTENEDSERIALIZER_T._serialized_start=6019
  _PROTOFLATTENEDSERIALIZER_T._serialized_end=6126
  _CSVCMSG_FLATTENEDSERIALIZER._serialized_start=6129
  _CSVCMSG_FLATTENEDSERIALIZER._serialized_end=6275
  _CSVCMSG_STOPSOUND._serialized_start=6277
  _CSVCMSG_STOPSOUND._serialized_end=6310
  _CBIDIRMSG_REBROADCASTGAMEEVENT._serialized_start=6312
  _CBIDIRMSG_REBROADCASTGAMEEVENT._serialized_end=6433
  _CBIDIRMSG_REBROADCASTSOURCE._serialized_start=6435
  _CBIDIRMSG_REBROADCASTSOURCE._serialized_end=6485
  _CMSGSERVERNETWORKSTATS._serialized_start=6488
  _CMSGSERVERNETWORKSTATS._serialized_end=7283
  _CMSGSERVERNETWORKSTATS_PORT._serialized_start=7114
  _CMSGSERVERNETWORKSTATS_PORT._serialized_end=7148
  _CMSGSERVERNETWORKSTATS_PLAYER._serialized_start=7151
  _CMSGSERVERNETWORKSTATS_PLAYER._serialized_end=7283
  _CSVCMSG_HLTVREPLAY._serialized_start=7286
  _CSVCMSG_HLTVREPLAY._serialized_end=7500
  _CCLCMSG_HLTVREPLAY._serialized_start=7503
  _CCLCMSG_HLTVREPLAY._serialized_end=7632
  _CSVCMSG_BROADCAST_COMMAND._serialized_start=7634
  _CSVCMSG_BROADCAST_COMMAND._serialized_end=7674
  _CCLCMSG_HLTVFIXUPOPERATORTICK._serialized_start=7677
  _CCLCMSG_HLTVFIXUPOPERATORTICK._serialized_end=7916
  _CSVCMSG_HLTVFIXUPOPERATORSTATUS._serialized_start=7918
  _CSVCMSG_HLTVFIXUPOPERATORSTATUS._serialized_end=7997
# @@protoc_insertion_point(module_scope)
