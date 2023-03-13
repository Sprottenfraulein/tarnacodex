from library import maths
from components import treasure, debuff, dbrequests, skill, textinserts, lootgen, maze, monster
from library import particle, calc2darray, pickrandom
import random


def attack_default(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-'
        else:
            return att_val_min, att_val_max

    only_from_hotbar_check(item_adress, pc, wins_dict)

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "Attack what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) - target.size > skill_obj.props['range']:
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_reqs_check(realm, skill_obj, pc):
        return False

    if not skill_costs_check(realm, skill_obj, pc):
        return False

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    target.wound(rnd_attack, 'att_physical', False, is_crit, wins_dict, fate_rnd, pc)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)
    # realm.pygame_settings.audio.sound(skill.props['sound_use'])
    if pc.char_sheet.equipped[2][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)
    elif pc.char_sheet.equipped[3][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[3][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def attack_powerful(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']
    att_rate = 2

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_fire')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    dam_min = att_val_min * 2
    dam_max = att_val_max * 2

    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-'
        else:
            return dam_min, dam_max, skill_obj.props['cost_mp']

    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "Attack what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True


    if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) - target.size > skill_obj.props['range']:
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    rnd_attack = random.randrange(att_val_min * att_rate, att_val_max * att_rate + 1)

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    target.wound(rnd_attack, 'att_fire', False, is_crit, wins_dict, fate_rnd, pc)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)
    # realm.pygame_settings.audio.sound(skill.props['sound_use'])
    realm.pygame_settings.audio.sound(skill_obj.props['sound_use'])
    realm.particle_list.append(particle.Particle((target.x_sq, target.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_dust_cloud')['default'], 16, speed_xy=(-0.25,-0.25)))

    return False


def attack_butterfly(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_lightning')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-'
        else:
            return att_val_min, att_val_max, skill_obj.props['cost_mp']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    for target in realm.mobs_short:
        if not target.alive:
            continue
        if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) - target.size <= skill_obj.props['range']:
            rnd_attack = random.randrange(att_val_min, att_val_max + 1)
            is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
            if is_crit:
                rnd_attack *= 4
            target.wound(rnd_attack, 'att_lightning', False, is_crit, wins_dict, fate_rnd, pc)

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-16, -16),
                               realm.animations.get_animation('effect_blood_swipe')['default'], 25))

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, None, skill_obj)
    realm.pygame_settings.audio.sound(skill_obj.props['sound_use'])
    return False


def shot_default(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-'
        else:
            return att_val_min, att_val_max

    only_from_hotbar_check(item_adress, pc, wins_dict)

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc):
        # skill_help(realm, skill_obj, 
        # 'new_txt', "Nothing to shoot with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if pc.char_sheet.equipped[2][0].props['class'] != pc.char_sheet.ammo_classes_dict[pc.char_sheet.equipped[3][0].props['class']]:
        skill_help(realm, skill_obj, 'new_txt', "Ammo won't fit.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    if not treasure.amount_change(pc.char_sheet.equipped[3][0], -1):
        pc.char_sheet.equipped[3][0] = None
        pc.char_sheet.calc_stats()
        wins_dict['realm'].spawn_realmtext(None, 'Out of ammo!', (0, 0), (0, -24),
                                           'fnt_celeb', pc, None, 240, 'def_bold', 24)
    wins_dict['inventory'].updated = True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    if pc.char_sheet.equipped[2][0].props['class'] == 'sling':
        anim_pack = (
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)},
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)}
        )
    else:
        anim_pack = (
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (0,)), 'timings': (60,)},
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (1,)), 'timings': (60,)}
        )
    speed = 0.5
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_physical', is_crit, pc),
                           speed, anim_pack, collision_limit=1, blast_radius=0)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)

    wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def shot_sniper(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']
    att_rate = 2

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_fire')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    dam_min = att_val_min * att_rate
    dam_max = att_val_max * att_rate
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-'
        else:
            return dam_min, dam_max, skill_obj.props['cost_mp']

    only_from_hotbar_check(item_adress, pc, wins_dict)

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc):
        # skill_help(realm, skill_obj,
        # 'new_txt', "Nothing to shoot with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if pc.char_sheet.equipped[2][0].props['class'] != pc.char_sheet.ammo_classes_dict[pc.char_sheet.equipped[3][0].props['class']]:
        skill_help(realm, skill_obj, 'new_txt', "Ammo won't fit.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    if not treasure.amount_change(pc.char_sheet.equipped[3][0], -1):
        pc.char_sheet.equipped[3][0] = None
        pc.char_sheet.calc_stats()
        wins_dict['realm'].spawn_realmtext(None, 'Out of ammo!', (0, 0), (0, -24),
                                           'fnt_celeb', pc, None, 240, 'def_bold', 24)
    wins_dict['inventory'].updated = True

    rnd_attack = random.randrange(att_val_min * att_rate, att_val_max * att_rate + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    if pc.char_sheet.equipped[2][0].props['class'] == 'sling':
        anim_pack = (
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)},
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)}
        )
    else:
        anim_pack = (
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (0,)), 'timings': (60,)},
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (1,)), 'timings': (60,)}
        )
    speed = 0.5
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_fire', is_crit, pc),
                           speed, anim_pack, collision_limit=1, blast_radius=0)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)

    wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def shot_multi(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']
    max_targets = 3 + pc.char_sheet.level // 10
    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_poison')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-', '-'
        else:
            return max_targets, att_val_min, att_val_max, skill_obj.props['cost_mp']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    if pc.char_sheet.equipped[2][0].props['class'] != pc.char_sheet.ammo_classes_dict[
        pc.char_sheet.equipped[3][0].props['class']]:
        skill_help(realm, skill_obj, 'new_txt', "Ammo won't fit.", (0, 0), (0, -24), None, pc, None, 120,
                   'def_bold', 24)
        return True

    shot = 0
    for target in realm.mobs_short:
        if shot == max_targets:
            break
        if not target.alive:
            continue
        if not realm.maze.flag_array[round(target.y_sq)][round(target.x_sq)].vis:
            continue
        if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) - target.size <= skill_obj.props['range']:
            shot += 1
            if not skill_reqs_check(realm, skill_obj, pc):
                break
            if pc.char_sheet.equipped[2][0].props['class'] != pc.char_sheet.ammo_classes_dict[
                pc.char_sheet.equipped[3][0].props['class']]:
                break
            if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (
                    skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
                continue
            if not skill_costs_check(realm, skill_obj, pc):
                break
            if not treasure.amount_change(pc.char_sheet.equipped[3][0], -1):
                pc.char_sheet.equipped[3][0] = None
                pc.char_sheet.calc_stats()
                wins_dict['realm'].spawn_realmtext(None, 'Out of ammo!', (0, 0), (0, -24),
                                                   'fnt_celeb', pc, None, 240, 'def_bold', 24)
            rnd_attack = random.randrange(att_val_min, att_val_max + 1)
            is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
            if is_crit:
                rnd_attack *= 4

            if pc.char_sheet.equipped[2][0].props['class'] == 'sling':
                anim_pack = (
                    {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)},
                    {'images': realm.tilesets.get_image('item_effects', (16, 16), (2,)), 'timings': (60,)}
                )
            else:
                anim_pack = (
                    {'images': realm.tilesets.get_image('item_effects', (16, 16), (0,)), 'timings': (60,)},
                    {'images': realm.tilesets.get_image('item_effects', (16, 16), (1,)), 'timings': (60,)}
                )
            speed = 0.5
            realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq),
                                   (rnd_attack, 'att_poison', is_crit, pc),
                                   speed, anim_pack, collision_limit=1, blast_radius=0)

    if shot == 0:
        skill_help(realm, skill_obj, 'new_txt', "No targets nearby.", (0, 0), (0, -24), None, pc, None, 120,
                   'def_bold', 24)
    else:
        pc.food_change(wins_dict, -5)
        wins_dict['inventory'].updated = True
        pc.act(wins_dict, None, skill_obj)
        realm.pygame_settings.audio.sound(skill_obj.props['sound_use'])

    return False


# TODO Spell skills.
def spell_magical_arrow(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']
    is_magic_item = item_adress[0][item_adress[1]] != skill_obj

    if is_magic_item:
        att_val_min, att_val_max = rods_damage_get(pc, item_adress[0][item_adress[1]].props['lvl'], fate_rnd)
    else:
        att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_arcane')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if is_magic_item:
            report = att_val_min, att_val_max
        elif not skill_reqs_check(realm, skill_obj, pc, is_magic_item):
            report = '-', '-', '-', '-'
        else:
            report = att_val_min, att_val_max, round(att_val_min * skill_obj.props['cost_mp']), round(att_val_max * skill_obj.props['cost_mp'])
        return report

    only_from_hotbar_check(item_adress, pc, wins_dict)

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc, is_magic_item):
        # skill_help(realm, skill_obj, 
        # 'new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    skill_sound = item_adress[0][item_adress[1]].props['sound_use']

    if not is_magic_item:
        if not skill_costs_check(realm, skill_obj, pc, rate=rnd_attack):
            return True
    elif not charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='This is it!'):
        skill_help(realm, skill_obj, 'new_txt', "No charges.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    anim_pack = (
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (12,)), 'timings': (60,)},
            {'images': realm.tilesets.get_image('item_effects', (16, 16), (13,)), 'timings': (60,)}
    )

    speed = 0.5
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_arcane', is_crit, pc),
                           speed, anim_pack, collision_limit=1, blast_radius=0)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)

    realm.pygame_settings.audio.sound(skill_sound)

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_vortex')['default'],
                                                 20))

    return False


def spell_fireball(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']
    att_rate = 2
    is_magic_item = item_adress[0][item_adress[1]] != skill_obj

    if is_magic_item:
        att_val_min, att_val_max = rods_damage_get(pc, item_adress[0][item_adress[1]].props['lvl'], fate_rnd)
    else:
        att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_fire')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    mp_cost_min = round(att_val_min * skill_obj.props['cost_mp'])
    mp_cost_max = round(att_val_max * skill_obj.props['cost_mp'])
    if just_values:
        if is_magic_item:
            report = att_val_min * att_rate, att_val_max * att_rate
        elif not skill_reqs_check(realm, skill_obj, pc, is_magic_item):
            report = '-', '-', '-', '-'
        else:
            report = att_val_min * att_rate, att_val_max * att_rate, mp_cost_min, mp_cost_max
        return report

    only_from_hotbar_check(item_adress, pc, wins_dict)

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            skill_help(realm, skill_obj, 'new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc, is_magic_item):
        # skill_help(realm, skill_obj, 
        # 'new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    rnd_attack = random.randrange(att_val_min * att_rate, att_val_max * att_rate + 1)
    skill_sound = item_adress[0][item_adress[1]].props['sound_use']

    if not is_magic_item:
        if not skill_costs_check(realm, skill_obj, pc, rate=rnd_attack // att_rate):
            return True
    elif not charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='This is it!'):
        skill_help(realm, skill_obj, 'new_txt', "No charges.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    image_pack = (
            realm.animations.get_animation('missile_fireball')['default'],
            realm.animations.get_animation('missile_fireball')['default']
    )
    speed = 0.25
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_fire', is_crit, pc),
                           speed, image_pack, collision_limit=1, blast_radius=2)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)

    realm.pygame_settings.audio.sound(skill_sound)

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_vortex')['default'],
                                                 20))

    return False


def spell_dispel(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    is_magic_item = item_adress[0][item_adress[1]] != skill_obj
    if just_values:
        report = skill_obj.props['cost_mp'], skill_obj.props['cost_gold']
        if not is_magic_item:
            return report
        else:
            return tuple()

    realm = wins_dict['realm']
    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc, is_magic_item):
        # skill_help(realm, skill_obj, 'new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
    try:
        flags = realm.maze.flag_array[y_sq][x_sq]
    except IndexError:
        return True
    if not flags.vis:
        return True
    pc_dist = maths.get_distance(realm.pc.x_sq, realm.pc.y_sq, x_sq, y_sq)
    if pc_dist > skill_obj.props['range'] or not calc2darray.path2d(
        realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
        (round(realm.pc.x_sq), round(realm.pc.y_sq)), 100, 10, r_max=10
    )[0]:
        skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.door is not None and flags.door.lock is not None and flags.door.lock.magical:
        pl_object = flags.door
    elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None and flags.obj.lock.magical:
        pl_object = flags.obj
    else:
        skill_help(realm, skill_obj, 'new_txt', "No magic here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    skill_level = item_adress[0][item_adress[1]].props['lvl']
    skill_sound = item_adress[0][item_adress[1]].props['sound_use']

    if not is_magic_item:
        if not skill_costs_check(realm, skill_obj, pc, rate=pl_object.lock.lvl):
            return True
    elif not charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='This is it!'):
        skill_help(realm, skill_obj, 'new_txt', "No charges.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if pl_object.lock.lvl > skill_level:
        skill_help(realm, skill_obj, 'new_txt', "The spell is beyond $n my comprehension!", (0, 0), (0, -24), None, pc, None,
                              120, 'def_bold', 24)
    else:
        exp = pl_object.lock.lvl * 100
        pc.char_sheet.experience_get(wins_dict, pc, pl_object.lock.lvl, exp)
        pl_object.lock = None
        pl_object.image_update()

    realm.particle_list.append(particle.Particle((pl_object.x_sq, pl_object.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_dust')['default'],
                                                 25))

    wins_dict['context'].end()
    realm.pygame_settings.audio.sound(skill_sound)
    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)

    return False


def repair(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        return skill_obj.props['cost_mp'], '10%'

    realm = wins_dict['realm']

    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc):
        # skill_help(realm, skill_obj, 'new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
    try:
        flags = realm.maze.flag_array[y_sq][x_sq]
    except IndexError:
        return True
    if not flags.vis:
        return True
    pc_dist = maths.get_distance(realm.pc.x_sq, realm.pc.y_sq, x_sq, y_sq)
    if pc_dist > skill_obj.props['range'] or not calc2darray.path2d(
            realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
            (round(realm.pc.x_sq), round(realm.pc.y_sq)), 100, 10, r_max=10
    )[0]:
        skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if len(flags.item) == 0:
        skill_help(realm, skill_obj, 'new_txt', "Nothing here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    item_repair = flags.item[-1]

    if (
            item_repair.props['item_type'] not in (
            'wpn_melee', 'wpn_ranged',  'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield', 'orb_source'
            ) or
            item_repair.props['condition'] <= 0 or
            item_repair.props['price_sell'] == 0
    ):
        skill_help(realm, skill_obj, 'new_txt', "Can't repair that!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    # Custom requirements check.
    if skill_obj.props['cost_mp'] > pc.char_sheet.mp and skill_obj.props['cost_mp'] > pc.autopower(wins_dict):
        skill_help(realm, skill_obj, 'new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    else:
        pc.char_sheet.mp_get(skill_obj.props['cost_mp'] * -1)
        realm.wins_dict['pools'].updated = True
    if item_repair.props['price_sell'] > pc.char_sheet.gold_coins:
        skill_help(realm, skill_obj, 'new_txt', "Not enough gold!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    else:
        pc.char_sheet.gold_coins += (item_repair.props['price_sell'] * -1)
        realm.wins_dict['inventory'].updated = True

    # TODO: Add resource spending for repairing.

    lvl_dif = pc.char_sheet.level - item_repair.props['lvl']
    sk = pc.char_sheet.profs['prof_craft'] + lvl_dif * 250  # 25% per level bonus/penalty
    rnd_roll = random.randrange(0, 1001)
    if rnd_roll == 1000 or rnd_roll - sk >= 500:
        item_repair.props['condition'] = max(0, item_repair.props['condition'] - 250)
        wins_dict['realm'].spawn_realmtext('new_txt', "I made it worse.", (0, 0), (0, -24), None, pc, None,
                                           120, 'def_bold', 24)
        pc.char_sheet.calc_stats()
        wins_dict['pools'].updated = True
        wins_dict['charstats'].updated = True
    elif rnd_roll == 0 or sk >= rnd_roll:
        item_repair.props['condition'] = treasure.calc_loot_stat(item_repair.props, 'condition_max')
        wins_dict['realm'].spawn_realmtext('new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120,
                                           'def_bold', 24)

        exp = item_repair.props['lvl'] * 10
        pc.char_sheet.experience_get(wins_dict, pc, item_repair.props['lvl'], exp)

        realm.particle_list.append(particle.Particle((item_repair.x_sq, item_repair.y_sq), (-4, -4),
                                                     realm.animations.get_animation('effect_arcane_dust')['default'],
                                                     20))
        pc.char_sheet.calc_stats()
        wins_dict['pools'].updated = True
        wins_dict['charstats'].updated = True
        wins_dict['realm'].spawn_realmtext('new_txt', '%s exp.' % (exp),
                                           (0, 0), (0, -24), 'sun', pc, (0, -2), 60, 'large', 16, 0,
                                           0.17)
    else:
        wins_dict['realm'].spawn_realmtext('new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120,
                                           'def_bold', 24)

    wins_dict['context'].end()
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)
    return False


def potion_heal(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    heal_hp_value = item_adress[0][item_adress[1]].props['mods']['hp_pool']['value_base']
    if just_values:
        return heal_hp_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='Potion finished!')

    pc.char_sheet.hp_get(heal_hp_value)
    wins_dict['pools'].updated = True
    wins_dict['context'].end()

    pc.add_cooldowns(wins_dict, 7)  # Cooldown for magical potion
    pc.act(wins_dict, None, skill_obj)

    return False


def potion_power(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    heal_mp_value = item_adress[0][item_adress[1]].props['mods']['mp_pool']['value_base']
    if just_values:
        return heal_mp_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='Potion finished!')

    pc.char_sheet.mp_get(heal_mp_value)
    wins_dict['pools'].updated = True
    wins_dict['context'].end()

    pc.add_cooldowns(wins_dict, 4)  # Cooldown for healing potion
    pc.act(wins_dict, None, skill_obj)

    return False


def eat(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    food_value = item_adress[0][item_adress[1]].props['mods']['food_pool']['value_base'] * skill_obj.props['lvl']
    if just_values:
        return food_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    charges_control(wins_dict, pc, item_adress[0][item_adress[1]], message='This is it!')

    pc.char_sheet.food_get(food_value)
    wins_dict['pools'].updated = True

    pc.act(wins_dict, None, skill_obj)

    return False


def picklock(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        lockpicks = pc.char_sheet.inventory_search('exp_lockpick')
        if len(lockpicks) == 0:
            return '-'
        lockpick, lockpick_mod = get_highest(lockpicks, 'prof_picklock')
        return (lockpick_mod + pc.char_sheet.profs['prof_picklock']) // 10

    realm = wins_dict['realm']
    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
    try:
        flags = realm.maze.flag_array[y_sq][x_sq]
    except IndexError:
        return True
    if not flags.vis:
        return True
    pc_dist = maths.get_distance(realm.pc.x_sq, realm.pc.y_sq, x_sq, y_sq)
    if pc_dist > skill_obj.props['range'] or not calc2darray.path2d(
            realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
            (round(realm.pc.x_sq), round(realm.pc.y_sq)), 100, 10, r_max=10
    )[0]:
        skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.door is not None and flags.door.lock is not None:
        pl_object = flags.door
    elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None:
        pl_object = flags.obj
    else:
        skill_help(realm, skill_obj, 'new_txt', "No locks here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill_obj == item.props['use_skill']:
        lockpick_mod = item_adress[0][item_adress[1]].props['mods']['prof_picklock']['value_base']
        lockpick = item_adress[0][item_adress[1]]
    else:
        lockpicks = pc.char_sheet.inventory_search('exp_lockpick')
        if len(lockpicks) == 0:
            skill_help(realm, skill_obj, 'new_txt', "I have no lockpicks!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        lockpick, lockpick_mod = get_highest(lockpicks, 'prof_picklock')

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    pl_result = pl_object.lock.unlock(wins_dict, pc, lockpick=lockpick, lockpick_mod=lockpick_mod)
    if pl_result:
        pl_object.lock = None
        pl_object.image_update()
    if lockpick.props['condition'] <= 0:
        pc.char_sheet.item_remove(wins_dict, lockpick)

    wins_dict['context'].end()

    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)

    return False


def disarm_trap(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        tools = pc.char_sheet.inventory_search('exp_tools')
        if len(tools) == 0:
            return '-'
        tool, tool_mod = get_highest(tools, 'prof_disarm')
        return (tool_mod + pc.char_sheet.profs['prof_disarm']) // 10

    realm = wins_dict['realm']
    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
    try:
        flags = realm.maze.flag_array[y_sq][x_sq]
    except IndexError:
        return True
    if not flags.vis:
        return True
    pc_dist = maths.get_distance(realm.pc.x_sq, realm.pc.y_sq, x_sq, y_sq)
    if pc_dist > skill_obj.props['range'] or not calc2darray.path2d(
            realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
            (round(realm.pc.x_sq), round(realm.pc.y_sq)), 100, 10, r_max=10
    )[0]:
        skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.trap is not None and flags.trap.visible == 1:
        trap = flags.trap
    elif flags.obj is not None and hasattr(flags.obj, 'trap') and flags.obj.trap is not None and flags.obj.trap.visible == 1:
        trap = flags.obj.trap
    elif flags.door is not None and flags.door.trap is not None and flags.door.trap.visible == 1:
        trap = flags.door.trap
    else:
        skill_help(realm, skill_obj, 'new_txt', "Seems no traps here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill_obj == item.props['use_skill']:
        tool_mod = item_adress[0][item_adress[1]].props['mods']['prof_disarm']['value_base']
        tool = item_adress[0][item_adress[1]]
    else:
        tools = pc.char_sheet.inventory_search('exp_tools')
        if len(tools) == 0:
            skill_help(realm, skill_obj, 'new_txt', "I have no tools!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        tool, tool_mod = get_highest(tools, 'prof_disarm')

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    if trap.mode != 1:
        skill_help(realm, skill_obj, 'new_txt', "The trap's safe!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    disarm_result = trap.disarm(wins_dict, pc, tool=tool, tool_mod=tool_mod)
    if disarm_result:
        trap.mode = 0
        trap.image_update()
    if tool.props['condition'] <= 0:
        pc.char_sheet.item_remove(wins_dict, tool)

    wins_dict['context'].end()

    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)

    return False


def dig(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    lvl_diff = 0
    if realm.maze:
        lvl_diff = item_adress[0][item_adress[1]].props['lvl'] - realm.maze.lvl
        hp_cost = skill_obj.props['cost_hp']
        if lvl_diff < 0:
            hp_cost += skill_obj.props['cost_hp'] * abs(lvl_diff)
    else:
        hp_cost = skill_obj.props['cost_hp']
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-'
        else:
            return hp_cost

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    rate = 1
    if lvl_diff < 0:
        rate += abs(lvl_diff)
    if not skill_costs_check(realm, skill_obj, pc, rate=rate):
        return True

    room_index = None
    for i in range(len(realm.maze.rooms)):
        if realm.maze.rooms[i].inside(pc.x_sq, pc.y_sq):
            room_index = i

    condition_cost = -10
    if lvl_diff < 0:
        condition_cost += lvl_diff * 10

    item_adress[0][item_adress[1]].props['condition'] += condition_cost
    if item_adress[0][item_adress[1]].props['condition'] <= 0:
        pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
        realm.pygame_settings.audio.sound('metal_pickup')
    elif room_index is None or room_index % 2 == 0:
        skill_help(realm, skill_obj, 'new_txt', "It' pointless!", (0, 0), (0, -24), None, pc, None,
                   120, 'def_bold', 24)
        realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    elif lvl_diff < -2:
        skill_help(realm, skill_obj, 'new_txt', "I barely scratched the surface!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        realm.pygame_settings.audio.sound('metal_pickup')
    else:
        realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
        # Digging roulette
        outcome = pickrandom.items_get((
            ('nothing', 20000),
            # Natural resources
            ('clay', 8000),
            # Extra
            ('scribble', 500),
            ('gold', 500),
            ('treasure', 500),
            ('monster', 500),
        ))[0]
        if outcome == 'nothing':
            skill_help(realm, skill_obj, 'new_txt', "No luck!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        elif outcome == 'clay':
            new_tr = treasure.Treasure(132, realm.maze.lvl, realm.db.cursor, realm.tilesets, realm.resources,
                                       realm.pygame_settings.audio, fate_rnd)
            lootgen.drop_loot(pc.x_sq, pc.y_sq, realm, (new_tr,))
            skill_help(realm, skill_obj, 'new_txt', "Ah, good!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        elif outcome == 'scribble':
            new_tr = treasure.Treasure(142, realm.maze.lvl, realm.db.cursor, realm.tilesets, realm.resources,
                                       realm.pygame_settings.audio, fate_rnd)
            rnd_roll = random.randrange(1, 10001)
            mans_list = [
                (mn, mn['roll_chance'])
                for mn in dbrequests.manuscript_get(realm.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'],
                                                    rnd_roll)
            ]
            if mans_list:
                new_tr.props['desc'] = textinserts.insert(realm, pc, pickrandom.items_get(mans_list, 1)[0]['desc'])
            lootgen.drop_loot(pc.x_sq, pc.y_sq, realm, (new_tr,))
            skill_help(realm, skill_obj, 'new_txt', "What's that?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        elif outcome == 'gold':
            new_gold = treasure.Treasure(
                6, realm.maze.lvl, realm.db.cursor,
                realm.tilesets, realm.resources, realm.pygame_settings.audio, fate_rnd
            )
            amount = new_gold.props['amount'] + new_gold.props['amount'] * 100 // 100
            new_gold.props['amount'] = round(
                amount * (treasure.SCALE_RATE_GOLD * (realm.maze.lvl * (realm.maze.lvl + 1) / 2)))
            new_gold.props['amount'] += (new_gold.props['amount'] * pc.char_sheet.profs['prof_findgold'] // 1000)
            # Level difference penalty
            new_gold.props['amount'] = round(
                new_gold.props['amount'] * (
                            1 - min(3, max(0, abs(realm.maze.lvl - pc.char_sheet.level) - 1)) * 0.25)
            )
            lootgen.drop_loot(pc.x_sq, pc.y_sq, realm, (new_gold,))
            skill_help(realm, skill_obj, 'new_txt', "Unexpected riches!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        elif outcome == 'treasure':
            treasure_list = []
            rnd_roll = random.randrange(1, 10001)
            """tr_ids_list = [
                (tr['treasure_id'], tr['roll_chance'])
                for tr in dbrequests.treasure_get(realm.db.cursor, realm.maze.lvl, rnd_roll, treasure_group=0)
            ]
            rnd_ids = pickrandom.items_get(tr_ids_list, 1, items_pop=True)"""
            tr_ids_list = [
                tr['treasure_id']
                for tr in dbrequests.treasure_get(realm.db.cursor, realm.maze.lvl,
                    random.randrange(1, 10001), treasure_group=0)
            ]
            rnd_ids = random.sample(tr_ids_list, min(1, len(tr_ids_list)))
            for rnd_id in rnd_ids:
                new_tr = treasure.Treasure(
                    rnd_id, realm.maze.lvl, realm.db.cursor, realm.tilesets, realm.resources,
                    realm.pygame_settings.audio, fate_rnd, findmagic=pc.char_sheet.profs['prof_findmagic']
                )
                treasure.loot_validate(new_tr.props)
                treasure_list.append(new_tr)

                # SPECIAL MANUSCRIPT STATEMENT
                if new_tr.props['item_type'] == 'misc_man':  # Manuscript item treasure_id
                    rnd_roll = random.randrange(1, 10001)
                    mans_list = [
                        (mn, mn['roll_chance'])
                        for mn in
                        dbrequests.manuscript_get(realm.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'],
                                                  rnd_roll)
                    ]
                    if len(mans_list) == 0:
                        del treasure_list[-1]
                    else:
                        new_tr.props['desc'] = textinserts.insert(realm, pc,
                                                                  pickrandom.items_get(mans_list, 1)[0]['desc'])
            lootgen.drop_loot(pc.x_sq, pc.y_sq, realm, treasure_list)
            skill_help(realm, skill_obj, 'new_txt', "I found something!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        elif outcome == 'monster':
            rnd_roll = random.randrange(1, 10001)
            mon_id = random.choice(dbrequests.get_monsters(realm.db.cursor, realm.maze.lvl, 0, None, rnd_roll))
            new_mon = dbrequests.monster_get_by_id(realm.db.cursor, mon_id)
            grade_list = dbrequests.grade_set_get(realm.db.cursor, new_mon['grade_set_monster'], realm.maze.lvl)
            if len(grade_list) > 0:
                if len(grade_list) > 1:
                    new_mon['grade'] = pickrandom.items_get([(grade, grade['roll_chance']) for grade in grade_list])[0]
                else:
                    new_mon['grade'] = grade_list[0]
            else:
                new_mon['grade'] = None
            del new_mon['grade_set_monster']
            maze.monster_apply_grade(realm.db, new_mon, realm.maze.lvl, fate_rnd)
            maze.scale_mob(new_mon, realm.maze.lvl, realm.maze)
            space_list = calc2darray.fill2d(realm.maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                            (round(pc.x_sq), round(pc.y_sq)), (round(pc.x_sq), round(pc.y_sq)), 2, 2, r_max=5)
            maze.mob_add(realm.maze, space_list[1][0], space_list[1][1], realm.animations, new_mon)
            skill_help(realm, skill_obj, 'new_txt', "Oh no!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            realm.shortlists_update(mobs=True)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, None, skill_obj)
    wins_dict['pools'].updated = True
    wins_dict['context'].end()

    return False


def craft(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    mp_cost = item_adress[0][item_adress[1]].props['lvl'] * skill_obj.props['cost_mp']
    gold_cost = item_adress[0][item_adress[1]].props['lvl'] * skill_obj.props['cost_gold']
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-'
        else:
            return mp_cost, gold_cost

    only_from_hotbar_check(item_adress, pc, wins_dict)

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
    try:
        flags = realm.maze.flag_array[y_sq][x_sq]
    except IndexError:
        return True
    if not flags.vis:
        return True
    pc_dist = maths.get_distance(realm.pc.x_sq, realm.pc.y_sq, x_sq, y_sq)
    if pc_dist > skill_obj.props['range'] or not calc2darray.path2d(
            realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
            (round(realm.pc.x_sq), round(realm.pc.y_sq)), 100, 10, r_max=10
    )[0]:
        skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    ingredient_list = flags.item[:]
    if len(ingredient_list) == 0:
        skill_help(realm, skill_obj, 'new_txt', "Nothing here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    gather_ingredients(realm.maze.flag_array, x_sq, y_sq, ingredient_list)
    in_work_list = []
    req_ingredient_list = dbrequests.get_recipe_ingredients(realm.db.cursor, item_adress[0][item_adress[1]].props['treasure_id'])
    for req_ing in req_ingredient_list:
        for ing in ingredient_list:
            if req_ing['ingredient_treasure_id'] == ing.props['treasure_id'] and ing not in in_work_list:
                ok = True
                """if ing.props['lvl'] and item_adress[0][item_adress[1]].props['lvl'] > ing.props['lvl']:
                    ok = False"""
                if req_ing['ingredient_amount'] and ing.props['amount'] < req_ing['ingredient_amount']:
                    ok = False
                elif req_ing['ingredient_charges'] and ing.props['charge'] < req_ing['ingredient_charges']:
                    ok = False
                elif req_ing['ingredient_condition'] and ing.props['condition'] < req_ing['ingredient_condition']:
                    ok = False
                if ok:
                    in_work_list.append(ing)
                    break
                else:
                    skill_help(realm, skill_obj, 'new_txt', "%s is no good!" % ing.props['label'],
                                          (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        else:
            skill_help(realm, skill_obj, 'new_txt', "Not enough ingredients!",
                                  (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            break
    else:
        # All components in place.
        if not skill_costs_check(realm, skill_obj, pc, rate=item_adress[0][item_adress[1]].props['lvl']):
            return True

        spent = False
        lvl_dif = min(1, pc.char_sheet.level - item_adress[0][item_adress[1]].props['lvl'])
        skill = pc.char_sheet.profs['prof_craft'] + lvl_dif * 250 + 300  # 25% per level penalty, 300 = base value
        rnd_roll = random.randrange(0, 1001)
        if rnd_roll == 1000 or rnd_roll - skill >= 500:
            skill_help(realm, skill_obj, 'new_txt', "Oh no!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            realm.sound_inrealm('fire_pickup', x_sq, y_sq, forced=True)
            realm.particle_list.append(particle.Particle((x_sq, y_sq), (-4, -4),
                                                         realm.animations.get_animation('effect_explosion')[
                                                             'default'], 25))
            spent = True
        elif rnd_roll == 0 or skill >= rnd_roll:
            result_lvl = min(
                max(1, sum(
                    [itm.props['lvl'] or item_adress[0][item_adress[1]].props['lvl'] for itm in in_work_list]
                ) // len(in_work_list)),
                item_adress[0][item_adress[1]].props['lvl']
            )
            results_list = dbrequests.get_recipe_result(realm.db.cursor,
                                                        item_adress[0][item_adress[1]].props['treasure_id'])
            treasure_list = []
            for tr_id in results_list:
                new_tr = treasure.Treasure(
                    tr_id, result_lvl, realm.db.cursor, realm.tilesets, realm.resources,
                    realm.pygame_settings.audio, fate_rnd, findmagic=pc.char_sheet.profs['prof_findmagic']
                )
                treasure.loot_validate(new_tr.props)
                treasure_list.append(new_tr)

                # SPECIAL MANUSCRIPT STATEMENT
                if new_tr.props['item_type'] == 'misc_man':  # Manuscript item treasure_id
                    rnd_roll = random.randrange(1, 10001)
                    mans_list = [
                        (mn, mn['roll_chance'])
                        for mn in
                        dbrequests.manuscript_get(realm.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'],
                                                  rnd_roll)
                    ]
                    if len(mans_list) == 0:
                        del treasure_list[-1]
                    else:
                        new_tr.props['desc'] = textinserts.insert(realm, pc,
                                                                  pickrandom.items_get(mans_list, 1)[0]['desc'])
            lootgen.drop_loot(x_sq, y_sq, realm, treasure_list)
            skill_help(realm, skill_obj, 'new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            realm.sound_inrealm('plate_pickup', x_sq, y_sq, forced=True)
            for itm in in_work_list:
                realm.particle_list.append(particle.Particle((round(itm.x_sq), round(itm.y_sq)), (-4, -4),
                                                             realm.animations.get_animation('effect_arcane_dust')[
                                                                 'default'], 25))
            spent = True
        else:
            skill_help(realm, skill_obj, 'new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            realm.sound_inrealm('plate_pickup', x_sq, y_sq, forced=True)
            spent = False

        if spent:
            for req_ing in req_ingredient_list:
                for ing in in_work_list:
                    if req_ing['ingredient_treasure_id'] == ing.props['treasure_id']:
                        if req_ing['expendable']:
                            realm.maze.flag_array[round(ing.y_sq)][round(ing.x_sq)].item.remove(ing)
                            realm.maze.loot.remove(ing)
                        else:
                            if req_ing['ingredient_amount']:
                                if not treasure.amount_change(ing, req_ing['ingredient_amount'] * -1):
                                    realm.maze.flag_array[round(ing.y_sq)][round(ing.x_sq)].item.remove(ing)
                                    realm.maze.loot.remove(ing)
                            if req_ing['ingredient_charges']:
                                if not treasure.charge_change(ing, req_ing['ingredient_charges'] * -1):
                                    realm.maze.flag_array[round(ing.y_sq)][round(ing.x_sq)].item.remove(ing)
                                    realm.maze.loot.remove(ing)
                            if req_ing['ingredient_condition']:
                                if not treasure.condition_change(ing, req_ing['ingredient_condition'] * -1):
                                    realm.maze.flag_array[round(ing.y_sq)][round(ing.x_sq)].item.remove(ing)
                                    realm.maze.loot.remove(ing)
                        in_work_list.remove(ing)
                        break

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, None, skill_obj)
    wins_dict['pools'].updated = True
    wins_dict['context'].end()
    return False


def pickup(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        return ()
    realm = wins_dict['realm']
    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    if no_aim:
        for i in range(round(pc.y_sq) - (skill_obj.props['range'] - 1),
                       round(pc.y_sq) + (skill_obj.props['range'] - 1) + 1):
            for j in range(round(pc.x_sq) - (skill_obj.props['range'] - 1),
                           round(pc.x_sq) + (skill_obj.props['range'] - 1) + 1):
                try:
                    flags = realm.maze.flag_array[i][j]
                except IndexError:
                    continue
                if flags.vis and len(flags.item) > 0 and calc2darray.path2d(realm.maze.flag_array, {'mov': False}, (j,i),
                                                 (round(pc.x_sq), round(pc.y_sq)), 100, 10, r_max=10)[0]:
                    x_sq, y_sq = j, i
                    break
            else:
                continue
            break
        else:
            skill_help(realm, skill_obj, 'new_txt', "Nothing here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return False
    else:
        x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
        try:
            flags = realm.maze.flag_array[y_sq][x_sq]
        except IndexError:
            return True
        if len(flags.item) == 0 or not flags.vis:
            return True
        if maths.get_distance(pc.x_sq, pc.y_sq, x_sq, y_sq) > skill_obj.props['range'] or not calc2darray.path2d(realm.maze.flag_array, {'mov': False}, (x_sq, y_sq),
                                                                                                                 (round(pc.x_sq), round(pc.y_sq)), 100, 10, r_max=10)[0]:
            skill_help(realm, skill_obj, 'new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True

    realm.coins_collect(pc.x_sq, pc.y_sq, radius=skill_obj.props['range'])
    for lt in flags.item[::-1]:
        for i in range(0, pc.char_sheet.inventory.items_max):
            if pc.char_sheet.inventory[i] is None:
                pc.char_sheet.inventory[i] = lt
                pc.moved_item_cooldown_check(pc.char_sheet.inventory[i], wins_dict['inventory'].inv_sockets_list[i])
                break
        else:
            return True

        realm.maze.flag_array[y_sq][x_sq].item.remove(lt)
        realm.maze.loot.remove(lt)
        # realm.loot_short.remove(lt)
        wins_dict['inventory'].updated = True
        realm.sound_inrealm(lt.props['sound_pickup'], x_sq, y_sq)
        break

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)
    wins_dict['context'].end()

    return False


def learn_skill(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        return ()
    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    try:
        new_skill_id = {
            95: 16,  # Repair skill
            96: 18,  # Ranged shot
            97: 19,  # Fireball spell
            98: 20,  # Butterfly skill
            99: 15,  # Dispel spell
            100: 5,  # Pick locks skill
            101: 6,   # Disarm skill
            105: 21,  # Powerful strike skill
            152: 24,  # Multishot skill
            153: 25  # Sniper Shot skill
        }[item_adress[0][item_adress[1]].props['treasure_id']]
    except KeyError:
        return True

    if item_adress[0][item_adress[1]].props['usable_%s' % pc.char_sheet.type] == 0:
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': '%s can not learn that.' % (pc.char_sheet.name, ),
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True
    new_skill = skill.Skill(new_skill_id, item_adress[0][item_adress[1]].props['lvl'], realm.db.cursor,
                            realm.tilesets, realm.resources, realm.pygame_settings.audio)
    if new_skill.props['lvl'] > pc.char_sheet.level:
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "%s is not experienced enough to use this item!" % pc.char_sheet.name.capitalize(),
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    for wnd in (pc.char_sheet.skills, pc.char_sheet.hotbar):
        for i in range(0, len(wnd)):
            sk = wnd[i]
            if sk is None or 'skill_id' not in sk.props:
                continue
            if sk.props['skill_id'] == new_skill.props['skill_id'] and sk.props['lvl'] <= new_skill.props['lvl']:
                wnd[i] = new_skill
                break
        else:
            continue
        break
    else:
        for i in range(0, len(pc.char_sheet.skills)):
            sk = pc.char_sheet.skills[i]
            if sk is None:
                pc.char_sheet.skills[i] = new_skill
                break
        else:
            skill_help(realm, skill_obj, 'new_txt', "I can't learn $n more skills!", (0, 0), (0, -24), None, pc, None, 120,
                                  'def_bold', 24)
            return True

    wins_dict['skillbook'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
    wins_dict['context'].end()
    skill_help(realm, skill_obj, 'new_txt', "I have learned a new Skill!", (0, 0), (0, -24), None, pc, None, 120,
                          'def_bold', 24)
    pc.act(wins_dict, None, skill_obj)

    return False


def skill_reqs_check(realm, skill_obj, pc, is_magic_item=False):
    """if pc.busy is not None:
        return False"""
    if skill_obj.cooldown_timer > 0:
        return False
    if is_magic_item:
        return True

    if skill_obj.props['item_type'] != 'skill_item' and (
        skill_obj.props['required_char_type'] not in (None, pc.char_sheet.type)
        or not pc.char_sheet.has_skill(skill_obj.props['skill_id'])
    ):
        skill_help(realm, skill_obj, 'new_txt', "I have no skills $n for this task!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    if (skill_obj.props['required_head'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[0],), skill_obj.props['required_head'])):
        return False
    if (skill_obj.props['required_chest'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[1],), skill_obj.props['required_chest'])):
        return False
    if (skill_obj.props['required_hand1'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[2],), skill_obj.props['required_hand1'])):
        return False
    if (skill_obj.props['required_hand2'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[3],), skill_obj.props['required_hand2'])):
        return False
    if (skill_obj.props['required_ring'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[4], pc.char_sheet.equipped[5]), skill_obj.props['required_ring'])):
        return False
    if (skill_obj.props['required_light'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[6],), skill_obj.props['required_light'])):
        skill_help(realm, skill_obj, 'new_txt', "I need some light!", (0, 0), (0, -24), None, pc, None, 120,
                              'def_bold', 24)
        return False

    return True


def skill_costs_check(realm, skill_obj, pc, rate=1):
    if skill_obj.props['cost_mp'] * rate > pc.char_sheet.mp and pc.autopower(realm.wins_dict) < skill_obj.props['cost_mp'] * rate:
        skill_help(realm, skill_obj, 'new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    elif skill_obj.props['cost_mp'] != 0:
        pc.char_sheet.mp_get(skill_obj.props['cost_mp'] * rate * -1)
        realm.wins_dict['pools'].updated = True

    if skill_obj.props['cost_hp'] * rate > pc.char_sheet.hp and pc.autoheal(realm.wins_dict) < skill_obj.props['cost_hp'] * rate:
        skill_help(realm, skill_obj, 'new_txt', "Not enough health!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    elif skill_obj.props['cost_hp'] != 0:
        pc.char_sheet.hp_get(skill_obj.props['cost_hp'] * rate * -1)
        realm.wins_dict['pools'].updated = True

    if skill_obj.props['cost_exp'] * rate > pc.char_sheet.experience:
        skill_help(realm, skill_obj, 'new_txt', "Not enough experience!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    elif skill_obj.props['cost_exp'] != 0:
        pc.char_sheet.experience_get(realm.wins_dict, pc, None, skill_obj.props['cost_exp'] * rate * -1)
        realm.wins_dict['pools'].updated = True
        realm.wins_dict['charstats'].updated = True

    if skill_obj.props['cost_gold'] * rate > pc.char_sheet.gold_coins:
        skill_help(realm, skill_obj, 'new_txt', "Not enough gold!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    elif skill_obj.props['cost_gold'] != 0:
        pc.char_sheet.gold_coins += (skill_obj.props['cost_gold'] * rate * -1)
        realm.wins_dict['inventory'].updated = True

    return True


def charges_control(wins_dict, pc, itm, message=None):
    if 'charge' in itm.props and itm.props['charge'] == 0:
        return False
    if not treasure.charge_change(itm, -1):
        pc.char_sheet.item_remove(wins_dict, itm)
        wins_dict['context'].end()
        if message is not None:
            wins_dict['realm'].spawn_realmtext(None, message, (0, 0), (0, -24),
                                               'fnt_celeb', pc, None, 240, 'def_bold', 24)
    else:
        wins_dict['inventory'].updated = True
        wins_dict['hotbar'].updated = True
    return True


def only_from_hotbar_check(item_adress, pc, wins_dict):
    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        wins_dict['dialogue'].launch(pc)
        return True


def rods_damage_get(pc, level, fate_rnd):
    rnd_attr = 12
    multiplier = rnd_attr + (rnd_attr - 10) * (level - 1) * pc.char_sheet.attr_rate
    base_dmg_min = 12 * level
    base_dmg_spread = 7 * level
    base_dmg_max = base_dmg_min + base_dmg_spread
    dmg_min = base_dmg_min + base_dmg_min * multiplier // 100
    dmg_max = base_dmg_max + base_dmg_max * multiplier // 100
    return dmg_min, dmg_max


def equipment_types_check(sockets, item_type):
    for socket in sockets:
        for itm in socket:
            if itm is None:
                continue
            if itm.props['item_type'] == item_type:
                return True
    return False


def get_highest(item_list, key):
    obj_max = item_list[0]
    obj_max_val = 0
    for itm in item_list:
        itm_val = treasure.calc_loot_stat(itm.props, key)
        if itm_val > obj_max_val:
            obj_max = itm
            obj_max_val = itm_val
    return obj_max, obj_max_val


def skill_help(realm, skill_obj, rt_id, caption, xy_sq, offset_xy, color=None, stick_obj=None, speed_xy=None,
               kill_timer=None, font='def_bold', size=24, frict_x=0, frict_y=0):
    if realm.last_skill != skill_obj:
        realm.last_skill = skill_obj
        realm.last_skill_timer = 60
        realm.spawn_realmtext(rt_id, caption, xy_sq, offset_xy, color=color, stick_obj=stick_obj, speed_xy=speed_xy,
                              kill_timer=kill_timer, font=font, size=size, frict_x=frict_x, frict_y=frict_y)


def gather_ingredients(flag_array, x_sq, y_sq, ingredient_list=None, r=5):
    if ingredient_list is None:
        ingredient_list = []
    offsets = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for off_x, off_y in offsets:
        try:
            items = flag_array[y_sq + off_y][x_sq + off_x].item
        except IndexError:
            continue
        if items:
            ingredient_list.extend(items)
            if r > 0:
                gather_ingredients(flag_array, x_sq + off_x, y_sq + off_y, ingredient_list, r=r-1)
    return ingredient_list
