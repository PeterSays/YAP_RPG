import random
import pygame
from Material import Material, materials
from PhysObj import PhysObj
from Stats import Stats, new_stats


class Part(PhysObj):
    def __init__(self, body, partkind, rel_size=1.0, reach=5, alt_stat=None, alt_name=None,
                 critical=False, alt_mat=None, alt_fluid=None, melts=True, add_purpose=None):
        self.body = body  # does not attach automatically!
        if alt_stat:
            self.stats = alt_stat
        else:
            self.stats = Stats(body.stats.form_dict(), vary=3)
        self.partkind = partkind
        self.critical = critical
        self.turn_clock = 0
        self.connections = []
        self.purpose = []
        self.unpurpose = []  # purposes to treat as disabled
        if add_purpose:
            for p in add_purpose:
                self.purpose.append(p)
        self.on_front = False
        self.on_back = False
        self.part_mat = self.body.material
        self.part_fluid = self.body.biofluid
        if alt_mat:
            self.part_mat = alt_mat
        if alt_fluid:
            self.part_fluid = alt_fluid

        super().__init__(rel_size * self.body.volume, self.part_mat, melts=melts, reach=reach, add_fluid=(100, self.part_fluid))

        if partkind == 'hand':
            self.purpose.append('grasp')
            self.purpose.append('pet')
        elif partkind == 'leg':
            self.purpose.append('jump')
        elif partkind == 'head':
            self.purpose.append('eat')
            self.purpose.append('think')
            self.purpose.append('balance')
        elif partkind == 'core':
            self.purpose.append('metabolize')
            self.purpose.append('generate fluid')
            self.purpose.append('cycle fluid')

        max_nameval = 0
        if alt_name:
            if alt_name not in self.body.part_names:
                self.name = alt_name
            else:
                try:
                    int(self.name[-1])
                    suffix_num = int(self.name[self.name.find('#')+1:])
                    self.name = self.name[:self.name.find('#')] + str(suffix_num+1)
                except ValueError:
                    self.name += '#2'

        else:
            self.name = f'{partkind}'
            while self.name in self.body.part_names:
                if max_nameval:
                    self.name = f'{partkind}{max_nameval}'
                else:
                    self.name = f'{partkind}{max_nameval}'
                max_nameval += 1

    def attach(self, part):
        self.connections.append(part)
        part.connections.append(self)
        if self.body and not part.body:
            part.body = self.body

    def detach(self, part):
        self.connections.remove(part)
        part.connections.remove(self)
        if self.body and part not in self.body.attached_parts():
            if part in part.body.high_parts:
                part.body.high_parts.remove(part)
            elif part in part.body.mid_parts:
                part.body.mid_parts.remove(part)
            elif part in part.body.low_parts:
                part.body.low_parts.remove(part)
            part.body = None

    def cycle_fluids(self):
        total_fluid = 0
        parts_no = 0
        for part in self.body.attached_parts():
            parts_no += 1
            total_fluid += part.get_fluid_amt()
        avg_fluids = total_fluid / parts_no
        avg_comparison = {'less': [], 'more': []}
        for part in self.body.attached_parts():
            if part.get_fluid_amt() < avg_fluids:
                avg_comparison['less'].append(part)
            else:
                avg_comparison['more'].append(part)

        for more_part in avg_comparison['more']:
            if self.get_fluid_amt() < self.fluid_cap:
                their_fluid_mat = random.choice(more_part.fluids)[1]
                self.change_fluid_amt(their_fluid_mat, 1)
                more_part.change_fluid_amt(their_fluid_mat, -1)
        for less_part in avg_comparison['less']:
            if self.get_fluid_amt():
                my_fluid_mat = random.choice(self.fluids)[1]
                self.change_fluid_amt(my_fluid_mat, -1)
                less_part.change_fluid_amt(my_fluid_mat, 1)

    def metabolize(self):
        pass

    def routine(self):
        if len(self.fluids):
            self.combine_like_fluids()
            for flui in self.fluids:
                if flui[0] <= 0:
                    self.fluids.remove(flui)

        self.turn_clock += 1
        active_purpose = [purpose for purpose in self.purpose if purpose not in self.unpurpose]
        if 'cycle fluid' in active_purpose and self.turn_clock % self.body.cycle_interval:
            self.cycle_fluids()

        if 'metabolize' in active_purpose and self.turn_clock % self.body.metab_interval:
            self.metabolize()

        if 'generate fluid' in active_purpose and self.turn_clock % self.body.fluidgen_interval:
            if self.get_fluid_amt() < self.fluid_cap:
                self.change_fluid_amt(self.part_fluid, 1)


class Body:
    def __init__(self, ent, spritename, stats_dict=None,
                 lvl=1, frontside='right', volume=10000, base='humanoid',
                 material=materials['flesh'], biofluid=materials['blood']):
        self.turn = 0
        self.x = 0
        self.y = 0
        self.entity = ent
        self.lvl = lvl
        self.sprite = None
        self.spritename = spritename
        self.high_parts = []
        self.mid_parts = []
        self.low_parts = []
        self.part_names = []
        if not stats_dict:
            stats_dict = new_stats(self.lvl)
        self.stats = Stats(stats_dict, vary=3)
        self.legs_needed = 0
        self.wings_needed = 0
        self.material = material
        self.nutrition = 0
        self.digesting = []  # (volume, material)
        self.biofluid = biofluid
        self.cycle_interval = 1
        self.metab_interval = 50
        self.fluidgen_interval = 10
        self.frontside = frontside
        self.x_flipped = False
        self.y_flipped = False
        self.base = base
        self.volume = volume  # .001 gal per unit

        bodystatmods = None
        bodystatamts = None
        bodyvary = 3

        bodyschema = []
        with open(f'text/body_schematics/{self.spritename[:-4]}.txt', 'r') as bodyfile:
            total_lines = len(list(bodyfile))
            current_line = -1
            bodyfile.seek(0)
            file_text = bodyfile.read()
            file_lines = file_text.split('\n')
            for bf_line_ in file_lines:
                current_line += 1

                if bf_line_ == '':
                    continue

                if bf_line_[-1] != '\n':
                    bf_line = bf_line_
                else:
                    bf_line = bf_line_[:-1]

                if bf_line.startswith('base: '):
                    self.base = bf_line[6:]
                elif bf_line.startswith('frontside: '):
                    self.frontside = bf_line[11:]
                elif bf_line.startswith('volume: '):
                    self.volume = int(bf_line[8:])

                elif bf_line.startswith('core_mat: '):
                    self.material = materials[bf_line[10:]]
                elif bf_line.startswith('core_fluid: '):
                    self.biofluid = materials[bf_line[12:]]

                elif bf_line.startswith('core_mods: '):
                    if bf_line[-1] == '\n':
                        bodystatmods = eval(bf_line[11:-1])
                    else:
                        bodystatmods = eval(bf_line[11:])
                elif bf_line.startswith('core_amts: '):
                    if bf_line[-1] == '\n':
                        bodystatamts = eval(bf_line[11:-1])
                    else:
                        bodystatamts = eval(bf_line[11:])
                elif bf_line.startswith('core_vary: '):
                    bodyvary = int(bf_line[11:])
                else:
                    bodyschema.append(bf_line)

        bodystats = Stats(stats_dict, mods=bodystatmods, modamts=bodystatamts, vary=bodyvary)
        self.core = Part(self, 'core', critical=True, alt_stat=bodystats)

        if self.base == 'humanoid':
            head = Part(self, 'head', rel_size=0.23, reach=2, critical=True)
            self.attach(head, placement='hi')

            arm1 = Part(self, 'arm', rel_size=0.11, reach=6)
            arm2 = Part(self, 'arm', rel_size=0.11, reach=6)
            self.attach(arm1, placement='mid')
            self.attach(arm2, placement='mid')
            hand1 = Part(self, 'hand', rel_size=0.02, reach=1)
            hand2 = Part(self, 'hand', rel_size=0.02, reach=1)
            arm1.attach(hand1)
            arm2.attach(hand2)

            leg1 = Part(self, 'leg', rel_size=0.11, reach=5)
            leg2 = Part(self, 'leg', rel_size=0.11, reach=5)
            self.attach(leg1, placement='low')
            self.attach(leg2, placement='low')
            foot1 = Part(self, 'foot', rel_size=0.02, reach=2)
            foot2 = Part(self, 'foot', rel_size=0.02, reach=2)
            leg1.attach(foot1)
            leg2.attach(foot2)

        elif self.base == 'peterling':
            self.core.purpose.append('eat')
            self.core.purpose.append('think')
            self.core.purpose.append('balance')

            leg1 = Part(self, 'leg', rel_size=0.23, reach=4)
            leg2 = Part(self, 'leg', rel_size=0.23, reach=4)
            self.attach(leg1, placement='low')
            self.attach(leg2, placement='low')
            foot1 = Part(self, 'foot', rel_size=0.1, reach=3)
            foot2 = Part(self, 'foot', rel_size=0.1, reach=3)
            leg1.attach(foot1)
            leg2.attach(foot2)

            arm1 = Part(self, 'arm', rel_size=0.23, reach=4)
            arm2 = Part(self, 'arm', rel_size=0.23, reach=4)
            self.attach(arm1, placement='high')
            self.attach(arm2, placement='high')
            foot3 = Part(self, 'foot', rel_size=0.1, reach=3)
            foot4 = Part(self, 'foot', rel_size=0.1, reach=3)
            arm1.attach(foot3)
            arm2.attach(foot4)

        elif self.base == 'orb':
            self.core.purpose.append('eat')
            self.core.purpose.append('think')
            self.core.purpose.append('balance')

        base_parts = []
        base_parts.extend(self.low_parts)
        base_parts.extend(self.mid_parts)
        base_parts.extend(self.high_parts)

        for part in base_parts:
            self.part_names.append(part.name)

        added_parts = []
        readmode = 'neutral'

        part_kind = 'unknown'
        part_name = 'unnamed'
        other_purpose = None
        rem_partkind = None
        rem_place = None
        onfront = False
        onback = False
        place = 'mid'
        reach_ = 5
        relsize = 1.0
        altmat = None
        altfluid = None
        altstat = None
        is_critical = False
        last_part = None
        statmods = None
        statamts = None
        statvary = 3

        for bfline_ in bodyschema:
            if bfline_[-1] != '\n':
                bfline = bfline_
            else:
                bfline = bfline_[:-1]

            if readmode == 'neutral':
                if bfline.startswith('add_part: '):
                    readmode = 'add_part'
                    part_kind = bfline[10:]
                elif bf_line.startswith('rem_part: '):
                    readmode = 'rem_part'
                    rem_partkind = bfline[10:]
                elif bf_line.startswith('select_part: '):  # focuses on a part that matches parameters
                    sel_partkind = bfline[13:]             # for purposes of last_part attachment
                    if sel_partkind in ('hi', 'mid', 'low'):
                        if sel_partkind == 'hi':
                            lp_search = self.high_parts
                        elif sel_partkind == 'mid':
                            lp_search = self.mid_parts
                        elif sel_partkind == 'low':
                            lp_search = self.low_parts
                        else:
                            lp_search = self.low_parts

                        last_part = random.choice(lp_search)
                    else:  # match by partkind
                        lp_search = self.attached_parts()
                        for part in lp_search:
                            if part.partkind == sel_partkind:
                                last_part = part

            elif readmode == 'add_part':
                if bfline.startswith('add_part_end'):
                    readmode = 'neutral'
                    altstat = Stats(self.core.stats.form_dict(), vary=statvary, mods=statmods, modamts=statamts)
                    new_part = Part(self, part_kind, rel_size=relsize, critical=is_critical, reach=reach_,
                                    alt_mat=altmat, alt_stat=altstat, alt_name=part_name, alt_fluid=altfluid, add_purpose=[other_purpose])
                    self.part_names.append(new_part.name)
                    if not (last_part and place == 'last_part'):
                        self.attach(new_part, on_front=onfront, on_back=onback, placement=place)
                    else:
                        last_part.attach(new_part)

                    added_parts.append(new_part)
                    last_part = new_part

                    if True:  # kindly ignore these!
                        part_kind = 'unknown'
                        part_name = 'unnamed'
                        onfront = False
                        other_purpose = None
                        onback = False
                        place = 'mid'
                        reach_ = 5
                        relsize = 1.0
                        altmat = None
                        altstat = None
                        altfluid = None
                        is_critical = False
                        last_part = None
                        statmods = None
                        statamts = None
                        statvary = 3

                elif bfline.startswith('rel_size: '):
                    relsize = int(bfline[10:])
                elif bfline.startswith('reach: '):
                    reach_ = int(bfline[7:])
                elif bfline.startswith('on_front'):
                    onfront = True
                elif bfline.startswith('on_back'):
                    onback = True
                elif bfline.startswith('critical: '):
                    is_critical = bool(bfline[10:])
                elif bfline.startswith('alt_mat: '):
                    altmat = materials[bfline[9:]]
                elif bfline.startswith('alt_fluid: '):
                    altfluid = materials[bfline[11:]]
                elif bfline.startswith('placement: '):
                    place = bfline[11:]
                elif bfline.startswith('vary: '):
                    statvary = int(bfline[6:])
                elif bfline.startswith('name: '):
                    part_name = bfline[6:]
                elif bfline.startswith('purpose: '):
                    other_purpose = bfline[9:]
                elif bfline.startswith('stat_mods: '):
                    if bfline[-1] == '\n':
                        statmods = eval(bfline[11:-1])
                    else:
                        statmods = eval(bfline[11:])
                elif bfline.startswith('stat_amts: '):
                    if bfline[-1] == '\n':
                        statamts = eval(bfline[11:-1])
                    else:
                        statamts = eval(bfline[11:])

            elif readmode == 'rem_part':  # made for removing base parts. make sure bases can apply parts by themselves
                removed_part = None
                if bfline.startswith('rem_part_end'):
                    readmode = 'neutral'

                    if rem_place:
                        if rem_place == 'hi':
                            searchplace = self.high_parts
                        elif rem_place == 'mid':
                            searchplace = self.mid_parts
                        elif rem_place == 'low':
                            searchplace = self.low_parts
                        rem_place = None
                    else:
                        searchplace = self.attached_parts()

                    for part in searchplace:
                        if part.partkind == rem_partkind:
                            removed_part = part

                    if removed_part:
                        removed_part.detach(self.core)
                        self.part_names.remove(removed_part.name)

                    if True:
                        rem_partkind = None
                        rem_place = None

                elif bfline.startswith('placement: '):
                    rem_place = bfline[11:]

        has_legs = 0
        has_wings = 0
        for part in self.attached_parts():
            if part.partkind == 'leg':
                has_legs += 1
            elif part.partkind == 'wing':
                has_wings += 1

        self.wings_needed = has_wings
        self.legs_needed = has_legs

        self.high_capacity = len(self.high_parts)
        self.mid_capacity = len(self.mid_parts)
        self.low_capacity = len(self.low_parts)

    def load(self):
        self.sprite = pygame.image.load(f'sprite/portraits/{self.spritename}')

    def unload(self):
        self.sprite = None

    def attach(self, limb_base_part, on_front=False, on_back=False, placement='mid'):
        limb_base_part.on_front = on_front
        limb_base_part.on_back = on_back

        self.core.attach(limb_base_part)
        if placement == 'hi':
            self.high_parts.append(limb_base_part)
        elif placement == 'mid':
            self.mid_parts.append(limb_base_part)
        elif placement == 'low':
            self.low_parts.append(limb_base_part)

    def attached_parts(self):
        attached = [self.core]
        for part in self.core.connections:
            if part not in attached:
                attached.append(part)

            for conn_part in part.connections:
                if conn_part not in attached:
                    attached.append(conn_part)

        return attached

    def can_fly(self):
        has_wings = 0
        can_lev = False
        for part in self.attached_parts():
            if part.partkind == 'wing':
                has_wings += 1
            if 'levitate' in [purpose for purpose in part.purpose if purpose not in part.unpurpose]:
                can_lev = True

        if (has_wings >= self.wings_needed > 0) or can_lev:
            return True
        else:
            return False

    def turn(self):
        for part in self.attached_parts():
            part.routine()
