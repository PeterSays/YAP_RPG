import random
import pygame
import os

from Body import Body
from Stats import Stats, new_stats


class Entity:
    def __init__(self, name, spritename, pos, spr_off=(0, 0), player=False, faction=None, lvl=5, stat_dict=None):
        self.name = name
        self.spritename = spritename
        self.sprite = None
        self.is_player = player
        self.in_battle = None
        self.move_dir = (0, 0)
        self.pos = pos
        self.sprite_offset = spr_off
        self.x = self.pos[0] * 32
        self.y = self.pos[1] * 32
        self.marchto_x = self.pos[0] * 32
        self.marchto_y = self.pos[1] * 32
        self.blocking = []
        self.pending_battle = None
        self.pending_tile = None
        self.faction_alignment = {}
        self.entity_relations = {}
        self.faction = faction
        if self.is_player:
            self.faction = 'Player Team'

        self.landed = False
        self.current_action = None
        self.action_completed = False
        self.action_queue = []

        self.body = Body(self, self.spritename, stats_dict=stat_dict, lvl=lvl)

    def load(self, ses):
        print(f'Loading {self.name}')
        self.x = self.pos[1] * 32
        self.y = self.pos[0] * 32
        self.marchto_x = self.pos[0] * 32
        self.marchto_y = self.pos[1] * 32
        self.sprite = pygame.image.load(f'sprite/map_entities/{self.spritename}')
        if self.faction and self.faction in ses['factions'].keys():  # in existing faction
            for ent in ses['entities']:

                if ent.name not in self.entity_relations.keys():
                    relation = 0
                    if ent.faction and ses['factions'][self.faction]:
                        if ent.faction in ses['factions'][self.faction].keys():
                            relation = ses['factions'][self.faction][ent.faction]

                    self.entity_relations[ent.name] = relation
                    if self.name not in ent.entity_relations.keys():
                        ent.entity_relations[self.name] = relation

        elif self.faction:
            ses['factions'][self.faction] = {}

            for ent in ses['entities']:

                if ent.name not in self.entity_relations.keys():
                    relation = 0
                    if ent.faction and ses['factions'][self.faction]:
                        if ent.faction in ses['factions'][self.faction].keys():
                            relation = ses['factions'][self.faction][ent.faction]

                    self.entity_relations[ent.name] = relation
                    if self.name not in ent.entity_relations.keys():
                        ent.entity_relations[self.name] = relation

        else:  # not in faction
            for ent in ses['entities']:
                if ent.name not in self.entity_relations.keys():
                    relation = random.randint(-25, 25)
                    self.entity_relations[ent.name] = relation
                    if self.name not in ent.entity_relations.keys():
                        ent.entity_relations[self.name] = relation

        if self not in ses['entities']:
            ses['entities'].append(self)

    def unload(self, ses):
        self.sprite = None
        if self in ses['entities']:
            ses['entities'].remove(self)

    def get_relation(self, withwho):
        pass

    def change_entity_relation(self, withwho, amount):
        pass

    def change_faction_alignment(self, ses, withfac, amount):
        pass

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

        if not self.is_player:
            if len(self.action_queue) and ((self.current_action and self.action_completed) or not self.current_action):
                next_action = self.action_queue.pop(0)
                self.current_action = next_action
                self.action_completed = False
