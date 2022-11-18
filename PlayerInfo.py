import ctypes


class PlayerInfo(ctypes.Structure):
    """
    The player_info_s struct that is used to store some player information.
    Easier to use ctypes because of the byte alignment that structs do

    For some reason the ctypes.sizeof() for this structure says 144, but the
    binary data is 140. It doesn't seem to cause any problems but there may
    be a mistake in here somewhere that I haven't been able to find
    """
    _fields_ = [
        ("xuid", ctypes.c_ulonglong),
        ("name", ctypes.c_char * 32),
        ("userID", ctypes.c_int32),
        ("guid", ctypes.c_char * 33),
        ("friendsID", ctypes.c_uint32),
        ("friendsName", ctypes.c_char * 32),
        ("fakeplayer", ctypes.c_bool),
        ("ishltv", ctypes.c_bool),
        ("customFiles", ctypes.c_uint32 * 4),
        ("filesDownloaded", ctypes.c_ubyte),
    ]

    def __str__(self):
        return ", ".join("%s=%s" % (x[0], getattr(self, x[0])) for x in
                        self._fields_)
