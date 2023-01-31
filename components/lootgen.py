from components import treasure, dbrequests, textinserts
from library import calc2darray, logfun, pickrandom
import random


def generate_loot(monster, realm, fate_rnd, pc, log=True):
    tr_group = monster.stats['treasure_group']
    tr_amount = monster.stats['treasure_amount']
    if 'affixes' in monster.stats:
        for affix in monster.stats['affixes']:
            if affix['additional_treasure'] is not None:
                tr_amount += affix['additional_treasure']

    treasure_list = []
    if pc.char_sheet.level == 1:
        rnd_rate = tr_amount + 1
    elif pc.char_sheet.level == 2:
        rnd_rate = tr_amount + 1
    elif pc.char_sheet.level == 3:
        rnd_rate = tr_amount
    elif pc.char_sheet.level < 6:
        rnd_rate = random.randrange(0, tr_amount + 1)
    else:
        rnd_rate = fate_rnd.expo_rnd(0, tr_amount + 1)
    actual_amount = max(rnd_rate, monster.stats['grade']['grade_level'])

    itm_lvl_spread_list = [
        (-2, 400),
        (-1, 1000),
        (0, 400),
        (1, 200)
    ]

    rnd_roll = random.randrange(1, 10001)
    tr_ids_list = [
        (tr['treasure_id'], tr['roll_chance'])
        for tr in dbrequests.treasure_get(
            realm.db.cursor,
            max(1, monster.stats['lvl'] + pickrandom.items_get(itm_lvl_spread_list, 1)[0]),
            tr_group, rnd_roll
        )
    ]
    rnd_ids = pickrandom.items_get(tr_ids_list, actual_amount, items_pop=True)
    for rnd_id in rnd_ids:
        new_tr = treasure.Treasure(
            rnd_id, max(1, monster.stats['lvl'] + pickrandom.items_get(itm_lvl_spread_list, 1)[0]),
            realm.db.cursor, realm.tilesets, realm.resources, realm.pygame_settings.audio, fate_rnd,
            mob_stats=monster.stats, findmagic=pc.char_sheet.profs['prof_findmagic']
        )
        treasure.loot_validate(new_tr.props)
        treasure_list.append(new_tr)

        # SPECIAL MANUSCRIPT STATEMENT
        if new_tr.props['item_type'] == 'misc_man':  # Manuscript item treasure_id
            rnd_roll = random.randrange(1, 10001)
            mans_list = [
                (mn, mn['roll_chance'])
                for mn in dbrequests.manuscript_get(realm.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'],
                                                    rnd_roll)
            ]
            if len(mans_list) == 0:
                del treasure_list[-1]
            else:
                new_tr.props['desc'] = textinserts.insert(realm, pc, pickrandom.items_get(mans_list, 1)[0]['desc'])

    # SPECIAL QUEST STATEMENT
    if (realm.maze.stage_index == realm.maze.chapter['stage_number'] - 1
            and not [mob for mob in realm.maze.mobs if mob.alive]):
        new_tr = treasure.Treasure(realm.maze.chapter['quest_item_id'], monster.stats['lvl'], realm.db.cursor,
                                   realm.tilesets, realm.resources, realm.pygame_settings.audio, fate_rnd)
        new_tr.props['quest_item'] = True
        treasure.loot_validate(new_tr.props)
        treasure_list.append(new_tr)

        # Special Blackrock statement. If the item in player's inventory, monsters, traps and doors have to be rerolled.
        for i in range(0, realm.maze.chapter['stage_number'] - 1):
            dbrequests.chapter_progress_set(realm.db, pc.char_sheet.id, i, 1, 0, 1, 0, 0, 1)
        realm.spawn_realmtext('new_txt', "This is it! I need to go back now.", (0, 0), (0, -24),
                                           'cyan', pc, None, 240, 'def_bold', 24)
        realm.sound_inrealm('realmtext_noise', pc.x_sq, pc.y_sq)

    return treasure_list


def generate_gold(monster, realm, fate_rnd, pc):
    gold_list = [monster.stats['gold']]     # value is in percents of default gold item amount value.
    if 'affixes' in monster.stats:
        for affix in monster.stats['affixes']:
            if affix['additional_gold'] is not None:
                gold_list.append(affix['additional_gold'])  # affixed monster can have additional gold drop

    treasure_list = []

    for gold_pile in gold_list:
        new_gold = treasure.Treasure(
            6, monster.stats['lvl'], realm.db.cursor,
            realm.tilesets, realm.resources, realm.pygame_settings.audio, fate_rnd
        )
        amount = new_gold.props['amount'] + new_gold.props['amount'] * gold_pile // 100
        new_gold.props['amount'] = round(amount * (treasure.SCALE_RATE_GOLD * (monster.stats['lvl'] * (monster.stats['lvl'] + 1) / 2)))
        new_gold.props['amount'] += (new_gold.props['amount'] * pc.char_sheet.profs['prof_findgold'] // 1000)

        if pc.char_sheet.level == 1:
            new_gold.props['amount'] *= 2
        elif pc.char_sheet.level == 2:
            new_gold.props['amount'] = round(new_gold.props['amount'] * 1.5)

        if new_gold.props['amount'] >= 10000:
            new_gold.props['grade'] = {'grade_level': 3}
        elif new_gold.props['amount'] >= 1000:
            new_gold.props['grade'] = {'grade_level': 2}
        elif new_gold.props['amount'] >= 100:
            new_gold.props['grade'] = {'grade_level': 1}
        else:
            new_gold.props['grade'] = {'grade_level': 0}
        # if new_gold.props['grade']['grade_level'] > 0:
        treasure.images_update(realm.db.cursor, new_gold.props, realm.tilesets)
        treasure.sounds_update(realm.db.cursor, new_gold.props)

        treasure_list.append(new_gold)

    return treasure_list


def drop_loot(x_sq, y_sq, realm, loot_list):
    space_list = calc2darray.fill2d(realm.maze.flag_array, {'mov': False, 'obj': True, 'door': True, 'floor': False},
                                          (x_sq, y_sq), (x_sq, y_sq), len(loot_list) + 1, 2, r_max=20)
    for i in range(len(loot_list) - 1, -1, -1):
        lt_x_sq, lt_y_sq = random.choice(space_list)

        realm.loot_spawn_list.append((loot_list[i], lt_x_sq, lt_y_sq))

    # realm.shortlists_update(loot=True)