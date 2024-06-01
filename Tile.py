import Entity

class Tile:
    def __init__(self, zone, pos):
        self.zone = zone
        self.y = pos[0]
        self.x = pos[1]
        self.initialized = False
        self.north = None
        self.south = None
        self.east = None
        self.west = None

    def update(self):
        pass
