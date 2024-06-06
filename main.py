import random

import pygame
from pygame.locals import *
from Zone import Zone

pygame.init()
fps = 60
fps_clock = pygame.time.Clock()
scr_width = 640
scr_height = 480
screen = pygame.display.set_mode((scr_width, scr_height))
pygame.display.set_caption("YAPSRPG")

session = {
    'screen_width': scr_width,
    'screen_height': scr_height,
    'scrolling': False,
    'screen_surface': screen,
    'game_phase': 'map',  # title, loading, map, battle
    'zone_loaded': [None],
    'latitude': 3,
    'longitude': 3,
    'world': []
}

tileset_properties = {
    'grass': {}
}

climate_map = [  # first dimension is temperature, second is precip
    ['frozen', 'tundra', 'taiga'],
    ['barren', 'grass', 'jungle'],
    ['desert', 'shrubs', 'tropic'],
]

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
            new_zone = Zone(ses, 20, 15, current_temp, current_prec, tilesets=(climate_map[index_temp][index_prec], climate_map[index_temp][index_prec]))
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

    starting_zone.load(session)

    return new_world


session['world'] = generate_world(session, 3, 3)

grassland = Zone(session, 20, 15, tilesets=('grass', 'frozen'))
grassland.load(session)

display_array = [[], [], [], [], []]
frame_no = -1
running = True
while running:
    frame_no += 1
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Gameloop
    if session['game_phase'] == 'map':
        display_array[0].extend(session['zone_loaded'][0].tile_list())

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
