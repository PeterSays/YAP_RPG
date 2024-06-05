import pygame.image
import os
import Entity

class Tile:
    def __init__(self, zone, pos, tileset: str, spritename: str):
        self.zone = zone
        self.pos = pos
        self.y = pos[1]*32
        self.x = pos[0]*32
        self.initialized = False  # refers to if the tile has been checked to connect with adjacent tiles
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.sprite = None
        self.tileset = tileset
        self.spritename = spritename

    def load(self):
        self.sprite = pygame.image.load(f'{os.curdir}/sprite/tiles/{self.spritename}')
        self.y = self.pos[1]*32 + self.zone.y
        self.x = self.pos[0]*32 + self.zone.x

        if self.pos[1] > 0:
            self.north = self.zone.tile_array[self.pos[1]-1][self.pos[0]]
        if self.pos[1] < len(self.zone.tile_array)-1:
            self.south = self.zone.tile_array[self.pos[1]+1][self.pos[0]]
        if self.pos[0] > 0:
            self.west = self.zone.tile_array[self.pos[1]][self.pos[0]-1]
        if self.pos[0] < len(self.zone.tile_array[0])-1:
            self.east = self.zone.tile_array[self.pos[1]][self.pos[0]+1]

        self.initialized = True

    def unload(self):
        self.sprite = None
        self.x = self.pos[0]*32
        self.y = self.pos[1]*32
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.initialized = False

    def update(self):
        pass
