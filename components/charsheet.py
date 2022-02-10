# Player character game rules stats object.
from library import maths, itemlist
from components import dbrequests


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

        self.exp_rate = 1.6
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
            'prof_picklock': 0,    # in  tenths of percents (1000 is 100%)
            'prof_detect': 0,      # in  tenths of percents (1000 is 100%)
            'prof_disarm': 0,      # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_findgold': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findfood': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findammo': 0,    # in  tenths of percents (1000 is 100%)
            'prof_findore': 0,     # in  tenths of percents (1000 is 100%intelligence
            'prof_findmagic': 0,   # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_lore': 0,        # in  tenths of percents (1000 is 100%)
            'prof_trade': 0,       # in  tenths of percents (1000 is 100%)
            'prof_craft': 0,       # in  tenths of percents (1000 is 100%)
                                   # in  tenths of percents (1000 is 100%)
            'prof_bonusexp': 0,    # in  tenths of percents (1000 is 100%)
            'prof_range': 0        # in  tenths of percents (1000 is 100%)
        }
        # dictionary of stat alterations. pairs "stat: value" added during game.
        self.de_buffs = {}
        self.modifiers = {}
        # Inventory list
        self.inventory = itemlist.ItemList(items_max=24, all_to_none=True, filters={
            'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                           'orb_ammo', 'orb_source', 'use_wand', 'exp_lockpick', 'exp_tools', 'exp_food', 'light',
                           'aug_gem', 'sup_potion']
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

        self.hotbar = itemlist.ItemList(all_to_none=True, items_max=9, filters={
            'item_types': ['skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc', 'sup_potion',
                           'exp_food', 'exp_lockpick', 'exp_tools']
        })

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
        for eq_pos in self.equipped:
            for eq_itm in eq_pos:
                if eq_itm is None:
                    continue
                if stat_name in eq_itm.props['mods']:
                    mod_add = eq_itm.props['mods'][stat_name]['value_base']
                    if 'value_spread' in eq_itm.props['mods'][stat_name]:
                        mod_add += eq_itm.props['mods'][stat_name]['value_spread']
                    mod += self.condition_mod_rate(mod_add, eq_itm.props)
        return mod

    def condition_mod_rate(self, mod_add, item_props):
        if 'condition' in item_props:
            cond_percent = item_props['condition'] * 100 // item_props['condition_max']
            if cond_percent == 0:
                result = 0
            elif cond_percent <= 25:
                result = mod_add // 2
            else:
                result = mod_add
            return result
        else:
            return mod_add

    def buff_mod(self, stat_name):
        mod = 0
        for de_buff in self.de_buffs:
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

    def experience_get(self, wins_dict, pc, exp_value):
        self.experience += exp_value
        """wins_dict['realm'].schedule_man.task_add('realm_tasks', 1, wins_dict['realm'], 'spawn_realmtext',
                                                 ('new_txt', "%s exp" % exp_value,
                                                  (0, 0), (0, -24), 'sun', pc, (0,0), 30, 'large', 16, 0, 0))"""
        if not self.exp_prev_lvl <= self.experience < self.exp_next_lvl:
            old_level = self.level
            self.level = self.calc_level(self.experience)
            if self.level != old_level:
                self.calc_stats()
                if self.level > old_level:
                    self.hp_get(100, True)
                    self.mp_get(100, True)
                    wins_dict['realm'].schedule_man.task_add('realm_tasks', 1, wins_dict['realm'], 'spawn_realmtext',
                                                             ('new_txt', "LEVEL UP!",
                                                              (0, 0), (0, -24), 'fnt_celeb', pc, (0, -3), 60, 'large', 16, 0,
                                                              0.15))
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
            self.attributes[attr_name] = chartype_stats[attr_name] + round(max((chartype_stats[attr_name] - 10), 1) * (self.level - 1) * self.attr_rate)
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
        for df in ('def_fire', 'def_poison', 'def_ice', 'def_lightning', 'def_arcane'):
            self.defences[df] = self.calc_def_elemental(df)
        # Calculating proficiencies
        for prof_name in self.profs.keys():
            self.profs[prof_name] = chartype_stats[prof_name]
            self.profs[prof_name] = self.calc_prof(prof_name)

    def hp_get(self, value=100, percent=False):
        hp_mod = value
        if percent:
            hp_mod = round(self.pools['HP'] * value / 100)
            self.hp += hp_mod
        else:
            self.hp += value
        self.hp = min(self.hp, self.pools['HP'])
        self.hp = max(self.hp, 0)
        return hp_mod

    def mp_get(self, value=100, percent=False):
        mp_mod = value
        if percent:
            mp_mod = round(self.pools['MP'] * value / 100)
            self.mp += mp_mod
        else:
            self.mp += value
        self.mp = min(self.mp, self.pools['MP'])
        self.mp = max(self.mp, 0)
        return mp_mod

    def food_get(self, value=100, percent=False):
        food_mod = value
        if percent:
            food_mod = round(self.pools['FOOD'] * value / 100)
            self.food += food_mod
        else:
            self.food += value
        self.food = min(self.food, self.pools['FOOD'])
        self.food = max(self.food, 0)
        return food_mod

    # INVENTORY
    def inventory_search(self, item_type):
        found_list = []
        for itm in self.inventory:
            if itm is None:
                continue
            if itm.props['item_type'] == item_type:
                found_list.append(itm)
            elif 'container' in itm.props and itm.props['container'] is not None:
                found_list.extend(self.inventory_search(item_type))
        return found_list

    def inventory_search_by_id(self, item_id):
        found_list = []
        for itm in self.inventory:
            if itm is None:
                continue
            if itm.props['treasure_id'] == item_id:
                found_list.append(itm)
            elif 'container' in itm.props and itm.props['container'] is not None:
                found_list.extend(self.inventory_search_by_id(item_id))
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
