# game items object
from library import logfun
from objects import dbrequests
import random


class Treasure:
    def __init__(self, treasure_id, db_cursor, tile_sets, resources, audio, x_sq=-1, y_sq=-1, stashed=True, log=True):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = self.off_y = 0
        self.stashed = stashed

        treasure_dict = dbrequests.treasure_get_by_id(db_cursor, treasure_id)

        self.props = init_props(db_cursor, treasure_dict)

        # linking images and sounds
        images_update(db_cursor, self.props, tile_sets)

        sounds_update(db_cursor, self.props, audio)


def init_props(db_cursor, treasure_dicts):
    base_props, modifier_list, de_buff_list = treasure_dicts

    # adding container list
    base_props['container_max'] = base_props['container']
    if base_props['container_max'] > 0:
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
    for mod_dict in modifier_list:
        init_modifier(base_props, mod_dict)

    # inserting de_buffs
    for db_dict in de_buff_list:
        modifier_list = dbrequests.de_buff_get_mods(db_cursor, db_dict['de_buff_id'])

        for mod_dict in modifier_list:
            init_modifier(db_dict, mod_dict)

    base_props['de_buffs'] = de_buff_list

    base_props['affixes'] = []

    return base_props


def affix_add(db_cursor, loot_props, affix_dicts):
    base_props, modifier_list, de_buff_list = affix_dicts

    # inserting modifiers
    base_props['mods'] = {}
    for mod_dict in modifier_list:
        init_modifier(base_props, mod_dict)

    # inserting de_buffs
    for db_dict in de_buff_list:
        modifier_list = dbrequests.de_buff_get_mods(db_cursor, db_dict['de_buff_id'])

        for mod_dict in modifier_list:
            init_modifier(db_dict, mod_dict)

    base_props['de_buffs'] = de_buff_list

    loot_props['affixes'].append(base_props)


def init_modifier(parent_dict, mod_dict):
    parent_dict['mods'][mod_dict['parameter_name']] = {}
    mod_value_base = random.randrange(mod_dict['value_base_min'], mod_dict['value_base_max'] + 1)
    parent_dict['mods'][mod_dict['parameter_name']]['value_base'] = mod_value_base
    parent_dict['mods'][mod_dict['parameter_name']]['value_type'] = mod_dict['value_type']
    if mod_dict['value_spread_min'] is not None and mod_dict['value_spread_max'] is not None:
        mod_value_spread = random.randrange(mod_dict['value_spread_min'], mod_dict['value_spread_max'] + 1)
        parent_dict['mods'][mod_dict['parameter_name']]['value_spread'] = mod_value_spread


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
    for affix in loot_props['affixes']:
        try:
            if affix['mods'][stat_name]['value_type'] == 0:
                equating_modifier = affix['mods'][stat_name]['value_base']
            stat_sum += affix['mods'][stat_name]['value_base']
            stat_sum += random.randrange(0, affix['mods'][stat_name]['value_spread'] + 1)
        except KeyError:
            pass
    if equating_modifier is not None:
        return equating_modifier
    else:
        return stat_sum


def loot_validate(loot_props):
    try:
        loot_props['condition'] = min(loot_props['condition'], calc_loot_stat(loot_props, 'condition_max'))
    except KeyError:
        pass
    try:
        loot_props['charge'] = min(loot_props['charge'], calc_loot_stat(loot_props, 'charge_max'))
    except KeyError:
        pass
    try:
        loot_props['amount'] = min(loot_props['amount'], calc_loot_stat(loot_props, 'amount_max'))
    except KeyError:
        pass


def loot_calc_name(loot_props):
    full_name = [loot_props['label']]
    for affix in loot_props['affixes']:
        if affix['suffix'] == 1:
            full_name.append(affix['label'])
        else:
            full_name.insert(0, affix['label'])
    return ' '.join(full_name)


def images_update(db_cursor, loot_props, tile_sets):
    images_dict = dbrequests.treasure_images_get(db_cursor, loot_props['treasure_id'], loot_props['grade'])
    loot_props['image_inventory'] = tile_sets.get_image(images_dict[0]['tileset'],
                                                        (images_dict[0]['width'], images_dict[0]['height']),
                                                        (images_dict[0]['index'],))
    loot_props['image_floor'] = tile_sets.get_image(images_dict[1]['tileset'],
                                                        (images_dict[1]['width'], images_dict[1]['height']),
                                                        (images_dict[1]['index'],))


def sounds_update(db_cursor, loot_props, audio):
    sounds_dict = dbrequests.treasure_sounds_get(db_cursor, loot_props['treasure_id'], loot_props['grade'])
    try:
        loot_props['sound_drop'] = audio.bank_sounds[sounds_dict[0]]
        loot_props['sound_pickup'] = audio.bank_sounds[sounds_dict[1]]
        loot_props['sound_use'] = audio.bank_sounds[sounds_dict[2]]
        loot_props['sound_swing'] = audio.bank_sounds[sounds_dict[3]]
    except KeyError:
        pass


def calc_level(level, loot_props):
    loot_props['price_buy'] = loot_props['price_buy'] * level // loot_props['lvl']
    loot_props['price_sell'] = loot_props['price_sell'] * level // loot_props['lvl']
    for mod in loot_props['mods'].values():
        mod['value_base'] = mod['value_base'] * level // loot_props['lvl']
        try:
            mod['value_spread'] = mod['value_spread'] * level // loot_props['lvl'] // 4
        except KeyError:
            pass
    loot_props['lvl'] = level


def calc_grade(db_cursor, grade, loot_props):
    affix_ids = set()
    if grade >= 2:
        affix_ids.add(roll_affix(db_cursor, grade, loot_props, is_suffix=0))
    if grade >= 3:
        affix_ids.add(roll_affix(db_cursor, grade, loot_props, is_suffix=0))
    if grade > 0:
        affix_ids.add(roll_affix(db_cursor, grade, loot_props))
    for aff in affix_ids:
        affix_add(db_cursor, loot_props, dbrequests.affix_loot_get_by_id(db_cursor, aff))
    loot_props['grade'] = grade


def roll_affix(db_cursor, grade, loot_props, is_suffix=None):
    rnd_roll = random.randrange(0, 10001)
    affix_ids = dbrequests.get_affixes(db_cursor, loot_props['lvl'], grade, (loot_props['item_type'],), rnd_roll, is_suffix=is_suffix)
    final_roll = random.randrange(0, len(affix_ids))
    return affix_ids[final_roll]
