from library import maths
from components import treasure
import random


def attack_default(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill, pc):
            return '-', '-'
        else:
            return att_val_min, att_val_max

    if not skill_reqs_check(realm, skill, pc):
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "Attack what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > skill.props['range']:
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_costs_check(realm, skill, pc):
        return True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    damage = rnd_attack * (100 - target.stats['def_physical']) // 100  # reduce attack by percent of def

    target.wound(damage, 'att_physical', False, is_crit, wins_dict, fate_rnd, pc)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill)
    # realm.pygame_settings.audio.sound(skill.props['sound_use'])
    if pc.char_sheet.equipped[2][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)
    elif pc.char_sheet.equipped[3][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[3][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def shot_default(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    realm = wins_dict['realm']

    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 1000)  # att_mods comprehended as procents
    att_val_max += (att_val_max * att_mods // 1000)  # att_mods comprehended as procents
    if just_values:
        if not skill_reqs_check(realm, skill, pc):
            return '-', '-'
        else:
            return att_val_min, att_val_max

    if not skill_reqs_check(realm, skill, pc):
        return True

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "Shoot what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if not skill_reqs_check(realm, skill, pc):
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > (skill.props['range'] * (pc.char_sheet.profs['prof_range'] + 1000) // 1000):
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    if not skill_costs_check(realm, skill, pc):
        return True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    image_pack = (
        realm.tilesets.get_image('item_effects', (16, 16), (0,)),
        realm.tilesets.get_image('item_effects', (16, 16), (1,))
    )
    speed = 0.25
    realm.spawn_projectile((pc.x_sq, pc.y_sq), (target.x_sq, target.y_sq), (rnd_attack, 'att_physical', is_crit, pc),
                           speed, image_pack, collision_limit=1, blast_radius=0)

    pc.food_change(wins_dict, -5)
    pc.act(wins_dict, (target.x_sq, target.y_sq), skill)

    if pc.char_sheet.equipped[2][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[2][0].props['sound_swing'], target.x_sq, target.y_sq)
    elif pc.char_sheet.equipped[3][0] is not None:
        wins_dict['realm'].sound_inrealm(pc.char_sheet.equipped[3][0].props['sound_swing'], target.x_sq, target.y_sq)

    return False


def potion_heal(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    heal_hp_value = item_adress[0][item_adress[1]].props['mods']['hp_pool']['value_base']
    if just_values:
        return heal_hp_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill, pc):
        return True

    pc.char_sheet.hp_get(heal_hp_value)
    wins_dict['pools'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    wins_dict['context'].end()

    pc.act(wins_dict, None, skill)

    return False


def potion_power(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    heal_mp_value = item_adress[0][item_adress[1]].props['mods']['mp_pool']['value_base']
    if just_values:
        return heal_mp_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill, pc):
        return True

    pc.char_sheet.mp_get(heal_mp_value)
    wins_dict['pools'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    wins_dict['context'].end()

    pc.act(wins_dict, None, skill)

    return False


def eat(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    food_value = item_adress[0][item_adress[1]].props['mods']['food_pool']['value_base'] * skill.props['lvl']
    if just_values:
        return food_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill, pc):
        return True

    pc.char_sheet.food_get(food_value)

    wins_dict['pools'].updated = True
    realm.pygame_settings.audio.sound(item_adress[0][item_adress[1]].props['sound_use'])
    pc.char_sheet.item_remove(wins_dict, item_adress[0][item_adress[1]])
    wins_dict['context'].end()

    pc.act(wins_dict, None, skill)

    return False


def picklock(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    if just_values:
        lockpicks = pc.char_sheet.inventory_search('exp_lockpick')
        if len(lockpicks) == 0:
            return '-'
        lockpick, lockpick_mod = get_highest(lockpicks, 'prof_picklock')
        return (lockpick_mod + pc.char_sheet.profs['prof_picklock']) // 10

    realm = wins_dict['realm']
    if not skill_reqs_check(realm, skill, pc):
        return True

    if no_aim:
        for i in range(round(pc.y_sq) - (skill.props['range'] - 1),
                       round(pc.y_sq) + (skill.props['range'] - 1) + 1):
            for j in range(round(pc.x_sq) - (skill.props['range'] - 1),
                           round(pc.x_sq) + (skill.props['range'] - 1) + 1):
                try:
                    flags = realm.maze.flag_array[i][j]
                except IndexError:
                    continue
                if not flags.vis:
                    continue
                if flags.door is not None and flags.door.lock is not None:
                    pl_object = flags.door
                    x_sq, y_sq = j, i
                    break
                elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None:
                    pl_object = flags.obj
                    x_sq, y_sq = j, i
                    break
            else:
                continue
            break
        else:
            realm.spawn_realmtext('new_txt', "No locks here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return False
    else:
        x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
        try:
            flags = realm.maze.flag_array[y_sq][x_sq]
        except IndexError:
            return True
        if not flags.vis:
            return True
        if flags.door is not None and flags.door.lock is not None:
            pl_object = flags.door
        elif flags.obj is not None and hasattr(flags.obj, 'lock') and flags.obj.lock is not None:
            pl_object = flags.obj
        else:
            return True
        if maths.get_distance(pc.x_sq, pc.y_sq, x_sq, y_sq) > skill.props['range']:
            realm.spawn_realmtext('new_txt', "Too far!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill == item.props['use_skill']:
        lockpick_mod = item_adress[0][item_adress[1]].props['mods']['prof_picklock']['value_base']
        lockpick = item_adress[0][item_adress[1]]
    else:
        lockpicks = pc.char_sheet.inventory_search('exp_lockpick')
        if len(lockpicks) == 0:
            realm.spawn_realmtext('new_txt', "I have no lockpicks!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        lockpick, lockpick_mod = get_highest(lockpicks, 'prof_picklock')

    if not skill_costs_check(realm, skill, pc):
        return True

    pl_result = pl_object.lock.unlock(wins_dict, pc, lockpick=lockpick, lockpick_mod=lockpick_mod)
    if pl_result:
        pl_object.lock = None
        pl_object.image_update()

    pc.char_sheet.item_remove(wins_dict, lockpick)
    wins_dict['context'].end()

    pc.food_change(wins_dict, -10)
    pc.act(wins_dict, (x_sq, y_sq), skill)

    return False


def disarm_trap(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    if just_values:
        tools = pc.char_sheet.inventory_search('exp_tools')
        if len(tools) == 0:
            return '-'
        tool, tool_mod = get_highest(tools, 'prof_disarm')
        return (tool_mod + pc.char_sheet.profs['prof_disarm']) // 10

    realm = wins_dict['realm']
    if not skill_reqs_check(realm, skill, pc):
        return True

    if no_aim:
        for i in range(round(pc.y_sq) - (skill.props['range'] - 1),
                       round(pc.y_sq) + (skill.props['range'] - 1) + 1):
            for j in range(round(pc.x_sq) - (skill.props['range'] - 1),
                           round(pc.x_sq) + (skill.props['range'] - 1) + 1):
                try:
                    flags = realm.maze.flag_array[i][j]
                except IndexError:
                    continue
                if not flags.vis:
                    continue
                if flags.trap is not None and flags.trap.visible == 1:
                    trap = flags.trap
                    x_sq, y_sq = j, i
                    break
                elif flags.obj is not None and hasattr(flags.obj, 'trap') and flags.obj.trap is not None and flags.obj.trap.visible == 1:
                    trap = flags.obj.trap
                    x_sq, y_sq = j, i
                    break
            else:
                continue
            break
        else:
            realm.spawn_realmtext('new_txt', "Seems no traps here!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return False
    else:
        x_sq, y_sq = realm.xy_pixels_to_squares(realm.mouse_pointer.xy)
        try:
            flags = realm.maze.flag_array[y_sq][x_sq]
        except IndexError:
            return True
        if not flags.vis:
            return True
        if flags.trap is not None and flags.trap.visible == 1:
            trap = flags.trap
        elif flags.obj is not None and hasattr(flags.obj, 'trap') and flags.obj.trap is not None and flags.obj.trap.visible == 1:
            trap = flags.obj.trap
        else:
            return True
        if maths.get_distance(pc.x_sq, pc.y_sq, x_sq, y_sq) > skill.props['range']:
            realm.spawn_realmtext('new_txt', "Too far!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True

    item = item_adress[0][item_adress[1]]
    if 'use_skill' in item.props and skill == item.props['use_skill']:
        tool_mod = item_adress[0][item_adress[1]].props['mods']['prof_disarm']['value_base']
        tool = item_adress[0][item_adress[1]]
    else:
        tools = pc.char_sheet.inventory_search('exp_tools')
        if len(tools) == 0:
            realm.spawn_realmtext('new_txt', "I have no tools!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True
        tool, tool_mod = get_highest(tools, 'prof_disarm')

    if not skill_costs_check(realm, skill, pc):
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
    pc.act(wins_dict, (x_sq, y_sq), skill)

    return False


def pickup(wins_dict, fate_rnd, pc, skill, item_adress, no_aim=False, just_values=False):
    if just_values:
        return ()
    realm = wins_dict['realm']
    if not skill_reqs_check(realm, skill, pc):
        return True

    if no_aim:
        for i in range(round(pc.y_sq) - (skill.props['range'] - 1),
                       round(pc.y_sq) + (skill.props['range'] - 1) + 1):
            for j in range(round(pc.x_sq) - (skill.props['range'] - 1),
                           round(pc.x_sq) + (skill.props['range'] - 1) + 1):
                try:
                    flags = realm.maze.flag_array[i][j]
                except IndexError:
                    continue
                if flags.vis and len(flags.item) > 0:
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
        if maths.get_distance(pc.x_sq, pc.y_sq, x_sq, y_sq) > skill.props['range']:
            realm.spawn_realmtext('new_txt', "Too far!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
            return True

    for lt in flags.item:
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
    pc.act(wins_dict, (x_sq, y_sq), skill)
    wins_dict['context'].end()

    return False


def skill_reqs_check(realm, skill, pc):
    if pc.busy is not None:
        return False
    if skill.cooldown_timer > 0:
        return False

    if skill.props['required_char_type'] not in (None, pc.char_sheet.type):
        realm.spawn_realmtext('new_txt', "I have no skills for this task!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    if (skill.props['required_head'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[0],), skill.props['required_head'])):
        return False
    if (skill.props['required_chest'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[1],), skill.props['required_chest'])):
        return False
    if (skill.props['required_hand1'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[2], pc.char_sheet.equipped[3]), skill.props['required_hand1'])):
        return False
    if (skill.props['required_hand2'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[2], pc.char_sheet.equipped[3]), skill.props['required_hand2'])):
        return False
    if (skill.props['required_ring'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[4], pc.char_sheet.equipped[5]), skill.props['required_ring'])):
        return False
    if (skill.props['required_light'] is not None
            and not equipment_types_check((pc.char_sheet.equipped[6],), skill.props['required_light'])):
        return False

    return True


def skill_costs_check(realm, skill, pc):
    if skill.props['cost_mp'] > pc.char_sheet.mp:
        realm.spawn_realmtext('new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.mp_get(skill.props['cost_mp'] * -1)
        realm.wins_dict['pools'].updated = True

    if skill.props['cost_hp'] > pc.char_sheet.hp:
        realm.spawn_realmtext('new_txt', "Not enough health!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.hp_get(skill.props['cost_hp'] * -1)
        realm.wins_dict['pools'].updated = True

    if skill.props['cost_exp'] > pc.char_sheet.experience:
        realm.spawn_realmtext('new_txt', "Not enough experience!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.experience_get(realm.wins_dict, pc, skill.props['cost_exp'] * -1)
        realm.wins_dict['pools'].updated = True
        realm.wins_dict['charstats'].updated = True

    if skill.props['cost_gold'] > pc.char_sheet.gold_coins:
        realm.spawn_realmtext('new_txt', "Not enough gold!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False
    else:
        pc.char_sheet.gold_coins += (skill.props['cost_gold'] * -1)
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