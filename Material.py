import random

class Material:
    def __init__(self, name, base_color, density, elasticity, freeze, boil,
                 r_range=10, g_range=10, b_range=10):
        self.name = name
        self.base_color = base_color
        self.r_range = r_range
        self.g_range = g_range
        self.b_range = b_range
        self.density = density  # lbs/gal
        self.elasticity = elasticity
        self.freeze_temp = freeze  # F
        self.boil_temp = boil  # F

    def get_color(self):
        new_r = self.base_color[0]+random.randint(0, self.r_range)
        new_g = self.base_color[1]+random.randint(0, self.g_range)
        new_b = self.base_color[2]+random.randint(0, self.b_range)
        return new_r, new_g, new_b


water_mat = Material('water', (10, 20, 150), 8.3, 0, 32, 212)
flesh_mat = Material('flesh', (175, 125, 115), 10.0, 1.7, 200, 210)
blood_mat = Material('blood', (75, 5, 5), 9, 0.5, 27, 220)
ectoplasm_mat = Material('ectoplasm', (230, 230, 230), 6.5, 10.0, 100, 200)

materials = {
    'flesh': flesh_mat,
    'blood': blood_mat,
    'water': water_mat,
    'ectoplasm': ectoplasm_mat
}
