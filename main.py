import random

import pygame
from pygame.locals import *
from Zone import Zone
from Entity import Entity
from Body import Body, Part

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
scr_width = 640
scr_height = 480
screen = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("YAPSRPG")

ground_level = scr_height - 30

class Line:
    def __init__(self, x1, y1, x2, y2, col, thick=1):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = col
        self.thickness = thick

    def pos1(self):
        return self.x1, self.y1

    def pos2(self):
        return self.x2, self.y2


class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lines = []

    def move(self, mx, my):
        self.x += mx
        self.y = my
        for line in self.lines:
            line.x1 += mx
            line.x2 += mx
            line.y1 += my
            line.y2 += my


class Background:
    def __init__(self, ses, flow1=1, flow2=2, extremeness=5, shape='tree',
                 pri=(100, 100, 100), sec=(25, 25, 25)):
        self.clock = 0
        self.shape_interval = 200
        self.extremeness = extremeness
        self.shape_type = shape
        self.shapes1 = []
        self.shapes2 = []
        self.session = ses
        self.primary_color = pri
        self.secondary_color = sec
        self.flow1 = flow1  # how many pixels a shape in the front bg will move
        self.flow2 = flow2  # how many pixels a shape in the back bg will move

    def draw_shape(self, which=0):
        start = 0
        flows = (self.flow1, self.flow2)
        shapes = (self.shapes1, self.shapes2)
        if flows[which] < 0:
            start = scr_width
        new_shape = Shape(start, ground_level)

        shapes[which].append(new_shape)

    def routine(self):
        self.clock += 1

        if self.clock % self.shape_interval == 0:
            self.draw_shape()

        for sh in self.shapes:
            sh.move(self.flow)


key_map = {
    'MoveNW': pygame.K_KP7,
    'MoveN': pygame.K_KP8,
    'MoveNE': pygame.K_KP9,
    'MoveE': pygame.K_KP6,
    'MoveSE': pygame.K_KP3,
    'MoveS': pygame.K_KP2,
    'MoveSW': pygame.K_KP1,
    'MoveW': pygame.K_KP4,
    'Stay': pygame.K_KP5,
}

session = {
    'screen_width': scr_width,
    'screen_height': scr_height,
    'scrolling': False,
    'screen_surface': screen,
    'game_phase': 'map',  # title, loading, map, battle
    'zone_loaded': [None],
    'latitude': 3,
    'longitude': 3,
    'world': [],
    'player': None,
    'entities': [],
    'structures': [],
    'factions': {  # names of other factions as keys, relations as values
        'Player Team': {
            'Peterling Horde': -100
        },

        'Peterling Horde': {
            'Player Team': -100
        }
    },
    'battle': {'attacker': None, 'attacked': None}
}

tileset_properties = {
    'grass': {}
}

climate_map = [  # first dimension is temperature, second is precip
    ['snow', 'tundra', 'taiga'],
    ['shrubs', 'grass', 'jungle'],
    ['desert', 'swamp', 'tropic'],
]
extra_tilesets = ['stone', 'water']

def generate_world(ses, lat, lon):
    new_world = []

    current_temp = random.randint(0, 2)
    current_prec = random.randint(0, 2)
    temp_direction_col = random.randint(-100, 100) / 100
    temp_direction_row = random.randint(-100, 100) / 100
    prec_direction_col = random.randint(-100, 100) / 100
    prec_direction_row = random.randint(-100, 100) / 100
    starting_zone = None

    for row in range(lon):  # making zone array
        new_row = []
        for col in range(lat):
            index_temp = round(max(min(2, current_temp), 0))  # takes care of over-/under- values
            index_prec = round(max(min(2, current_prec), 0))
            possible_tilesets = [
                climate_map[index_temp][index_prec], climate_map[index_temp][index_prec],
            ]
            possible_tilesets.extend(extra_tilesets)
            ts1 = random.choice(possible_tilesets)
            ts2 = random.choice(possible_tilesets)
            ts1_names = []
            for i in range(3):
                ts1_names.append(f'{ts1}_{i}.png')
            ts2_names = []
            for i in range(3):
                ts2_names.append(f'{ts2}_{i}.png')
            ts_names = {ts1: ts1_names, ts2: ts2_names}

            new_zone = Zone(20, 15, current_temp, current_prec, tilesets=(ts1, ts2),
                            tile_spritenames=ts_names)
            new_row.append(new_zone)

            if row == round((lat-1)/2) and col == round((lon-1)/2):
                starting_zone = new_zone

            current_temp += temp_direction_col
            current_prec += prec_direction_col

        new_world.append(new_row)

        current_temp += temp_direction_row
        current_prec += prec_direction_row

    for row in range(lon):  # connecting adjacent zones
        for col in range(lat):
            this_zone = new_world[row][col]

            if row > 0:
                this_zone.north_neighbor = new_world[row-1][col]
            if row < lon-1:
                this_zone.south_neighbor = new_world[row+1][col]
            if col > 0:
                this_zone.west_neighbor = new_world[row][col-1]
            if col > lat-1:
                this_zone.east_neighbor = new_world[row][col+1]

            this_zone.initialized = True

    starting_tile = random.choice(starting_zone.tile_list())
    player = Entity('peter1', f'peter.png', starting_tile.pos, player=True, spr_off=(-1, -1))
    ses['player'] = player

    starting_tile.ent_join(player, None, forced=True)
    starting_zone.load(ses)
    player.load(ses)

    return new_world


def nonplayer_battle_start(ses, attacker, attacked):
    pass


def battle_start(ses, enemy):
    ses['game_phase'] = 'battle'
    if enemy.pending_battle:
        attacker = enemy
        attacked = ses['player']
    else:
        attacker = ses['player']
        attacked = enemy

    ses['battle']['attacker'] = attacker
    ses['battle']['attacked'] = attacked

    attacker.body.load()
    attacked.body.load()

    # attacker faces left from the right side of the screen
    # attacked faces right from the left side of the screen

    if attacker.body.frontside == 'right':
        attacker.body.sprite = pygame.transform.flip(attacker.body.sprite, True, False)
        attacker.body.x_flipped = True

    if attacked.body.frontside == 'left':
        attacked.body.sprite = pygame.transform.flip(attacked.body.sprite, True, False)
        attacked.body.x_flipped = True

    attacked.body.x = round(scr_width/2) - (30 + attacked.body.sprite.get_width())
    attacked.body.y = ground_level - attacked.body.sprite.get_height()

    attacker.body.x = round(scr_width/2) + 30
    attacker.body.y = ground_level - attacker.body.sprite.get_height()


def battle_end(ses):
    ses['battle']['attacker'].body.x_flipped = False
    ses['battle']['attacked'].body.x_flipped = False


session['world'] = generate_world(session, 3, 3)
input_interrupt = False
player_sent_input = False
moveto_attempt = None

display_array = [[], [], [], [], []]
frame_no = -1
running = True
while running:
    frame_no += 1
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and not player_sent_input and not input_interrupt and session['player']:
            if session['game_phase'] == 'map':
                cur_pos = session['player'].pos
                cur_tile = session['zone_loaded'][0].tile_array[cur_pos[1]][cur_pos[0]]
                if event.key == key_map['MoveN']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.north
                    session['player'].move_dir = (0, -1)
                elif event.key == key_map['MoveNW']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.northwest
                    session['player'].move_dir = (-1, -1)
                elif event.key == key_map['MoveNE']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.northeast
                    session['player'].move_dir = (1, -1)
                elif event.key == key_map['MoveE']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.east
                    session['player'].move_dir = (1, 0)
                elif event.key == key_map['MoveSE']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.southeast
                    session['player'].move_dir = (1, 1)
                elif event.key == key_map['MoveS']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.south
                    session['player'].move_dir = (0, 1)
                elif event.key == key_map['MoveSW']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.southwest
                    session['player'].move_dir = (-1, 1)
                elif event.key == key_map['MoveW']:
                    player_sent_input = True
                    moveto_attempt = cur_tile.west
                    session['player'].move_dir = (-1, 0)
                elif event.key == key_map['Stay']:
                    player_sent_input = True
                    moveto_attempt = None
                    session['player'].move_dir = (0, 0)
            elif session['game_phase'] == 'battle':
                atkr = session['battle']['attacker']
                atkd = session['battle']['attacked']

    # Gameloop
    if session['game_phase'] == 'map':
        display_array[0].extend(session['zone_loaded'][0].tile_list())
        display_array[1].extend(session['structures'])
        display_array[2].extend(session['entities'])

        if player_sent_input and session['player']:  # player move
            player_sent_input = False
            if moveto_attempt:
                current_pos = session['player'].pos
                current_tile = session['zone_loaded'][0].tile_array[current_pos[1]][current_pos[0]]
                move_result = moveto_attempt.ent_join(session['player'], current_tile)
                move_success = move_result[0]
                if move_success:
                    pass
                else:
                    print(f'{move_success}: {move_result[1]}')
            elif session['player'].move_dir[0] == 0 and session['player'].move_dir[1] == 0:
                pass
            else:  # run into wall
                print('bump')  # play 'bump' noise

            session['player'].move_dir = (0, 0)

        if frame_no == 20 and len(session['entities']) == 1:
            player2 = Entity('peter2', f'peter.png', (random.randint(0, session['latitude']-1), random.randint(0, session['longitude']-1)), spr_off=(-1, -1))
            st = random.choice(session['zone_loaded'][0].tile_list())
            st.ent_join(player2, None, forced=True)
            player2.load(session)

        if frame_no == 40 and len(session['entities']) == 2:
            peterling = Entity('peterling1', f'peterling.png', (random.randint(0, session['latitude']-1), random.randint(0, session['longitude']-1)),  spr_off=(2, -7), faction='Peterling Horde')
            st = random.choice(session['zone_loaded'][0].tile_list())
            st.ent_join(peterling, None, forced=True)
            peterling.load(session)

        for ent in session['entities']:
            ent.update()

            if not ent.is_player:
                if ent.current_action and 'move' in ent.current_action.lower():  # notplayer move
                    current_pos = ent.pos
                    current_tile = session['zone_loaded'][0].tile_array[current_pos[1]][current_pos[0]]
                    moveto_tile = session['zone_loaded'][0].tile_array[current_pos[1] + ent.move_dir[1]][current_pos[0] + ent.move_dir[0]]
                    move_result = moveto_tile.ent_join(ent, current_tile)
                    move_success = move_result[0]

                    ent.move_dir = (0, 0)
                    ent.action_completed = True

                    if ent.current_action == 'MoveN':
                        ent.move_dir = (0, -1)
                    elif ent.current_action == 'MoveNW':
                        ent.move_dir = (-1, -1)
                    elif ent.current_action == 'MoveNE':
                        ent.move_dir = (1, -1)
                    elif ent.current_action == 'MoveE':
                        ent.move_dir = (-1, 0)
                    elif ent.current_action == 'W':
                        ent.move_dir = (-1, 0)
                    elif ent.current_action == 'MoveSW':
                        ent.move_dir = (-1, 1)
                    elif ent.current_action == 'MoveSE':
                        ent.move_dir = (1, 1)
                    elif ent.current_action == 'MoveS':
                        ent.move_dir = (0, 1)

                if ent.pending_battle and ent.pending_battle.is_player:  # nonplayer starts battle with player
                    input_interrupt = True
                    battle_start(session, ent)
                elif ent.pending_battle:  # nonplayer starts battle with nonplayer
                    nonplayer_battle_start(session)
                
            elif ent.pending_battle:  # player starts battle (with nonplayer)
                input_interrupt = True
                battle_start(session, ent.pending_battle)

    elif session['game_phase'] == 'battle':
        display_array[2].append(Line(0, ground_level, scr_width, ground_level, (75, 20, 50), thick=5))  # the ground
        display_array[3].append(session['battle']['attacker'].body)
        display_array[3].append(session['battle']['attacked'].body)

    # Display
    layer = -1
    screen.fill((0, 0, 0))
    for display_list in display_array:
        layer += 1

        for displayed in display_list:
            if type(displayed) == Line:
                pygame.draw.line(screen, displayed.color, displayed.pos1(), displayed.pos2())
            else:
                screen.blit(displayed.sprite, (displayed.x, displayed.y))
    display_array = [[], [], [], [], []]

    pygame.display.flip()

    fps_clock.tick(fps)

pygame.quit()
