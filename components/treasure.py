# game items object
from library import logfun, pickrandom
from components import dbrequests, skill
import random


class Treasure:
    def __init__(self, treasure_id, lvl, db_cursor, tile_sets, resources, audio, fate_rnd, x_sq=-1, y_sq=-1,
                 mob_stats=None, grade=None, log=True):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = self.off_y = 0

        self.CONDITION_PENALTY_LEVEL = 250
        self.CONDITION_BROKEN_LEVEL = 0

        base_props, modifier_list, de_buff_list = dbrequests.treasure_get_by_id(db_cursor, treasure_id)

        if base_props['lvl'] is not None:
            calc_level(lvl, base_props, modifier_list, de_buff_list)

        self.props, add_price_expos = init_props(db_cursor, fate_rnd, base_props, modifier_list, de_buff_list)

        if grade is None:
            if mob_stats is not None and mob_stats['grade_set_loot'] is not None:
                calc_grade(db_cursor, mob_stats['grade_set_loot'], base_props, tile_sets, audio, fate_rnd)
            else:
                calc_grade(db_cursor, 1, base_props, tile_sets, audio, fate_rnd)
        else:
            self.props['grade'] = dbrequests.grade_get_by_id(db_cursor, 1)

        # Attaching a skill if an item is usable.
        if self.props['use_skill'] is not None:
            self.props['use_skill'] = skill.Skill(self.props['use_skill'], self.props['lvl'],
                                                  db_cursor, tile_sets, resources, audio)

        # Correcting price based on modifiers buffs and affixes
        item_expo_price(self.props, add_price_expos)

        # linking images and sounds
        images_update(db_cursor, self.props, tile_sets)

        sounds_update(db_cursor, self.props)

        loot_validate(self.props)


def init_props(db_cursor, fate_rnd, base_props, modifier_list, de_buff_list):
    # adding container list
    base_props['container_max'] = base_props['container']
    if base_props['container_max'] is not None and base_props['container_max'] > 0:
        base_props['container'] = []
    else:
        del base_props['container']

    if base_props['condition_max'] is not None:
        base_props['condition'] = random.randrange(base_props['condition_reduced_base'],
                                                   base_props['condition_reduced_base']
                                                   + base_props['condition_reduced_spread'] + 1)
    del base_props['condition_reduced_base']
    del base_props['condition_reduced_spread']

    if base_props['charge_max'] is not None:
        base_props['charge'] = random.randrange(base_props['charge_reduced_base'],
                                                base_props['charge_reduced_base']
                                                + base_props['charge_reduced_spread'] + 1)
    del base_props['charge_reduced_base']
    del base_props['charge_reduced_spread']

    if base_props['amount_max'] is not None:
        base_props['amount'] = random.randrange(base_props['amount_base'],
                                                base_props['amount_base']
                                                + base_props['amount_spread'] + 1)
    del base_props['amount_base']
    del base_props['amount_spread']

    # inserting modifiers
    base_props['mods'] = {}
    add_price_expos = []
    for mod_dict in modifier_list:
        add_price_expos.append(init_modifier(base_props, mod_dict, fate_rnd))

    # inserting de_buffs
    for db_dict in de_buff_list:
        modifier_list = dbrequests.de_buff_get_mods(db_cursor, db_dict['de_buff_id'])

        for mod_dict in modifier_list:
            add_price_expos.append(init_modifier(db_dict, mod_dict, fate_rnd))

    base_props['de_buffs'] = de_buff_list

    base_props['affixes'] = []

    return base_props, add_price_expos


def affix_add(db_cursor, loot_props, affix_dicts, fate_rnd):
    base_props, modifier_list, de_buff_list = affix_dicts

    # inserting modifiers
    base_props['mods'] = {}
    for mod_dict in modifier_list:
        init_modifier(base_props, mod_dict, fate_rnd)

    # inserting de_buffs
    for db_dict in de_buff_list:
        modifier_list = dbrequests.de_buff_get_mods(db_cursor, db_dict['de_buff_id'])

        for mod_dict in modifier_list:
            init_modifier(db_dict, mod_dict, fate_rnd)

    base_props['de_buffs'] = de_buff_list

    loot_props['affixes'].append(base_props)


def init_modifier(parent_dict, mod_dict, fate_rnd):
    parent_dict['mods'][mod_dict['parameter_name']] = {}
    mod_value_base = fate_rnd.expo_rnd(mod_dict['value_base_min'], mod_dict['value_base_max'])
    parent_dict['mods'][mod_dict['parameter_name']]['value_base'] = mod_value_base
    parent_dict['mods'][mod_dict['parameter_name']]['value_type'] = mod_dict['value_type']
    if mod_dict['value_spread_min'] is not None and mod_dict['value_spread_max'] is not None:
        mod_value_spread = fate_rnd.expo_rnd(mod_dict['value_spread_min'], mod_dict['value_spread_max'])
        parent_dict['mods'][mod_dict['parameter_name']]['value_spread'] = mod_value_spread
    else:
        mod_value_spread = 0

    per_base = mod_dict['value_base_min'] + (mod_dict['value_spread_min'] or 0) / 2
    mod_rolled = mod_value_base + mod_value_spread / 2 - per_base
    mod_max = (mod_dict['value_base_max'] + (mod_dict['value_spread_max'] or 0) / 2) - per_base
    if mod_max > 0:
        price_expo_rate = 1 + mod_rolled / mod_max
    else:
        price_expo_rate = 1
    return price_expo_rate


# USE ONLY FOR LOCAL ITEM PARAMETERS- IT DOES NOT TAKE CHARACTER STATS INTO CALCULATION!
def calc_loot_stat(loot_props, stat_name):
    # If the variable equating_modifier is set, stat value will be reset to it
    equating_modifier = None
    if stat_name in loot_props:
        stat_sum = loot_props[stat_name]
    else:
        stat_sum = 0
    try:
        if loot_props['mods'][stat_name]['value_type'] == 0:
            equating_modifier = loot_props['mods'][stat_name]['value_base']
        stat_sum += loot_props['mods'][stat_name]['value_base']
        stat_sum += random.randrange(0, loot_props['mods'][stat_name]['value_spread'] + 1)
    except KeyError:
        pass
    if stat_name not in ('def_physical',):  # Prevent char affixes from affecting item stats.
        for affix in loot_props['affixes']:
            try:
                if affix['mods'][stat_name]['value_type'] == 0:
                    equating_modifier = affix['mods'][stat_name]['value_base']
                elif affix['mods'][stat_name]['value_type'] == 2:
                    mod_percent = affix['mods'][stat_name]['value_base']
                    if 'value_spread' in affix['mods'][stat_name]:
                        random.randrange(0, affix['mods'][stat_name]['value_spread'] + 1)
                    stat_sum += stat_sum * mod_percent // 1000
                else:
                    stat_sum += affix['mods'][stat_name]['value_base']
                    stat_sum += random.randrange(0, affix['mods'][stat_name]['value_spread'] + 1)
            except KeyError:
                pass
    if stat_name not in ('condition', 'condition_max', 'charge', 'charge_max'):
        stat_sum = condition_mod_rate(stat_sum, loot_props)
    if equating_modifier is not None:
        return equating_modifier
    else:
        return stat_sum


def condition_mod_rate(mod_add, item_props):
    if 'condition' in item_props:
        cond_percent = item_props['condition'] * 100 // calc_loot_stat(item_props, 'condition_max')
        if cond_percent == 0:
            result = 0
        elif cond_percent <= 25:
            result = mod_add // 2
        else:
            result = mod_add
        return result
    else:
        return mod_add


def loot_validate(loot_props):
    try:
        loot_props['condition'] = min(loot_props['condition'], calc_loot_stat(loot_props, 'condition_max'))
        loot_props['condition'] = max(loot_props['condition'], 0)
    except KeyError:
        pass
    try:
        loot_props['charge'] = min(loot_props['charge'], calc_loot_stat(loot_props, 'charge_max'))
        loot_props['charge'] = max(loot_props['charge'], 0)
    except KeyError:
        pass
    try:
        loot_props['amount'] = min(loot_props['amount'], calc_loot_stat(loot_props, 'amount_max'))
        loot_props['amount'] = max(loot_props['amount'], 0)
    except KeyError:
        pass


def loot_calc_name(loot_props):
    full_name = [loot_props['label']]
    for affix in loot_props['affixes']:
        if affix['suffix'] == 1:
            full_name.append('of')
            full_name.append(affix['label'])
        else:
            full_name.insert(0, affix['label'])
    return ' '.join(full_name)


def images_update(db_cursor, loot_props, tile_sets):
    images_dict = dbrequests.treasure_images_get(db_cursor, loot_props['treasure_id'],
                                                 loot_props['grade']['grade_level'])
    if len(images_dict) == 0:
        images_dict = dbrequests.treasure_images_get(db_cursor, loot_props['treasure_id'], 0)

    try:
        loot_props['image_inventory'] = tile_sets.get_image(images_dict[0]['tileset'],
                                                        (images_dict[0]['width'], images_dict[0]['height']),
                                                        (images_dict[0]['index'],))
    except KeyError:
        pass
    try:
        loot_props['image_floor'] = tile_sets.get_image(images_dict[1]['tileset'],
                                                        (images_dict[1]['width'], images_dict[1]['height']),
                                                        (images_dict[1]['index'],))
    except KeyError:
        pass


def sounds_update(db_cursor, loot_props):
    sounds_dict = dbrequests.treasure_sounds_get(db_cursor, loot_props['treasure_id'],
                                                 loot_props['grade']['grade_level'])
    for snd in ('sound_drop', 'sound_pickup', 'sound_use', 'sound_swing'):
        if snd in sounds_dict:
            loot_props[snd] = sounds_dict[snd]
        else:
            loot_props[snd] = None


def calc_level(level, base_props, modifier_list, de_buff_list):
    base_props['price_buy'] = base_props['price_buy'] * level
    base_props['price_sell'] = base_props['price_sell'] * level
    for mod in modifier_list:
        if mod['value_scalable'] == 0:
            continue
        mod['value_base_min'] = mod['value_base_min'] * level
        mod['value_base_max'] = mod['value_base_max'] * level
        if mod['value_spread_min'] is None:
            continue
        mod['value_spread_min'] = mod['value_spread_min'] * level
        mod['value_spread_max'] = mod['value_spread_max'] * level
    base_props['lvl'] = level


def calc_grade(db_cursor, grade_set_loot, loot_props, tile_sets, audio, fate_rnd):
    if loot_props['lvl'] is None:
        lvl = 0
    else:
        lvl = loot_props['lvl']
    grade_list = dbrequests.grade_set_get(db_cursor, grade_set_loot, lvl)
    if len(grade_list) > 0:
        if len(grade_list) > 1:
            loot_props['grade'] = pickrandom.items_get([(grade, grade['roll_chance']) for grade in grade_list])[0]
        else:
            loot_props['grade'] = grade_list[0]
    else:
        loot_props['grade'] = None
        return

    if loot_props['grade']['affix_amount'] > 0:
        affix_ids = set()
        if loot_props['grade']['affix_amount'] >= 2:
            affix_ids.add(roll_affix(db_cursor, loot_props['grade']['grade_level'], loot_props, is_suffix=0))
        if loot_props['grade']['affix_amount'] >= 3:
            affix_ids.add(roll_affix(db_cursor, loot_props['grade']['grade_level'], loot_props, is_suffix=0))
        affix_ids.add(roll_affix(db_cursor, loot_props['grade']['grade_level'], loot_props))
        if None in affix_ids:
            affix_ids.remove(None)
        for aff in affix_ids:
            affix_add(db_cursor, loot_props, dbrequests.affix_loot_get_by_id(db_cursor, aff), fate_rnd)

    # images_update(db_cursor, loot_props, tile_sets)
    # sounds_update(db_cursor, loot_props)


def roll_affix(db_cursor, grade, loot_props, is_suffix=None):
    rnd_roll = random.randrange(0, 10001)
    affix_ids = dbrequests.get_affixes(db_cursor, loot_props['lvl'], grade, (loot_props['item_type'],), rnd_roll, is_suffix=is_suffix)
    if len(affix_ids) > 0:
        return random.choice(affix_ids)
    else:
        return None


def condition_equipment_change(char_sheet, value, socket=None):
    recalc_pc_stats = False
    for socket in char_sheet.equipped:
        for itm in socket:
            if itm is None:
                continue
            if 'condition' in itm.props:
                prev_cond = itm.props['condition']
                itm.props['condition'] += value
                loot_validate(itm.props)

                if (prev_cond > itm.CONDITION_PENALTY_LEVEL >= itm.props['condition']
                        or prev_cond > itm.CONDITION_BROKEN_LEVEL >= itm.props['condition']):
                    recalc_pc_stats = True
    return recalc_pc_stats


def item_expo_price(loot_props, add_price_expos):
    additional_price_buy = 0
    additional_price_sell = 0
    for ape in add_price_expos:
        additional_price_buy += loot_props['price_buy'] * (ape - 1)
        additional_price_sell += loot_props['price_sell'] * (ape - 1)
    loot_props['price_buy'] = int(round(loot_props['price_buy'] + additional_price_buy))
    loot_props['price_sell'] = int(round(loot_props['price_sell'] + additional_price_sell))


def charge_change(item, value):
    item.props['charge'] += value

    if item.props['charge'] <= 0:
        if item.props['vanish_empty'] == 1:
            return False
        else:
            item.props['charge'] = 0
    return True


def amount_change(item, value):
    item.props['amount'] += value

    if item.props['amount'] <= 0:
        if item.props['vanish_empty'] == 1:
            return False
        else:
            item.props['amount'] = 0
    return True