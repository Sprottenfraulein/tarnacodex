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