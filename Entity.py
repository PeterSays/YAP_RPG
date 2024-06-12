import random

import pygame
import os


class Entity:
    def __init__(self, name, spritename, pos, spr_off=(0, 0), player=False):
        self.name = name
        self.spritename = spritename
        self.sprite = None
        self.pos = pos
        self.sprite_offset = spr_off
        self.x = self.pos[0] * 32
        self.y = self.pos[1] * 32
        self.marchto_x = self.pos[0] * 32
        self.marchto_y = self.pos[1] * 32
        self.blocking = []

        self.landed = False

    def load(self, ses):
        self.x = self.pos[1] * 32
        self.y = self.pos[0] * 32
        self.marchto_x = self.pos[0] * 32
        self.marchto_y = self.pos[1] * 32
        self.sprite = pygame.image.load(f'{os.curdir}/sprite/map_entities/{self.spritename}')
        if self not in ses['entities']:
            ses['entities'].append(self)

    def unload(self, ses):
        self.sprite = None
        if self in ses['entities']:
            ses['entities'].remove(self)

    def update(self):
        still_x = False
        still_y = False

        if self.x > self.marchto_x + self.sprite_offset[0]:
            self.x -= random.randint(1, 3)
        elif self.x < self.marchto_x + self.sprite_offset[0]:
            self.x += random.randint(1, 3)
        else:
            still_x = True

        if self.y > self.marchto_y + self.sprite_offset[1]:
            self.y -= random.randint(1, 3)
        elif self.y < self.marchto_y + self.sprite_offset[1]:
            self.y += random.randint(1, 3)
        else:
            still_y = True

        if still_x and still_y and not self.landed:
            print(f'{self.name} @ {self.pos}: {self.x}, {self.y}')
            self.landed = True
