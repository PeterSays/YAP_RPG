from Material import Material, materials
import random

class PhysObj:
    def __init__(self, volume, material, melts=True, reach=1, fluidcap=100, add_fluid=None):
        self.volume = volume
        self.composition = self.volume
        self.max_composition = self.composition
        self.material = material
        self.fluids = []  # holds tuples (unit int, material)
        if add_fluid:
            self.fluids.append(add_fluid)
        self.fluid_cap = fluidcap
        if add_fluid[0] < self.fluid_cap:
            self.fluids.clear()
            new_add_fluid = (fluidcap, add_fluid[1])
            self.fluids.append(new_add_fluid)
        self.reach = reach  # 1 per 10 pixels (?)
        self.leakage = 0  # leaks this much per turn
        self.temperature = 70
        self.meltable = melts
        self.cut = 1.0
        self.bash = 1.0
        self.puncture = 1.0

    def get_fluid_amt(self):
        fluid_total = 0
        for fl in self.fluids:
            fluid_total += fl[0]
        return fluid_total

    def remaining_fluid_space(self):
        return self.fluid_cap - self.get_fluid_amt()

    def change_fluid_amt(self, fluid_mat, amount):
        fl_id = 0
        chosen_fluid = None
        for fl in self.fluids:
            if fl[0] == fluid_mat:
                chosen_fluid = fl
                break
            fl_id += 1

        if chosen_fluid:
            self.fluids.remove(chosen_fluid)
            new_fluid = (chosen_fluid[0]+amount, fluid_mat)
        elif amount > 0:
            new_fluid = (amount, fluid_mat)
        else:
            return

        self.fluids.insert(fl_id, new_fluid)

    def combine_like_fluids(self):  # combining fluids of same material within a part
        fluid_id = random.randint(0, len(self.fluids) - 1)
        chosen_fluid = self.fluids[fluid_id]
        fl_id = 0
        second_fluid = None
        for fl in self.fluids:
            if fl[1] == chosen_fluid[1] and fluid_id != fl_id:
                second_fluid = fl
                break
            fl_id += 1

        if second_fluid:
            combined_fluid = (chosen_fluid[0] + second_fluid[0], chosen_fluid[1])
            self.fluids.remove(chosen_fluid)
            self.fluids.remove(second_fluid)
            self.fluids.append(combined_fluid)

