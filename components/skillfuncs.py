from library import maths
import random


def attack_default(wins_dict, fate_rnd, pc, skill, socket, no_aim=False, just_values=False):
    att_val_min, att_val_max = pc.char_sheet.attacks['att_base']
    att_mods = pc.char_sheet.calc_attack_mod('att_physical')
    att_val_min += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    att_val_max += (att_val_min * att_mods // 100)  # att_mods comprehended as procents
    if just_values:
        return att_val_min, att_val_max

    realm = wins_dict['realm']

    target = wins_dict['target'].mob_object
    if target is None or not target.alive:
        if no_aim:
            realm.spawn_realmtext('new_txt', "Attack what?", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return True

    if not skill_reqs_check(realm, skill, pc):
        return True

    if maths.get_distance(pc.x_sq, pc.y_sq, target.x_sq, target.y_sq) > skill.props['range']:
        """realm.schedule_man.task_add('realm_tasks', 1, realm, 'spawn_realmtext',
                                    ('new_txt', "Too far!",
                                     (0, 0), (0, -24), None, True, realm.pc))
        realm.schedule_man.task_add('realm_tasks', 8, realm, 'remove_realmtext', ('new_txt',))"""
        return True

    rnd_attack = random.randrange(att_val_min, att_val_max + 1)
    is_crit = (random.randrange(1, 1001) <= pc.char_sheet.profs['prof_crit'])
    if is_crit:
        rnd_attack *= 4

    damage = rnd_attack * (100 - target.stats['def_physical']) // 100  # reduce attack by percent of def

    target.wound(damage, is_crit, wins_dict, fate_rnd, pc)

    pc.act(wins_dict, (target.x_sq, target.y_sq), skill, socket)

    return False


def potion_heal(wins_dict, fate_rnd, pc, skill, socket, no_aim=False, just_values=False):
    heal_hp_value = skill.props['lvl'] * 10
    if just_values:
        return heal_hp_value

    realm = wins_dict['realm']

    if not skill_reqs_check(realm, skill, pc):
        return True

    pc.char_sheet.hp_get(heal_hp_value)
    wins_dict['pools'].updated = True

    pc.act(wins_dict, None, skill, socket)

    return False


def pickup(wins_dict, fate_rnd, pc, skill, socket, no_aim=False, just_values=False):
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
            pc.char_sheet.gold_coins += lt.props['amount']
            realm.maze.flag_array[y_sq][x_sq].item.remove(lt)
            realm.maze.loot.remove(lt)
            # realm.loot_short.remove(lt)
            wins_dict['inventory'].updated = True
            break
        if len(pc.char_sheet.inventory) >= pc.char_sheet.inventory.items_max:
            for i in range(0, len(pc.char_sheet.inventory)):
                if pc.char_sheet.inventory[i] is None:
                    pc.char_sheet.inventory[i] = lt
                break
            else:
                return True
        else:
            pc.char_sheet.inventory.append(lt)
        realm.maze.flag_array[y_sq][x_sq].item.remove(lt)
        realm.maze.loot.remove(lt)
        # realm.loot_short.remove(lt)
        wins_dict['inventory'].updated = True
        break

    pc.act(wins_dict, (x_sq, y_sq), skill, socket)

    return False


def skill_reqs_check(realm, skill, pc):
    if pc.busy is not None:
        return False
    if skill.cooldown_timer > 0:
        return False
    if skill.props['cost_mp'] > pc.char_sheet.mp:
        realm.spawn_realmtext('new_txt', "Not enough powers!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
        return False

    if skill.props['required_char_type'] not in (None, pc.char_sheet.type):
        realm.spawn_realmtext('new_txt', "I have no skills for this!", (0, 0), (0, -24), None, pc, None, 120, 'def_bold', 24)
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


def equipment_types_check(sockets, item_type):
    for socket in sockets:
        for itm in socket:
            if itm is None:
                continue
            if itm.props['item_type'] == item_type:
                return True
    return False
