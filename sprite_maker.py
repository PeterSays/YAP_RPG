import random
import pygame

def replace_color(new_path, grey_path, primary, secondary, tertiary):
    prim = 4286611584  # 128, 128, 128
    seco = 4293322470  # 230, 230, 230
    tert = 4289967027  # 179, 179, 179
    old_sprite = pygame.image.load(f'./sprite/{grey_path}')
    prim_replace = old_sprite.map_rgb(primary)
    seco_replace = old_sprite.map_rgb(secondary)
    tert_replace = old_sprite.map_rgb(tertiary)
    oldsprite_array = pygame.PixelArray(old_sprite)
    oldsprite_array.replace(prim, prim_replace)
    oldsprite_array.replace(seco, seco_replace)
    oldsprite_array.replace(tert, tert_replace)
    new_sprite = oldsprite_array.surface
    oldsprite_array.close()
    pygame.image.save(new_sprite, f'./sprite/{new_path}')
    return new_sprite


def make_lines(new_path):
    blank = pygame.image.load(f'./sprite/tiles/blank_0.png')
    blank_array = pygame.PixelArray(blank)
    primary_ink = 0
    secondary_ink = 0
    sprite_shape = blank.get_size()
    for row in range(sprite_shape[0]):
        primary_ink = 0
        secondary_ink = 0
        for col in range(sprite_shape[1]):
            if not primary_ink and not random.randint(0, 5):
                primary_ink += random.randint(3, 10)
            if not secondary_ink and not random.randint(0, 9):
                secondary_ink += random.randint(3, 10)

            if primary_ink > 0:
                blank_array[col, row] = pygame.Color(4286611584)
                primary_ink -= 1
            if secondary_ink > 0:
                blank_array[col, row] = pygame.Color(4293322470)
                secondary_ink -= 1
            if primary_ink > 0 and random.randint(0, 1):
                blank_array[col, row] = pygame.Color(4286611584)
                primary_ink -= 1

    new_sprite = blank_array.surface
    blank_array.close()
    pygame.image.save(new_sprite, f'./sprite/{new_path}')
    return new_sprite


# make_lines('test.png')
# replace_color('test.png', '/tiles/greyed_0.png', (0, 0, 8), (70, 70, 80), (65, 30, 40))
# testimg = pygame.image.load('./sprite/test.png')
# testarray = pygame.PixelArray(testimg)
# print(testarray)
