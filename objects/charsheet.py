# Player character game rules stats object.
from library import maths
from objects import dbrequests


class CharSheet:
    def __init__(self, db, chr_id, chr_name='Xenia', chr_type='champion', chr_level=1):
        self.db = db
        self.id = chr_id

        self.name = chr_name
        self.type = chr_type
        self.level = chr_level

        self.attributes = {
            'STR': 0,
            'DEX': 0,
            'CON': 0,
            'INT': 0,
            'WIS': 0,
            'CHA': 0
        }
        self.attr_rate = 1

        self.pools = {
            'HP': 0,
            'MP': 0,
            'FOOD': 0
        }
        self.hp = 0
        self.mp = 0
        self.food = 0
        self.experience = 0
        self.exp_next_lvl = 0

        self.exp_rate = 1.4
        self.exp_rate_multiplier = 100

        self.attacks = {
            'att_melee': 0,
            'att_ranged': 0,
            'att_fire': 0,
            'att_poison': 0,
            'att_ice': 0,
            'att_lightning': 0,
            'att_arcane': 0
        }
        self.defences = {
            'def_melee': 0,
            'def_ranged': 0,
            'def_fire': 0,
            'def_poison': 0,
            'def_ice': 0,
            'def_lightning': 0,
            'def_arcane': 0
        }

        self.profs = {
            'provoke': 0,       # distance of mobs becoming aggressive
            'evade': 0,         # avoid being hit by enemy
            'crit': 0,          # chance of critical attack
            'thorns': 0,        # in percents x10 (100% = 1000), returns all close damage to attacker.
            'reflect': 0,       # in percents x10 (100% = 1000), returns all ranged damage to attacker.

            'picklock': 0,      # open locked doors without keys
            'detect': 0,        # make trap or hidden door visible
            'disarm': 0,        # dismantle a trap

            'findgold': 0,      # in percents x10 (100% = 1000), increases gold amounts dropped.
            'findfood': 0,      # in percents x10 (100% = 1000), increases food amounts dropped.
            'findammo': 0,      # in percents x10 (100% = 1000), increases ammo amounts dropped.
            'findore': 0,       # number competes against ore deposit level x10 to successfully drop an ore. based on intelligence
            'findmagic': 0,     # increases quality of drop items

            'lore': 0,          # identify an item
            'trade': 0,         # buy cheaper
            'craft': 0,         # number competes against item difficulty to successfully craft. based on intelligence

            'bonusexp': 0       # in percents x10 (100% = 1000), increases exp amounts received.
        }
        # dictionary of stat alterations. pairs "stat: value" added during game.
        self.modifiers = {}
        # Inventory list
        self.inventory = []
        # Equipment dictionary
        self.equipped = {
            'head': None,
            'chest': None,
            'mainhand': None,
            'offhand': None,
            'ring1': None,
            'ring2': None,
            'ammo': None,
            'light': None
        }

    def calc_hp(self):
        con_mods = self.equipment_mod('CON', self.attributes['CON']) + self.buff_mod('CON', self.attributes['CON'])
        try:
            con_mods += self.modifiers['CON']
        except KeyError:
            pass
        natural_hp = (self.attributes['CON'] + con_mods) * 2
        hp_mods = self.equipment_mod('HP', natural_hp) + self.buff_mod('HP', natural_hp)
        try:
            hp_mods += self.modifiers['HP']
        except KeyError:
            pass
        total_hp = natural_hp + hp_mods
        return total_hp

    def calc_mp(self):
        int_mods = self.equipment_mod('INT', self.attributes['INT']) + self.buff_mod('INT', self.attributes['INT'])
        try:
            int_mods += self.modifiers['INT']
        except KeyError:
            pass
        natural_mp = (self.attributes['INT'] + int_mods) * 2
        mp_mods = self.equipment_mod('MP', natural_mp) + self.buff_mod('MP', natural_mp)
        try:
            mp_mods += self.modifiers['MP']
        except KeyError:
            pass
        total_mp = natural_mp + mp_mods
        return total_mp

    def calc_attack_melee(self):
        str_mods = self.equipment_mod('STR', self.attributes['STR']) + self.buff_mod('STR', self.attributes['STR'])
        try:
            str_mods += self.modifiers['STR']
        except KeyError:
            pass
        natural_dmg = self.attributes['STR'] + str_mods
        dmg_mods = self.equipment_mod('att_melee', natural_dmg) + self.buff_mod('att_melee', natural_dmg)
        try:
            dmg_mods += self.modifiers['att_melee']
        except KeyError:
            pass
        total_dmg = natural_dmg + dmg_mods
        return total_dmg

    def calc_attack_ranged(self):
        dex_mods = self.equipment_mod('DEX', self.attributes['DEX']) + self.buff_mod('DEX', self.attributes['DEX'])
        try:
            dex_mods += self.modifiers['DEX']
        except KeyError:
            pass
        natural_dmg = self.attributes['DEX'] + dex_mods
        dmg_mods = self.equipment_mod('att_ranged', natural_dmg) + self.buff_mod('att_ranged', natural_dmg)
        try:
            dmg_mods += self.modifiers['att_ranged']
        except KeyError:
            pass
        total_dmg = natural_dmg + dmg_mods
        return total_dmg

    def calc_attack_elemental(self, attack_id):
        int_mods = self.equipment_mod('INT', self.attributes['INT']) + self.buff_mod('INT', self.attributes['INT'])
        try:
            int_mods += self.modifiers['INT']
        except KeyError:
            pass
        natural_dmg = self.attributes['INT'] + int_mods
        dmg_mods = self.equipment_mod(attack_id, natural_dmg) + self.buff_mod(attack_id, natural_dmg)
        try:
            dmg_mods += self.modifiers[attack_id]
        except KeyError:
            pass
        total_dmg = natural_dmg + dmg_mods
        return total_dmg

    def calc_defence_melee(self):
        str_mods = self.equipment_mod('STR', self.attributes['STR']) + self.buff_mod('STR', self.attributes['STR'])
        try:
            str_mods += self.modifiers['STR']
        except KeyError:
            pass
        natural_def = self.attributes['STR'] + str_mods
        def_mods = self.equipment_mod('def_melee', natural_def) + self.buff_mod('def_melee', natural_def)
        try:
            def_mods += self.modifiers['def_melee']
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_defence_ranged(self):
        dex_mods = self.equipment_mod('DEX', self.attributes['DEX']) + self.buff_mod('DEX', self.attributes['DEX'])
        try:
            dex_mods += self.modifiers['DEX']
        except KeyError:
            pass
        natural_def = self.attributes['DEX'] + dex_mods
        def_mods = self.equipment_mod('def_ranged', natural_def) + self.buff_mod('def_ranged', natural_def)
        try:
            def_mods += self.modifiers['def_ranged']
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_def_elemental(self, defence_id):
        wis_mods = self.equipment_mod('WIS', self.attributes['WIS']) + self.buff_mod('WIS', self.attributes['WIS'])
        try:
            wis_mods += self.modifiers['WIS']
        except KeyError:
            pass
        natural_def = self.attributes['WIS'] + wis_mods
        def_mods = self.equipment_mod(defence_id, natural_def) + self.buff_mod(defence_id, natural_def)
        try:
            def_mods += self.modifiers[defence_id]
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_prof(self, prof_id):
        prof_mods = self.equipment_mod(prof_id, self.profs[prof_id]) + self.buff_mod(prof_id, self.profs[prof_id])
        try:
            prof_mods += self.modifiers[prof_id]
        except KeyError:
            pass
        total_prof = self.profs[prof_id] + prof_mods
        return total_prof

    def equipment_mod(self, stat_name, stat_value):
        # checking equipped items for modifiers for provided stat
        mod = 0
        return mod

    def buff_mod(self, stat_name, stat_value):
        # checking active buffs and debuffs for modifiers for provided stat
        mod = 0
        return mod

    def experience_get(self, exp_value):
        self.experience += exp_value
        old_level = self.level
        self.level = self.calc_level(self.experience)
        if self.level != old_level:
            self.calc_stats()

    def calc_level(self, exp_value):
        exp_value = 0
        level = 1
        for x in range(0, 101):
            exp_value += maths.exponential(self.exp_rate, x, self.exp_rate_multiplier)
            level_value = x + 2
            if self.experience >= exp_value:
                level = level_value
        return level

    def calc_stats(self):
        # First of all, calculating Attributes based on character type and level. Final alteration to these stats
        # (self.modifiers dictionary) will be made later and are not needed here.
        chartype_stats = dbrequests.char_params_get(self.db.cursor, 'characters', self.type)
        for attr_name in self.attributes.keys():
            self.attributes[attr_name] = chartype_stats[attr_name] + round(chartype_stats[attr_name] * (self.level - 1) * self.attr_rate)
        # Calculating pools
        self.pools['HP'] = self.calc_hp()
        self.pools['MP'] = self.calc_mp()
        # Calculating attacks
        self.attacks['att_melee'] = self.calc_attack_melee()
        self.attacks['att_ranged'] = self.calc_attack_ranged()
        for att in ('att_fire', 'att_poison', 'att_ice', 'att_lightning', 'att_arcane'):
            self.attacks[att] = self.calc_attack_elemental(att)
        # Calculating defences
        self.defences['def_melee'] = self.calc_defence_melee()
        self.defences['def_ranged'] = self.calc_defence_ranged()
        for att in ('def_fire', 'def_poison', 'def_ice', 'def_lightning', 'def_arcane'):
            self.attacks[att] = self.calc_def_elemental(att)
        # Calculating proficiencies
        for prof_name in self.profs.keys():
            self.profs[prof_name] = chartype_stats[prof_name]
            self.profs[prof_name] = self.calc_prof(prof_name)

    def hp_get(self, value=100, percent=True):
        hp_mod = value
        if percent:
            hp_mod = round(self.pools['HP'] * value / 100)
            self.hp = hp_mod
        else:
            self.hp += value
        self.hp = min(self.hp, self.pools['HP'])
        return hp_mod

    def mp_get(self, value=100, percent=True):
        mp_mod = value
        if percent:
            mp_mod = round(self.pools['MP'] * value / 100)
            self.mp = mp_mod
        else:
            self.mp += value
        self.mp = min(self.mp, self.pools['MP'])
        return mp_mod

    def food_get(self, value=100, percent=True):
        food_mod = value
        if percent:
            food_mod = round(self.pools['FOOD'] * value / 100)
            self.food = food_mod
        else:
            self.food += value
        self.food = min(self.food, self.pools['FOOD'])
        return food_mod

    # INVENTORY
    def inventory_search(self, item_id):
        for itm in self.inventory:
            if itm['id'] == item_id:
                return itm
            elif 'container' in itm and itm['container']:
                con_itm = self.inventory_search(item_id)
                if con_itm:
                    return con_itm

    def inventory_remove(self, item_id):
        for itm in self.inventory[:]:
            if itm['id'] == item_id:
                self.inventory.remove(itm)
                return itm
            elif 'container' in itm and itm['container']:
                con_itm = self.inventory_remove(item_id)
                if con_itm:
                    return con_itm