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
            'attr_str': 0,
            'attr_dex': 0,
            'attr_con': 0,
            'attr_int': 0,
            'attr_wis': 0,
            'attr_cha': 0
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
            'att_base': [0, 0],
            'att_physical': 0,
            'att_fire': 0,
            'att_poison': 0,
            'att_ice': 0,
            'att_lightning': 0,
            'att_arcane': 0
        }
        self.defences = {
            'def_melee': 0,
            'def_ranged': 0,
            'def_physical': 0,
            'def_fire': 0,
            'def_poison': 0,
            'def_ice': 0,
            'def_lightning': 0,
            'def_arcane': 0
        }
        self.attack_speed = 0

        self.skills = {}

        self.profs = {
            'prof_provoke': 0,       # distance of mobs becoming aggressive
            'prof_evade': 0,         # avoid being hit by enemy
            'prof_crit': 0,          # chance of critical attack
            'prof_thorns': 0,        # in percents x10 (100% = 1000), returns all close damage to attacker.
            'prof_reflect': 0,       # in percents x10 (100% = 1000), returns all ranged damage to attacker.

            'prof_picklock': 0,      # open locked doors without keys
            'prof_detect': 0,        # make trap or hidden door visible
            'prof_disarm': 0,        # dismantle a trap

            'prof_findgold': 0,      # in percents x10 (100% = 1000), increases gold amounts dropped.
            'prof_findfood': 0,      # in percents x10 (100% = 1000), increases food amounts dropped.
            'prof_findammo': 0,      # in percents x10 (100% = 1000), increases ammo amounts dropped.
            'prof_findore': 0,       # number competes against ore deposit level x10 to successfully drop an ore. based on intelligence
            'prof_findmagic': 0,     # increases quality of drop items

            'prof_lore': 0,          # identify an item
            'prof_trade': 0,         # buy cheaper
            'prof_craft': 0,         # number competes against item difficulty to successfully craft. based on intelligence

            'prof_bonusexp': 0       # in percents x10 (100% = 1000), increases exp amounts received.
        }
        # dictionary of stat alterations. pairs "stat: value" added during game.
        self.de_buffs = {}
        self.modifiers = {}
        # Inventory list
        self.inventory = []
        self.inv_max = 24
        # Equipment dictionary
        self.eq_ids = (
            'head',
            'chest',
            'mainhand',
            'offhand',
            'ring1',
            'ring2',
            'ammo',
            'light'
        )
        self.equipped = [
            None, # 0 head
            None, # 1 chest
            None, # 2 mainhand
            None, # 3 offhand
            None, # 4 ring1
            None, # 5 ring2
            None, # 6 ammo
            None, # 7 light
        ]

        self.gold_coins = 1000

    def calc_hp(self):
        con_mods = self.equipment_mod('attr_con') + self.buff_mod('attr_con')
        try:
            con_mods += self.modifiers['attr_con']
        except KeyError:
            pass
        natural_hp = (self.attributes['attr_con'] + con_mods) * 2
        hp_mods = self.equipment_mod('HP') + self.buff_mod('HP')
        try:
            hp_mods += self.modifiers['HP']
        except KeyError:
            pass
        total_hp = natural_hp + hp_mods
        return total_hp

    def calc_mp(self):
        int_mods = self.equipment_mod('attr_int') + self.buff_mod('attr_int')
        try:
            int_mods += self.modifiers['attr_int']
        except KeyError:
            pass
        natural_mp = (self.attributes['attr_int'] + int_mods) * 2
        mp_mods = self.equipment_mod('MP') + self.buff_mod('MP')
        try:
            mp_mods += self.modifiers['MP']
        except KeyError:
            pass
        total_mp = natural_mp + mp_mods
        return total_mp

    def calc_attack_base(self, weapon=None):
        if weapon is not None:
            try:
                dmg_weapon_min, dmg_weapon_max = weapon['mods']['att_base']['value_base'], \
                                                 weapon['mods']['att_base']['value_base'] + weapon['mods']['att_base']['value_spread']
                weapon_type = weapon['item_type']
            except KeyError:
                dmg_weapon_min = dmg_weapon_max = 1
                weapon_type = 'wpn_melee'
        else:
            try:
                dmg_weapon_min, dmg_weapon_max = self.equipped[2]['mods']['att_base']['value_base'], \
                                                 self.equipped[2]['mods']['att_base']['value_base'] + self.equipped[2]['mods']['att_base']['value_spread']
                weapon_type = self.equipped[2]['item_type']
            except TypeError:
                dmg_weapon_min = dmg_weapon_max = 1
                weapon_type = 'wpn_melee'

        attr_multiplier = 1
        if weapon_type == 'wpn_melee':
            str_mods = self.equipment_mod('attr_str') + self.buff_mod('attr_str')
            try:
                str_mods += self.modifiers['attr_str']
            except KeyError:
                pass
            attr_multiplier = self.attributes['attr_str'] + str_mods
        elif weapon_type == 'wpn_ranged':
            dex_mods = self.equipment_mod('attr_dex') + self.buff_mod('attr_dex')
            try:
                dex_mods += self.modifiers['attr_dex']
            except KeyError:
                pass
            attr_multiplier = self.attributes['attr_dex'] + dex_mods
        elif weapon_type == 'wpn_magic':
            int_mods = self.equipment_mod('attr_int') + self.buff_mod('attr_int')
            try:
                int_mods += self.modifiers['attr_int']
            except KeyError:
                pass
            attr_multiplier = self.attributes['attr_int'] + int_mods
        attack_base_min, attack_base_max = dmg_weapon_min * attr_multiplier, dmg_weapon_max * attr_multiplier
        return attack_base_min, attack_base_max

    def calc_attack_mod(self, attack):
        dmg_mods = self.equipment_mod(attack) + self.buff_mod(attack)
        try:
            dmg_mods += self.modifiers[attack]
        except KeyError:
            pass
        total_mods = dmg_mods
        return total_mods

    def calc_defence_melee(self):
        str_mods = self.equipment_mod('attr_str') + self.buff_mod('attr_str')
        try:
            str_mods += self.modifiers['attr_str']
        except KeyError:
            pass
        natural_def = self.attributes['attr_str'] + str_mods
        def_mods = self.equipment_mod('def_melee') + self.buff_mod('def_melee')
        try:
            def_mods += self.modifiers['def_melee']
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_defence_ranged(self):
        dex_mods = self.equipment_mod('attr_dex') + self.buff_mod('attr_dex')
        try:
            dex_mods += self.modifiers['attr_dex']
        except KeyError:
            pass
        natural_def = self.attributes['attr_dex'] + dex_mods
        def_mods = self.equipment_mod('def_ranged') + self.buff_mod('def_ranged')
        try:
            def_mods += self.modifiers['def_ranged']
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_defence_physical(self):
        cha_mods = self.equipment_mod('attr_cha') + self.buff_mod('attr_cha')
        try:
            cha_mods += self.modifiers['attr_cha']
        except KeyError:
            pass
        natural_def = self.attributes['attr_cha'] + cha_mods
        def_mods = self.equipment_mod('def_physical') + self.buff_mod('def_physical')
        try:
            def_mods += self.modifiers['def_physical']
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_def_elemental(self, defence_id):
        wis_mods = self.equipment_mod('attr_wis') + self.buff_mod('attr_wis')
        try:
            wis_mods += self.modifiers['attr_wis']
        except KeyError:
            pass
        natural_def = self.attributes['attr_wis'] + wis_mods
        def_mods = self.equipment_mod(defence_id) + self.buff_mod(defence_id)
        try:
            def_mods += self.modifiers[defence_id]
        except KeyError:
            pass
        total_def = natural_def + def_mods
        return total_def

    def calc_prof(self, prof_id):
        prof_mods = self.equipment_mod(prof_id) + self.buff_mod(prof_id)
        try:
            prof_mods += self.modifiers[prof_id]
        except KeyError:
            pass
        total_prof = self.profs[prof_id] + prof_mods
        return total_prof

    def equipment_mod(self, stat_name):
        mod = 0
        for eq_item in self.equipped:
            if eq_item is None:
                continue
            try:
                mod += eq_item.props['mods'][stat_name]
            except KeyError:
                pass
        return mod

    def buff_mod(self, stat_name):
        mod = 0
        for de_buff in self.de_buffs:
            try:
                mod += de_buff['mods'][stat_name]
            except KeyError:
                pass
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
        self.attacks['att_base'] = self.calc_attack_base()
        for att in ('att_physical', 'att_fire', 'att_poison', 'att_ice', 'att_lightning', 'att_arcane'):
            self.attacks[att] = self.calc_attack_mod(att)
        # Calculating defences
        self.defences['def_melee'] = self.calc_defence_melee()
        self.defences['def_ranged'] = self.calc_defence_ranged()
        self.defences['def_physical'] = self.calc_defence_physical()
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
    def inventory_search(self, item_type):
        for itm in self.inventory:
            if itm is None:
                continue
            if itm.props['item_type'] == item_type:
                return itm
            elif 'container' in itm.props and itm.props['container'] is not None:
                con_itm = self.inventory_search(item_type)
                if con_itm:
                    return con_itm

    def inventory_remove(self, item_type):
        for itm in self.inventory[:]:
            if itm is None:
                continue
            if itm.props['item_type'] == item_type:
                self.inventory.remove(itm)
                return itm
            elif 'container' in itm.props and itm.props['container'] is not None:
                con_itm = self.inventory_remove(item_type)
                if con_itm:
                    return con_itm