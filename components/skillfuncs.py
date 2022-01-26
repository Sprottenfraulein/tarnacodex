from library import maths
import random


def attack_default(realm, fate_rnd, pc, aimed_obj, skill_props, just_values=False):
    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    att_val_max += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    if just_values:
        return att_val_min, att_val_max
    if aimed_obj is None:
        return
    if maths.get_distance(pc.x_sq, pc.y_sq, aimed_obj.x_sq, aimed_obj.y_sq) > skill_props['range']:
        return

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    damage = rnd_attack * (100 - aimed_obj.stats['def_physical']) // 100 # reduce attack by percent of def
    aimed_obj.hp -= damage
    aimed_obj.check(realm, fate_rnd, pc)
