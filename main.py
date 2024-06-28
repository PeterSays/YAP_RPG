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

            new_zone = Zone(20, 15, current_temp, current_prec, tilesets=(ts1, ts2))
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


def nonplayer_battle(ses, attacker, attacked):
    pass

def battle_start(ses, enemy):
    ses['game_phase'] = 'battle'
    if enemy.pending_battle:
        attacker = enemy
        attacked = ses['player']
    else:
        attacker = ses['player']
        attacked = enemy


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
            peterling = Entity('peterling1', f'peterling.png', (random.randint(0, session['latitude']-1), random.randint(0, session['longitude']-1)), spr_off=(2, -7), faction='Peterling Horde')
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
                    pass
                elif ent.pending_battle:  # nonplayer starts battle with nonplayer
                    pass
                
            elif ent.pending_battle:  # player starts battle (with nonplayer)
                pass

    # Display
    layer = -1
    screen.fill((0, 0, 0))
    for display_list in display_array:
        layer += 1

        for displayed in display_list:
            screen.blit(displayed.sprite, (displayed.x, displayed.y))
    display_array = [[], [], [], [], []]

    pygame.display.flip()

    fps_clock.tick(fps)

pygame.quit()
