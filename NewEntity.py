from Field.FieldState import FieldState


class NewEntity:
    def __init__(self, index, serial, demo_class):
        self.index = index
        self.serial = serial
        self.demo_class = demo_class
        self.active = True
        self.state = FieldState()
        self.fpCache = {}
        self.fpNoop = {}
