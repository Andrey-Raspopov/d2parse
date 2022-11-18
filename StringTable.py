class StringTable:
    def __init__(self, index, name, user_data_fixed_size, user_data_size, user_data_size_bits, flags):
        self.index = index
        self.name = name
        self.items = {}
        self.user_data_fixed_size = user_data_fixed_size
        self.user_data_size = user_data_size
        self.user_data_size_bits = user_data_size_bits
        self.flags = flags
