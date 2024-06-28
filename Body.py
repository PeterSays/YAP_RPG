import random
import pygame
from Material import Material


class Part:
    def __init__(self, body, partkind, rel_size=1.0, critical=False, alt_mat=None):
        self.body = body
        self.partkind = partkind
        self.critical = critical
        self.connections = []
        self.volume = rel_size * self.body.volume
        self.composition = self.volume * 1000
        self.fluids = [(self.body.biofluid, 100)]
        self.leakage = 0
        self.material = self.body.material
        if alt_mat:
            self.material = alt_mat

        max_nameval = 0
        self.name = f'{partkind}'
        while self.name not in self.body.part_names:
            if max_nameval:
                self.name = f'{partkind}{max_nameval}'
            else:
                self.name = f'{partkind}{max_nameval}'
            max_nameval += 1

    def attach(self, part):
        self.connections.append(part)
        part.connections.append(self)

    def detach(self, part):
        self.connections.remove(part)
        part.connections.remove(self)
        if not part in self.body.attached_parts():
            part.body = None

class Body:
    def __init__(self, ent, spritename, volume, material, biofluid, frontside='right', base='humanoid',
                 add_hig=None, add_mid=None, add_low=None):
        self.entity = ent
        self.sprite = None
        self.spritename = spritename
        self.frontside = frontside
        self.base = base
        self.core = Part(self, 'core', critical=True)
        self.legs_needed = 0
        self.high_parts = []
        self.mid_parts = []
        self.low_parts = []
        self.part_names = []
        self.all_parts = []
        self.volume = volume
        self.material = material
        self.biofluid = biofluid

        if add_hig:
            self.high_parts.extend(add_hig)
            self.all_parts.extend(add_hig)
        if add_mid:
            self.mid_parts.extend(add_mid)
            self.all_parts.extend(add_mid)
        if add_low:
            self.low_parts.extend(add_low)
            self.all_parts.extend(add_low)

        for part in self.all_parts:
            self.part_names.append(part.name)
            self.core.attach(part)

    def load(self, ses):
        self.sprite = pygame.image.load(f'sprite/portraits/{self.spritename}')

    def attached_parts(self):
        attached = [self.core]
        for part in self.core.connections:
            if part not in attached:
                attached.append(part)

            for conn_part in part.connections:
                if conn_part not in attached:
                    attached.append(conn_part)

        return attached

