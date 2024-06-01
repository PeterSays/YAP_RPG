import numpy
from Tile import Tile

class Zone:
    def __init__(self, t_col, t_row, pos=(0, 0)):
        self.x = pos[0]
        self.y = pos[1]
        self.tile_array = []
        self.tile_col = t_col
        self.tile_row = t_row

        for row_ind in range(t_row):
            new_row = []
            for col_ind in range(t_col):
                new_tile = Tile(self, (col_ind, row_ind))
                new_row.append(new_tile)

    def update():
        for tile in self.tile_array:
            tile.update()
