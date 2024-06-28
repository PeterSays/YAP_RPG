import random

class Material:
    def __init__(self, name, base_color, density, elasticity, melt, freeze, boil,
                 r_range=10, g_range=10, b_range=10):
        self.name = name
        self.base_color = base_color
        self.r_range = r_range
        self.g_range = g_range
        self.b_range = b_range
        self.density = density
        self.elasticity = elasticity
        self.melt_temp = melt
        self.freeze_temp = freeze
        self.boil_temp = boil

    def get_color(self):
        new_r = self.base_color[0]+random.randint(0, self.r_range)
        new_g = self.base_color[1]+random.randint(0, self.g_range)
        new_b = self.base_color[2]+random.randint(0, self.b_range)
        return new_r, new_g, new_b
