class GameEvent(object):
    def __init__(self, name):
        self.name = name
        self.keys = {}

    def __str__(self):
        return "%s: %s" % (self.name, self.keys)
