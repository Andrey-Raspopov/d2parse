class Serializer:
    def __init__(self, msg, s):
        self.name = msg.symbols[s.serializer_name_sym]
        self.version = s.serializer_version
        self.fields = []
