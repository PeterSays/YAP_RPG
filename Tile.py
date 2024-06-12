import random

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

        self.structure = None
        self.entity = None

        self.ses = None


    def blocked(self, from_dir):
        all_blocks = []
        for ent in self.entities:
            if len(ent.blocking):
                all_blocks.extend(ent.blocking)
        all_blocks.extend(self.structure.blocking)
        if from_dir in all_blocks:
            return True

    def ent_leave(self):
        enthere = self.entity
        self.entity = None
        return enthere

    def ent_join(self, ent, fromtile, forced=False):
        from_dir = ''

        if not forced:
            if fromtile.pos[1] < self.pos[1]:
                from_dir += 'N'
            elif fromtile.pos[1] > self.pos[1]:
                from_dir += 'S'

            if fromtile.pos[0] < self.pos[0]:
                from_dir += 'W'
            elif fromtile.pos[0] > self.pos[0]:
                from_dir += 'E'

            if not self.sprite:
                self.load(fromtile.ses)

        if not self.entity and (forced or not self.blocked(from_dir)):
            self.entity = ent

            return True

        elif not self.entity:
            return False
        else:
            return False

    def load(self, session):
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
        self.ses = session

        if self.structure:
            self.structure.load(session)

        if self.entity:
            self.entity.load(session)

    def unload(self, session):
        self.sprite = None
        self.x = self.pos[0]*32
        self.y = self.pos[1]*32
        self.north = None
        self.south = None
        self.east = None
        self.west = None
        self.initialized = False

        if self.structure:
            self.structure.unload(session)

        if self.entity:
            self.entity.unload(session)

    def update(self):
        pass
