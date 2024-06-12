import os
import pygame

class Structure:
    def __init__(self, spritename, tile, spr_off=(0, 0)):
        self.spritename = spritename
        self.sprite = None
        self.pos = tile.pos
        self.blocking = []
        self.y = tile.pos[1] * 32
        self.x = tile.pos[0] * 32

    def load(self, session):
        self.sprite = pygame.image.load(f'{os.curdir}/sprite/map_entities/{self.spritename}')
        if self not in session['structures']:
            session['structures'].append(self)

    def unload(self, session):
        self.sprite = None
        if self in session['structures']:
            session['structures'].remove(self)

    def update(self):
        pass
