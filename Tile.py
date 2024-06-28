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
        self.northwest = None
        self.northeast = None
        self.south = None
        self.southwest = None
        self.southeast = None
        self.east = None
        self.west = None
        self.sprite = None
        self.tileset = tileset
        self.spritename = spritename
        self.walkable = True

        self.structure = None
        self.entity = None

        self.ses = None

    def blocked(self, from_dir):
        if self.structure and from_dir in self.structure.blocking:
            return self.structure

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
            if fromtile:
                fromtile.entity = None
            self.entity = ent
            self.entity.pos = self.pos
            self.entity.marchto_x = self.pos[0] * 32
            self.entity.marchto_y = self.pos[1] * 32
            return True, None

        elif not self.entity and self.structure:  # blocked by structure

            return False, self.structure

        elif self.entity:  # blocked by entity
            print(f'Entity collision @ {self.pos}')
            # determine reaction based on allegiance
            # battle if opposed
            # winner takes the spot, loser dies, positions stay if fled
            # swap places with player character if unopposed
            if ent.entity_relations[self.entity.name] < -50:  # enemies
                ent.pending_battle = self.entity
                ent.pending_tile = self
                return False, self.entity
            else:
                swapping_ent = self.entity
                self.entity = None
                fromtile.entity = None
                fromtile.ent_join(swapping_ent, self)
                self.entity = ent
                self.entity.pos = self.pos
                self.entity.marchto_x = self.pos[0] * 32
                self.entity.marchto_y = self.pos[1] * 32
                return True, swapping_ent
        else:
            return False, None

    def load(self, session):
        self.sprite = pygame.image.load(f'{os.curdir}/sprite/tiles/{self.spritename}')
        self.y = self.pos[1]*32 + self.zone.y
        self.x = self.pos[0]*32 + self.zone.x

        if self.pos[1] > 0:
            self.north = self.zone.tile_array[self.pos[1]-1][self.pos[0]]
            self.zone.tile_array[self.pos[1] - 1][self.pos[0]].south = self

            if self.pos[0] > 0:
                self.northwest = self.zone.tile_array[self.pos[1]-1][self.pos[0]-1]
                self.zone.tile_array[self.pos[1] - 1][self.pos[0] - 1].southeast = self

            if self.pos[0] < len(self.zone.tile_array)-1:
                self.northeast = self.zone.tile_array[self.pos[1]-1][self.pos[0]+1]
                self.zone.tile_array[self.pos[1] - 1][self.pos[0] + 1].southwest = self

        if self.pos[1] < len(self.zone.tile_array)-1:
            self.south = self.zone.tile_array[self.pos[1]+1][self.pos[0]]
            self.zone.tile_array[self.pos[1] + 1][self.pos[0]].north = self
            if self.pos[0] > 0:
                self.southwest = self.zone.tile_array[self.pos[1]+1][self.pos[0]-1]
                self.zone.tile_array[self.pos[1] + 1][self.pos[0] - 1].northeast = self

            if self.pos[0] < len(self.zone.tile_array)-1:
                self.southeast = self.zone.tile_array[self.pos[1]+1][self.pos[0]+1]
                self.zone.tile_array[self.pos[1] + 1][self.pos[0] + 1].northwest = self

        if self.pos[0] > 0:
            self.west = self.zone.tile_array[self.pos[1]][self.pos[0]-1]
            self.zone.tile_array[self.pos[1]][self.pos[0] - 1].east = self
        if self.pos[0] < len(self.zone.tile_array[0])-1:
            self.east = self.zone.tile_array[self.pos[1]][self.pos[0]+1]
            self.zone.tile_array[self.pos[1]][self.pos[0] + 1].west = self

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
        self.northwest = None
        self.northeast = None
        self.south = None
        self.southwest = None
        self.southeast = None
        self.east = None
        self.west = None
        self.initialized = False

        if self.structure:
            self.structure.unload(session)

        if self.entity:
            self.entity.unload(session)

    def update(self):
        pass
