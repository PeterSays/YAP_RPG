import os
import random
from random import choice
from Tile import Tile

class Zone:
    def __init__(self, session, t_col, t_row, temper, precip, tilesets=('grass', 'grass')):
        self.x = 0
        self.y = 0
        self.tilesets = tilesets
        self.tile_array = []
        self.tile_col = t_col
        self.tile_row = t_row
        self.tile_spritenames = {}

        self.temperature = temper
        self.precipitation = precip

        self.north_neighbor = None
        self.south_neighbor = None
        self.east_neighbor = None
        self.west_neighbor = None
        self.initialized = False  # refers to if the zone has been checked to be connected with neighbors

        for tileset in tilesets:
            if tileset not in self.tile_spritenames.keys():
                self.tile_spritenames[tileset] = []

                all_tiles = os.listdir('./sprite/tiles')
                for til in all_tiles:
                    if til[:til.find('_')] == tileset:
                        self.tile_spritenames[tileset].append(til)

        for row_ind in range(t_row):
            new_row = []
            for col_ind in range(t_col):
                this_tileset = random.choice(tilesets)
                new_tile = Tile(self, (col_ind, row_ind), this_tileset, choice(self.tile_spritenames[this_tileset]))
                new_row.append(new_tile)
            self.tile_array.append(new_row)

    def tile_list(self):
        tl = []
        for row in self.tile_array:
            for tile in row:
                tl.append(tile)
        return tl

    def load(self, session):
        if not session['zone_loaded'][0]:
            session['zone_loaded'] = []

        session['zone_loaded'].append(self)
        session['scrolling'] = False
        if round(session['screen_width']/32) == self.tile_col:
            self.x = 0
        else:
            self.x = round((session['screen_width'] * 0.5) - (0.5 * self.tile_col * 32))
            session['scrolling'] = True

        if round(session['screen_height']/32) == self.tile_row:
            self.y = 0
        else:
            self.y = round((session['screen_height'] * 0.5) - (0.5 * self.tile_row * 32))
            session['scrolling'] = True

        for tile in self.tile_list():
            tile.load()

        # self.initialized must be made true in main.py - generate_world() after connecting to other zones

    def unload(self, session):
        if self in session['zone_loaded']:
            session['zone_loaded'].remove(self)

        if not len(session['zone_loaded']):
            session['zone_loaded'] = [None]

        self.north_neighbor = None
        self.south_neighbor = None
        self.east_neighbor = None
        self.west_neighbor = None

        for tile in self.tile_list():
            tile.unload()

        self.initialized = False

    def update(self):
        for tile in self.tile_list():
            tile.update()
