import random
import pygame

primary_rgb = (128, 128, 128)
secondary_rgb = (230, 230, 230)
tertiary_rgb = (179, 179, 179)

def varied(orig_rgb, var, r_var=0, g_var=0, b_var=0):
    or_r = orig_rgb[0]
    or_g = orig_rgb[1]
    or_b = orig_rgb[2]

    nw_r = or_r + random.randint(abs(var)*-1, abs(var)) + random.randint(abs(r_var)*-1, abs(r_var))
    nw_g = or_g + random.randint(abs(var) * -1, abs(var)) + random.randint(abs(g_var) * -1, abs(g_var))
    nw_b = or_b + random.randint(abs(var) * -1, abs(var)) + random.randint(abs(b_var) * -1, abs(b_var))

    return nw_r, nw_g, nw_b

def replace_color(new_path, grey_path, primary, secondary, tertiary):
    primary_rgb_ = (128, 128, 128)
    secondary_rgb_ = (230, 230, 230)
    tertiary_rgb_ = (179, 179, 179)

    old_sprite = pygame.image.load(f'./sprite/{grey_path}')
    prim = old_sprite.map_rgb(primary_rgb_)
    seco = old_sprite.map_rgb(secondary_rgb_)
    tert = old_sprite.map_rgb(tertiary_rgb_)
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


def make_lines(new_path, bgtile='blank_0.png'):
    primary_rgb_ = (128, 128, 128)
    secondary_rgb_ = (230, 230, 230)
    tertiary_rgb_ = (179, 179, 179)

    blank = pygame.image.load(f'./sprite/tiles/{bgtile}')
    blank_array = pygame.PixelArray(blank)
    secondary_ink = 0
    tertiary_ink = 0
    sprite_shape = blank.get_size()
    for row in range(sprite_shape[0]):
        secondary_ink = 0
        tertiary_ink = 0
        for col in range(sprite_shape[1]):
            if not secondary_ink and not random.randint(0, 12):
                secondary_ink += random.randint(3, 10)
            if not tertiary_ink and not random.randint(0, 20):
                tertiary_ink += random.randint(1, 3)

            if secondary_ink > 0:
                blank_array[col, row] = pygame.Color(secondary_rgb_)
                secondary_ink -= 1
            if tertiary_ink > 0:
                blank_array[col, row] = pygame.Color(tertiary_rgb_)
                tertiary_ink -= 1
            if secondary_ink > 0 and random.randint(0, 1):
                blank_array[col, row] = pygame.Color(secondary_rgb_)
                secondary_ink -= 1

    new_sprite = blank_array.surface
    blank_array.close()
    pygame.image.save(new_sprite, f'./sprite/{new_path}')
    return new_sprite


# make_lines('test.png')
# replace_color('result.png', 'tiles/greyed_0.png', (163, 156, 62), (185, 178, 85), (147, 137, 70))
