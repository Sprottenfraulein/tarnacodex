# Player character game rules stats object.
from library import maths, itemlist
from components import dbrequests, treasure


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
            'FOOD': 1000
        }
        self.hp = 0
        self.mp = 0
        self.food = 1000

        self.exp_rate = 2.3
        self.exp_rate_multiplier = 100

        self.experience = 0
        self.exp_next_lvl = maths.exponential(self.exp_rate, 1, self.exp_rate_multiplier)
        self.exp_prev_lvl = 0

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
        self.att_def_dict = {
            'att_physical': 'def_physical',
            'att_fire': 'def_fire',
            'att_poison': 'def_poison',
            'att_ice': 'def_ice',
            'att_lightning': 'def_lightning',
            'att_arcane': 'def_arcane'
        }
        # self.attack_speed = 0
        self.ammo_classes_dict = {
            'stones': 'sling',
            'arrows': 'bow',
            'bolts': 'x-bow'
        }

        self.skills = itemlist.ItemList(items_max=36,  all_to_none=True, filters={
            'item_types': ['skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc']
        })

        self.profs = {
            'prof_provoke': 0,     # in  tenths of percents (1000 is 100%)
            'prof_evade': 0,       # in  tenths of percents (1000 is 100%)
            'prof_crit': 0,        # in  tenths of percents (1000 is 100%)
            'prof_thorns': 0,      # in  tenths of percents (1000 is 100%)
            'prof_reflect': 0,     # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_range': 0,       # in  tenths of percents (1000 is 100%)
            'prof_picklock': 0,    # in  tenths of percents (1000 is 100%)
            'prof_detect': 0,      # in  tenths of percents (1000 is 100%)
            'prof_disarm': 0,      # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_findgold': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findfood': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findammo': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findore': 0,     # in  tenths of percents (1000 is 100%intelligence
            'prof_findmagic': 0,   # in  tenths of percents (1000 is 100%)

            'prof_light': 0,       # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_lore': 0,        # in  tenths of percents (1000 is 100%)
            'prof_trade': 0,       # in  tenths of percents (1000 is 100%)
            'prof_craft': 0,       # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_bonusexp': 0    # in  tenths of percents (1000 is 100%)
        }
        # dictionary of stat alterations. pairs "stat: value" added during game.
        self.de_buffs = {}
        self.modifiers = {}
        # Inventory list
        self.inventory = itemlist.ItemList(items_max=24, all_to_none=True, filters={
            'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                           'orb_ammo', 'orb_source', 'use_wand', 'exp_lockpick', 'exp_tools', 'exp_food', 'exp_key',
                           'light', 'aug_gem', 'sup_potion', 'use_learn', 'misc_man', 'exp_res', 'use_craft']
        })
        # Equipment dictionary
        self.equipped = [
            # 0 head
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['arm_head'],
            }),
            # 1 chest
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['arm_chest'],
            }),
            # 2 mainhand
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic'],
            }),
            # 3 offhand
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['wpn_melee', 'orb_shield', 'orb_ammo', 'orb_source'],
            }),
            # 4 ring1
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['acc_ring'],
            }),
            # 5 ring2
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['acc_ring'],
            }),
            # 6 light
            itemlist.ItemList(all_to_none=True, items_max=1, filters={
                'item_types': ['light'],
            }),
        ]

        self.hotbar = itemlist.ItemList(all_to_none=True, items_max=12, filters={
            'item_types': ['skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc', 'sup_potion',
                           'exp_food', 'exp_lockpick', 'exp_key', 'exp_tools', 'use_learn', 'use_craft']
        })

        self.missions = {}

        self.gold_coins = 0
        self.base_light = 6


    def calc_attr(self, attr_id):
        attr_mods = self.equipment_mod(attr_id) + self.buff_mod(attr_id)
        try:
            attr_mods += self.modifiers[attr_id]
        except KeyError:
            pass
        total_attr = self.attributes[attr_id] + attr_mods
        return total_attr

    def calc_hp(self):
        natural_hp = self.calc_natural_hp()
        hp_mods = self.equipment_mod('HP') + self.buff_mod('HP')
        try:
            hp_mods += self.modifiers['HP']
        except KeyError:
            pass
        total_hp = natural_hp + hp_mods
        return total_hp

    def calc_natural_hp(self):
        con_mods = self.equipment_mod('attr_con') + self.buff_mod('attr_con')
        try:
            con_mods += self.modifiers['attr_con']
        except KeyError:
            pass
        return (self.attributes['attr_con'] + con_mods) * 2

    def calc_mp(self):
        natural_mp = self.calc_natural_mp()
        mp_mods = self.equipment_mod('MP') + self.buff_mod('MP')
        try:
            mp_mods += self.modifiers['MP']
        except KeyError:
            pass
        total_mp = natural_mp + mp_mods
        return total_mp

    def calc_natural_mp(self):
        int_mods = self.equipment_mod('attr_int') + self.buff_mod('attr_int')
        try:
            int_mods += self.modifiers['attr_int']
        except KeyError:
            pass
        return (self.attributes['attr_int'] + int_mods) * 2

    def calc_attack_base(self, weapon=None):
        if weapon is not None:
            try:
                dmg_weapon_min, dmg_weapon_max = weapon['mods']['att_base']['value_base'], \
                                                 weapon['mods']['att_base']['value_base'] + weapon['mods']['att_base']['value_spread']
                dmg_weapon_min = self.condition_mod_rate(dmg_weapon_min, weapon)
                dmg_weapon_max = self.condition_mod_rate(dmg_weapon_max, weapon)
                weapon_type = weapon['item_type']
            except KeyError:
                dmg_weapon_min = dmg_weapon_max = 1
                weapon_type = 'wpn_melee'
        else:
            mainhand = self.equipped[2][0]
            if mainhand is not None and 'mods' in mainhand.props and 'att_base' in mainhand.props['mods']:
                dmg_weapon_min, dmg_weapon_max = mainhand.props['mods']['att_base']['value_base'], \
                                                 mainhand.props['mods']['att_base']['value_base'] + mainhand.props['mods']['att_base']['value_spread']
                weapon_type = mainhand.props['item_type']
                dmg_weapon_min = self.condition_mod_rate(dmg_weapon_min, mainhand.props)
                dmg_weapon_max = self.condition_mod_rate(dmg_weapon_max, mainhand.props)
            else:
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
        attack_base_min, attack_base_max = dmg_weapon_min + dmg_weapon_min * attr_multiplier // 100, dmg_weapon_max + dmg_weapon_min * attr_multiplier // 100
        return attack_base_min, attack_base_max

    def calc_attack_mod(self, attack):
        dmg_mods = self.equipment_mod(attack) + self.buff_mod(attack)
        try:
            dmg_mods += self.modifiers[attack]
        except KeyError:
            pass
        return dmg_mods

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

    def calc_prof_mod(self, prof_id):
        prof_mods = self.equipment_mod(prof_id) + self.buff_mod(prof_id)
        try:
            prof_mods += self.modifiers[prof_id]
        except KeyError:
            pass
        return prof_mods

    def equipment_mod(self, stat_name):
        mod = 0
        for eq_pos in self.equipped:
            for eq_itm in eq_pos:
                if eq_itm is None:
                    continue
                if stat_name in eq_itm.props['mods']:
                    if eq_itm.props['item_type'] == 'orb_ammo' and not self.ammo_has_weapon(eq_itm.props):
                        continue
                    mod_add = eq_itm.props['mods'][stat_name]['value_base']
                    if 'value_spread' in eq_itm.props['mods'][stat_name]:
                        mod_add += eq_itm.props['mods'][stat_name]['value_spread']
                    mod += self.condition_mod_rate(mod_add, eq_itm.props)
                for aff in eq_itm.props['affixes']:
                    mod += self.eq_affix_mod(aff, stat_name)
                for de_buff in eq_itm.props['de_buffs']:
                    if stat_name in de_buff['mods']:
                        if de_buff['mods'][stat_name]['value_type'] in (1, 3):
                            mod += de_buff['mods'][stat_name]['value_base']
                        elif de_buff['mods'][stat_name]['value_type'] == 2:
                            base_stat = self.get_char_stat(stat_name)
                            mod += round(base_stat * de_buff['mods'][stat_name]['value_base'] / 1000)
                # mod_add = treasure.calc_loot_stat(eq_itm.props, stat_name)
                # mod += self.condition_mod_rate(mod, eq_itm.props)
        return mod

    def ammo_has_weapon(self, itm_props):
        weapon = self.equipped[2][0]
        if weapon is not None and  self.ammo_classes_dict[itm_props['class']] == weapon.props['class']:
            return True
        return False

    def eq_affix_mod(self, affix, stat_name):
        mod = 0
        if stat_name in affix['mods']:
            if affix['mods'][stat_name]['value_type'] in (1, 3):
                mod += affix['mods'][stat_name]['value_base']
            elif affix['mods'][stat_name]['value_type'] == 2:
                base_stat = self.get_char_stat(stat_name)
                mod += round(base_stat * affix['mods'][stat_name]['value_base'] / 1000)
        if 'de_buffs' in affix:
            for de_buff in affix['de_buffs']:
                if stat_name in de_buff['mods']:
                    if de_buff['mods'][stat_name]['value_type'] in (1, 3):
                        mod += de_buff['mods'][stat_name]['value_base']
                    elif de_buff['mods'][stat_name]['value_type'] == 2:
                        base_stat = self.get_char_stat(stat_name)
                        mod += round(base_stat * de_buff['mods'][stat_name]['value_base'] / 1000)
        return mod

    def get_char_stat(self, stat_name):
        for st_gr in (self.attributes, self.profs):
            if stat_name in st_gr:
                return st_gr[stat_name]
        if stat_name == 'def_physical':
            mod = 0
            for eq_pos in self.equipped:
                for eq_itm in eq_pos:
                    if eq_itm is None:
                        continue
                    if stat_name in eq_itm.props['mods']:
                        mod_add = eq_itm.props['mods'][stat_name]['value_base']
                        mod += self.condition_mod_rate(mod_add, eq_itm.props)
            return self.calc_attr('attr_cha') + mod
        elif stat_name in self.defences:
            return self.calc_attr('attr_wis')
        elif stat_name in self.attacks:
            return 0
        elif stat_name == 'HP':
            return self.calc_natural_hp()
        elif stat_name == 'MP':
            return self.calc_natural_mp()
        elif stat_name == 'FOOD':
            return 1000
        return 0

    def condition_mod_rate(self, mod_add, item_props):
        if 'condition' in item_props:
            cond_percent = item_props['condition'] * 100 // treasure.calc_loot_stat(item_props, 'condition_max')
            if cond_percent == 0:
                result = mod_add // 2
            else:
                result = mod_add
            return result
        else:
            return mod_add

    def buff_mod(self, stat_name):
        mod = 0
        for de_buff in self.de_buffs.values():
            if stat_name in de_buff['mods']:
                mod += de_buff['mods'][stat_name]['value_base']
                if 'value_spread' in de_buff['mods'][stat_name]:
                    mod += de_buff['mods'][stat_name]['value_spread']
        return mod

    def calc_all_mods(self, stat_name):
        mod_sum = self.equipment_mod(stat_name) + self.buff_mod(stat_name)
        try:
            mod_sum += self.modifiers[stat_name]
        except KeyError:
            pass
        return mod_sum

    def experience_get(self, wins_dict, pc, challenge_level, exp_value):
        exp_color = 'sun'
        level_diff = min(3, max(0, abs(pc.char_sheet.level - challenge_level) - 1))
        if challenge_level is not None:
            new_exp_value = round(exp_value - exp_value * (level_diff * 0.25))
        else:
            new_exp_value = exp_value
        if level_diff == 1:
            exp_color = 'fnt_header'
        if level_diff == 2:
            exp_color = 'fnt_muted'
        elif level_diff == 3:
            exp_color = 'bloody'
        if new_exp_value < 0:
            exp_color = 'bloody'
        self.experience += new_exp_value
        wins_dict['realm'].spawn_realmtext('new_txt', '%s exp.' % new_exp_value,
                                               (0, 0), (0, -24), exp_color, pc, (0, -2), 60, 'large', 16, 0,
                                               0.17)
        if not self.exp_prev_lvl <= self.experience < self.exp_next_lvl:
            old_level = self.level
            self.level = self.calc_level(self.experience)
            if self.level != old_level:
                self.calc_stats()
                if self.level > old_level:
                    self.hp_get(100, True)
                    self.mp_get(100, True)
                    wins_dict['realm'].spawn_realmtext('new_txt', "LEVEL UP!",
                                                      (0, 0), (0, -24), 'fnt_celeb', pc, (0, -3), 60, 'large', 18, 0,
                                                      0.15)
                    wins_dict['realm'].pygame_settings.audio.sound('level_up')
                return True
        return False

    def calc_level(self, exp_value):
        exp_value = 0
        level = 1
        for x in range(0, 101):
            exp_value += maths.exponential(self.exp_rate, x + 1, self.exp_rate_multiplier)
            level_value = x + 2
            if self.experience >= exp_value:
                level = level_value
                self.exp_prev_lvl = exp_value
                self.exp_next_lvl = exp_value + maths.exponential(self.exp_rate, x + 2, self.exp_rate_multiplier)
        return level

    def calc_stats(self):
        # First of all, calculating Attributes based on character type and level. Final alteration to these stats
        # (self.modifiers dictionary) will be made later and are not needed here.
        chartype_stats = dbrequests.char_params_get(self.db.cursor, 'characters', self.type)
        for attr_name in self.attributes.keys():
            attr_base = chartype_stats[attr_name] + round(max((chartype_stats[attr_name] - 10), 1) * (self.level - 1) * self.attr_rate)
            self.attributes[attr_name] = attr_base
        # Calculating pools
        self.pools['HP'] = self.calc_hp()
        self.pools['MP'] = self.calc_mp()
        # checking for exceeding values
        self.hp_get(0)
        self.mp_get(0)
        # Calculating attacks
        self.attacks['att_base'] = self.calc_attack_base()
        for att in ('att_physical', 'att_fire', 'att_poison', 'att_ice', 'att_lightning', 'att_arcane'):
            self.attacks[att] = self.calc_attack_mod(att)
        # Calculating defences
        self.defences['def_melee'] = self.calc_defence_melee()
        self.defences['def_ranged'] = self.calc_defence_ranged()
        self.defences['def_physical'] = self.calc_defence_physical()
        for df in ('def_fire', 'def_poison', 'def_ice', 'def_lightning', 'def_arcane'):
            self.defences[df] = self.calc_def_elemental(df)
        # Calculating proficiencies
        for prof_name in self.profs.keys():
            self.profs[prof_name] = chartype_stats[prof_name] + self.calc_prof_mod(prof_name)

    def hp_get(self, value=100, percent=False):
        hp_mod = value
        if percent:
            hp_mod = round(self.pools['HP'] * value / 100)
            self.hp += hp_mod
        else:
            self.hp += round(value)
        self.hp = min(self.hp, self.pools['HP'])
        # self.hp = max(self.hp, 0)
        return hp_mod

    def mp_get(self, value=100, percent=False):
        mp_mod = value
        if percent:
            mp_mod = round(self.pools['MP'] * value / 100)
            self.mp += mp_mod
        else:
            self.mp += round(value)
        self.mp = min(self.mp, self.pools['MP'])
        # self.mp = max(self.mp, 0)
        return mp_mod

    def food_get(self, value=100, percent=False):
        food_mod = value
        if percent:
            food_mod = round(self.pools['FOOD'] * value / 100)
            self.food += food_mod
        else:
            self.food += round(value)
        self.food = min(self.food, self.pools['FOOD'])
        self.food = max(self.food, 0)
        return food_mod

    # INVENTORY
    def inventory_search(self, item_type=None, item_class=None):
        found_list = []
        for itm in self.inventory:
            if itm is None:
                continue
            if item_type is not None and itm.props['item_type'] != item_type:
                continue
            if item_class is not None and itm.props['class'] != item_class:
                continue
            found_list.append(itm)
        return found_list

    def equipped_search(self, item_type=None, item_class=None):
        found_list = []
        for eq_pos in self.equipped:
            for itm in eq_pos:
                if itm is None:
                    continue
                if item_type is not None and itm.props['item_type'] != item_type:
                    continue
                if item_class is not None and itm.props['class'] != item_class:
                    continue
                found_list.append(itm)
        return found_list

    def inventory_search_by_id(self, item_id, level=None, amount=1):
        found_list = []
        for itm in self.inventory:
            if amount == 0:
                return found_list
            if itm is None:
                continue
            if itm.props['treasure_id'] == item_id:
                if level is None or itm.props['lvl'] is None or itm.props['lvl'] >= level:
                    found_list.append(itm)
                    if amount > 0:
                        amount -= 1
        return found_list

    def equipped_search_by_id(self, item_id):
        found_list = []
        for eq_pos in self.equipped:
            for itm in eq_pos:
                if itm is None:
                    continue
                if itm.props['treasure_id'] == item_id:
                    found_list.append(itm)
        return found_list

    def inventory_remove_by_id(self, item_id, level=None, amount=1):
        for i in range(0, len(self.inventory)):
            itm = self.inventory[i]
            if amount == 0:
                break
            if itm is None:
                continue
            if itm.props['treasure_id'] == item_id:
                if level is None or itm.props['lvl'] is None or itm.props['lvl'] >= level:
                    self.inventory[i] = None
                    if amount > 0:
                        amount -= 1

    def item_remove(self, wins_dict, item):
        if item in self.inventory:
            self.inventory[self.inventory.index(item)] = None
            wins_dict['inventory'].updated = True
            return True
        elif item in self.hotbar:
            self.hotbar[self.hotbar.index(item)] = None
            wins_dict['hotbar'].updated = True
            return True
        else:
            for socket in self.equipped:
                if item in socket:
                    socket[socket.index(item)] = None
                    wins_dict['inventory'].updated = True
                    return True
        return False

    def quest_item_remove(self, wins_dict):
        for i in range(len(self.inventory)-1, -1, -1):
            if self.inventory[i] is None:
                continue
            if 'quest_item' in self.inventory[i].props:
                self.inventory[i] = None
                wins_dict['inventory'].updated = True
        for i in range(len(self.hotbar)-1, -1, -1):
            if self.hotbar[i] is None:
                continue
            if 'quest_item' in self.hotbar[i].props:
                self.hotbar[i] = None
                wins_dict['hotbar'].updated = True
        for i in range(len(self.equipped)-1, -1, -1):
            if self.equipped[i][0] is None:
                continue
            if 'quest_item' in self.equipped[i][0].props:
                self.equipped[i][0] = None
                wins_dict['equipped'].updated = True

    def itemlists_clean_tail(self):
        """for i in range(len(self.skills) - 1, -1, -1):
            if self.skills[i] is None:
                del self.skills[i]
            else:
                break

        for i in range(len(self.inventory) - 1, -1, -1):
            if self.inventory[i] is None:
                del self.inventory[i]
            else:
                break"""
        pass

    def itemlist_cleanall_skills(self, wins_dict, pc):
        for i in range(len(self.skills) - 1, -1, -1):
            if self.skills[i] is None:
                del self.skills[i]

        skill_win = wins_dict['skillbook']
        for i in range(0, len(self.skills)):
            pc.moved_item_cooldown_check(self.skills[i], skill_win.skb_sockets_list[i])

        for i in range(len(self.skills), self.skills.items_max):
            self.skills.append(None)
        pass

    def itemlist_cleanall_inventory(self, wins_dict, pc):
        for i in range(len(self.inventory) -1, -1, -1):
            if self.inventory[i] is None:
                del self.inventory[i]

        inv_win = wins_dict['inventory']
        for i in range(0, len(self.inventory)):
            pc.moved_item_cooldown_check(self.inventory[i], inv_win.inv_sockets_list[i])

        for i in range(len(self.inventory), self.inventory.items_max):
            self.inventory.append(None)
        pass

    def has_skill(self, skill_id):
        for wnd in (self.skills, self.hotbar):
            for i in range(0, len(wnd)):
                sk = wnd[i]
                if not sk or 'skill_id' not in sk.props:
                    continue
                if sk.props['skill_id'] == skill_id:
                    return True
        return False

    def missions_check(self, wins_dict, pc):
        missions_updated = False
        available_missions = dbrequests.mission_get(self.db.cursor, self.level, pc.location[0]['chapter_id'],
                                                    pc.location[1], self.type)
        for i in range(0, len(available_missions)):
            new_mission = available_missions.pop()
            for req_id in new_mission['reqs']:
                if req_id not in self.missions or 'complete' not in self.missions[req_id]:
                    break
            else:
                if new_mission['mission_id'] not in self.missions:
                    self.missions[new_mission['mission_id']] = new_mission
                    new_mission['lvl'] = pc.char_sheet.level
                    missions_updated = True
                elif (self.missions[new_mission['mission_id']]['once'] == 0
                      and 'complete' in self.missions[new_mission['mission_id']]
                      and self.missions[new_mission['mission_id']]['complete'] >=
                      self.missions[new_mission['mission_id']]['lvl'] != pc.char_sheet.level):
                    self.missions[new_mission['mission_id']]['lvl'] = pc.char_sheet.level
                    missions_updated = True
        if missions_updated:
            wins_dict['tasks'].restart()
            wins_dict['realm'].spawn_realmtext('new_txt', "There are the new Tasks!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
        return missions_updated

    def mission_task_check(self, mission):
        for tr_id, amount in mission['tasks']:
            if len(self.inventory_search_by_id(tr_id, mission['lvl'], amount)) < amount:
                return False
        for tr_id, amount in mission['tasks']:
            self.inventory_remove_by_id(tr_id, mission['lvl'], amount)
        return True
