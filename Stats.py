import random


def new_stats(lvl=1, vary=0, neg_ok=False, zero_ok=False):
    sd = {'STR': lvl, 'CON': lvl, 'DEX': lvl, 'AGI': lvl, 'INT': lvl, 'WIS': lvl, 'CHA': lvl}
    if vary:
        for stat in sd.keys():
            added = sd[stat] + random.randint(vary * -1, vary)
            if (added > 0 or neg_ok) and (added != 0 or zero_ok):
                sd[stat] = added

    return sd

class Stats:
    def __init__(self, stats_dict: dict, vary=0, neg_ok=False, mods=None, modamts=None):
        '''
        :param mods: ['STR', 'CON', 'INT']
        :param modamts: [(1.5, 2.0), (1.3, 1.8), (0.4, 0.7)] where (min, max)
        '''
        stat_dict = stats_dict.copy()
        if vary:
            for stat in stat_dict.keys():
                added = stat_dict[stat] + random.randint(vary*-1, vary)
                if added > 0 or neg_ok:
                    stat_dict[stat] += added

        if mods and modamts:
            ma_length = len(modamts)
            current_mod = 0
            for stat_modded in mods:
                if current_mod <= ma_length-1:
                    amount_range = modamts[current_mod]
                else:
                    amount_range = modamts[ma_length-1]
                min_change = amount_range[0]*100
                max_change = amount_range[1]*100
                amount_change = random.randint(min_change, max_change)
                stat_dict[stat_modded] = stat_dict[stat_modded] * (amount_change/100)

        self.stat_dict = stat_dict
        self.strength = stat_dict['STR']
        self.constitution = stat_dict['CON']
        self.dexterity = stat_dict['DEX']
        self.agility = stat_dict['AGI']
        self.intelligence = stat_dict['INT']
        self.wisdom = stat_dict['WIS']
        self.charisma = stat_dict['CHA']

    def form_dict(self):
        sd = self.stat_dict.copy()
        return sd

