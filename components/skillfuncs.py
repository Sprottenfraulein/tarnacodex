from library import maths
from components import treasure, debuff, dbrequests, skill
from library import particle, calc2darray
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

    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "Attack what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) > skill_obj.props['range']:
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    damage = rnd_attack * (100 - target.stats['def_physical']) // 100  # reduce attack by percent of def

    target.wound(damage, 'att_physical', False, is_crit, wins_dict, fate_rnd, pc)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)
    # realm.pygame_settings.audio.sound(skill.props['sound_use'])
    if pc.char_sheet.equipped[2][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)
    elif pc.char_sheet.equipped[3][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[3][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def attack_butterfly(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-'
        else:
            return att_val_min, att_val_max, skill_obj.props['cost_mp'] * skill_obj.props['lvl']

    if not skill_reqs_check(realm, skill_obj, pc):
        return True

    if not skill_costs_check(realm, skill_obj, pc, rate=skill_obj.props['lvl']):
        return True

    for target in realm.mobs_short:
        if round(maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq), 1) <= skill_obj.props['range']:
            rnd_attack = random.randrange(att_val_min, att_val_max + 1)
            damage = rnd_attack * (100 - target.stats['def_physical']) // 100  # reduce attack by percent of def
            is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
            if is_crit:
                rnd_attack *= 4
            target.wound(damage, 'att_physical', False, is_crit, wins_dict, fate_rnd, pc)

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_blood_swipe')['default'],
                                                 20))

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, None, skill_obj)
    # realm.pygame_settings.audio.sound(skill.props['sound_use'])
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

    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc):
        # realm.spawn_realmtext(
        # 'new_txt', "Nothing to shoot with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if pc.char_sheet.equipped[2][0].props['class'] != pc.char_sheet.ammo_classes_dict[pc.char_sheet.equipped[3][0].props['class']]:
        realm.spawn_realmtext('new_txt', "Ammo won't fit.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
        wins_dict['inventory'].updated = True
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
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_physical', is_crit, pc),
                           speed, anim_pack, collision_limit=1, blast_radius=0)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill_obj)

    wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


# TODO Spell skills.
def spell_magical_arrow(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_arcane')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-', '-'
        else:
            return att_val_min, att_val_max, round(att_val_min * skill_obj.props['cost_mp']), round(att_val_max * skill_obj.props['cost_mp'])

    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc):
        # realm.spawn_realmtext(
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

    if not skill_costs_check(realm, skill_obj, pc, rate=rnd_attack):
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

    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_vortex')['default'],
                                                 20))

    return False


def spell_fireball(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_fire')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    fb_dam_min = att_val_min * 2
    fb_dam_max = att_val_max * 2
    mp_cost_min = att_val_min * skill_obj.props['cost_mp']
    mp_cost_max = att_val_max * skill_obj.props['cost_mp']
    if just_values:
        if not skill_reqs_check(realm, skill_obj, pc):
            return '-', '-', '-', '-'
        else:
            return fb_dam_min, fb_dam_max, mp_cost_min, mp_cost_max

    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "I have to aim.", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    """if not skill_reqs_check(realm, skill, pc):
        return True"""
    if not skill_reqs_check(realm, skill_obj, pc):
        # realm.spawn_realmtext(
        # 'new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24
        # )
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill_obj.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    rnd_attack = random.randrange(fb_dam_min, fb_dam_max + 1)

    if not skill_costs_check(realm, skill_obj, pc, rate=rnd_attack):
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

    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])

    realm.particle_list.append(particle.Particle((pc.x_sq, pc.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_vortex')['default'],
                                                 20))

    return False


def spell_dispel(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        return skill_obj.props['cost_mp'], skill_obj.props['cost_gold']

    realm = wins_dict['realm']
    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    if not skill_reqs_check(realm, skill_obj, pc):
        # realm.spawn_realmtext('new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
        realm.spawn_realmtext('new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.door is not None and flags.door.lock is not None and flags.door.lock.magical:
        pl_object = flags.door
    elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None and flags.obj.lock.magical:
        pl_object = flags.obj
    else:
        realm.spawn_realmtext('new_txt', "No magic here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    if pl_object.lock.lvl > pc.char_sheet.level:
        realm.spawn_realmtext('new_txt', "The spell is beyond $n my comprehension!", (0, 0), (0, -24), None, pc, None,
                              120, 'def_bold', 24)
        return False

    if not skill_costs_check(realm, skill_obj, pc, rate=pl_object.lock.lvl):
        return True

    exp = pl_object.lock.lvl * 100
    pc.char_sheet.experience_get(wins_dict, pc, exp)
    pl_object.lock = None
    pl_object.image_update()

    realm.particle_list.append(particle.Particle((pl_object.x_sq, pl_object.y_sq), (-4, -4),
                                                 realm.animations.get_animation('effect_arcane_dust')['default'],
                                                 20))

    wins_dict['context'].end()
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)

    return False


def repair(wins_dict, fate_rnd, pc, skill_obj, item_adress, no_aim=False, just_values=False):
    if just_values:
        return skill_obj.props['cost_mp'], '10%'

    realm = wins_dict['realm']

    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

    if not skill_reqs_check(realm, skill_obj, pc):
        # realm.spawn_realmtext('new_txt', "Nothing to cast with!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
        realm.spawn_realmtext('new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if len(flags.item) == 0:
        realm.spawn_realmtext('new_txt', "Nothing here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    item_repair = flags.item[-1]

    if (
            item_repair.props['item_type'] not in (
            'wpn_melee', 'wpn_ranged',  'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield', 'orb_source'
            ) or
            item_repair.props['condition'] <= 0 or
            item_repair.props['price_sell'] == 0
    ):
        realm.spawn_realmtext('new_txt', "Can't repair that!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    # Custom requirements check.
    if skill_obj.props['cost_mp'] > pc.char_sheet.mp:
        realm.spawn_realmtext('new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    else:
        pc.char_sheet.mp_get(skill_obj.props['cost_mp'] * -1)
        realm.wins_dict['pools'].updated = True
    if item_repair.props['price_sell'] > pc.char_sheet.gold_coins:
        realm.spawn_realmtext('new_txt', "Not enough gold!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
        pc.char_sheet.experience_get(wins_dict, pc, exp)

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

    if not treasure.charge_change(item_adress[0][item_adress[1]], -1):
        pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
        wins_dict['context'].end()
        # pc.char_sheet.calc_stats()
        wins_dict['realm'].spawn_realmtext(None, 'Potion finished!', (0, 0), (0, -24),
                                           'fnt_celeb', pc, None, 240, 'def_bold', 24)

    pc.char_sheet.hp_get(heal_hp_value)
    wins_dict['pools'].updated = True
    wins_dict['inventory'].updated = True
    wins_dict['hotbar'].updated = True
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

    if not treasure.charge_change(item_adress[0][item_adress[1]], -1):
        pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
        wins_dict['context'].end()
        # pc.char_sheet.calc_stats()
        wins_dict['realm'].spawn_realmtext(None, 'Potion finished!', (0, 0), (0, -24),
                                           'fnt_celeb', pc, None, 240, 'def_bold', 24)

    pc.char_sheet.mp_get(heal_mp_value)
    wins_dict['pools'].updated = True
    wins_dict['inventory'].updated = True
    wins_dict['hotbar'].updated = True
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

    pc.char_sheet.food_get(food_value)

    wins_dict['pools'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
    wins_dict['context'].end()

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
    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

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
        realm.spawn_realmtext('new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.door is not None and flags.door.lock is not None:
        pl_object = flags.door
    elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None:
        pl_object = flags.obj
    else:
        realm.spawn_realmtext('new_txt', "No locks here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill_obj == item.props['use_skill']:
        lockpick_mod = item_adress[0][item_adress[1]].props['mods']['prof_picklock']['value_base']
        lockpick = item_adress[0][item_adress[1]]
    else:
        lockpicks = pc.char_sheet.inventory_search('exp_lockpick')
        if len(lockpicks) == 0:
            realm.spawn_realmtext('new_txt', "I have no lockpicks!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        lockpick, lockpick_mod = get_highest(lockpicks, 'prof_picklock')

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    pl_result = pl_object.lock.unlock(wins_dict, pc, lockpick=lockpick, lockpick_mod=lockpick_mod)
    if pl_result:
        pl_object.lock = None
        pl_object.image_update()

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
    if item_adress[0] in (pc.char_sheet.inventory, pc.char_sheet.skills):
        realm.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': "This item may be used from Hotbar!",
            'bttn_cancel': 'OK'
        }
        realm.wins_dict['dialogue'].launch(pc)
        return True

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
        realm.spawn_realmtext('new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True
    if flags.trap is not None and flags.trap.visible == 1:
        trap = flags.trap
    elif flags.obj is not None and hasattr(flags.obj, 'trap') and flags.obj.trap is not None and flags.obj.trap.visible == 1:
        trap = flags.obj.trap
    else:
        realm.spawn_realmtext('new_txt', "Seems no traps here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill_obj == item.props['use_skill']:
        tool_mod = item_adress[0][item_adress[1]].props['mods']['prof_disarm']['value_base']
        tool = item_adress[0][item_adress[1]]
    else:
        tools = pc.char_sheet.inventory_search('exp_tools')
        if len(tools) == 0:
            realm.spawn_realmtext('new_txt', "I have no tools!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        tool, tool_mod = get_highest(tools, 'prof_disarm')

    if not skill_costs_check(realm, skill_obj, pc):
        return True

    if trap.mode != 1:
        realm.spawn_realmtext('new_txt', "The trap's safe!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    disarm_result = trap.disarm(wins_dict, pc, tool_mod=tool_mod)
    if disarm_result:
        trap.mode = 0
        trap.image_update()

    pc.char_sheet.item_remove(wins_dict, tool)
    wins_dict['context'].end()

    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill_obj)

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
            realm.spawn_realmtext('new_txt', "Nothing here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
            realm.spawn_realmtext('new_txt', "Can't reach!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True

    for lt in flags.item[::-1]:
        if lt.props['treasure_id'] == 6:
            realm.coins_collect(lt, flags.item, pc)
            break
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
            101: 6   # Disarm skill
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
            realm.spawn_realmtext('new_txt', "I can't learn $n more skills!", (0, 0), (0, -24), None, pc, None, 120,
                                  'def_bold', 24)
            return True

    wins_dict['skillbook'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
    wins_dict['context'].end()

    pc.act(wins_dict, None, skill_obj)

    return False


def skill_reqs_check(realm, skill_obj, pc):
    if pc.busy is not None:
        return False
    if skill_obj.cooldown_timer > 0:
        return False

    if skill_obj.props['item_type'] != 'skill_item' and (
        skill_obj.props['required_char_type'] not in (None, pc.char_sheet.type)
        or not pc.char_sheet.has_skill(skill_obj.props['skill_id'])
    ):
        realm.spawn_realmtext('new_txt', "I have no skills $n for this task!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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
        realm.spawn_realmtext('new_txt', "I need some light!", (0, 0), (0, -24), None, pc, None, 120,
                              'def_bold', 24)
        return False

    return True


def skill_costs_check(realm, skill_obj, pc, rate=1):
    if skill_obj.props['cost_mp'] * rate > pc.char_sheet.mp:
        realm.spawn_realmtext('new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.mp_get(skill_obj.props['cost_mp'] * rate * -1)
        realm.wins_dict['pools'].updated = True

    if skill_obj.props['cost_hp'] * rate > pc.char_sheet.hp:
        realm.spawn_realmtext('new_txt', "Not enough health!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.hp_get(skill_obj.props['cost_hp'] * rate * -1)
        realm.wins_dict['pools'].updated = True

    if skill_obj.props['cost_exp'] * rate > pc.char_sheet.experience:
        realm.spawn_realmtext('new_txt', "Not enough experience!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.experience_get(realm.wins_dict, pc, skill_obj.props['cost_exp'] * rate * -1)
        realm.wins_dict['pools'].updated = True
        realm.wins_dict['charstats'].updated = True

    if skill_obj.props['cost_gold'] * rate > pc.char_sheet.gold_coins:
        realm.spawn_realmtext('new_txt', "Not enough gold!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.gold_coins += (skill_obj.props['cost_gold'] * rate * -1)
        realm.wins_dict['inventory'].updated = True

    return True


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