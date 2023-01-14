from components import treasure, dbrequests
from library import calc2darray, logfun
import random


def generate_loot(monster, realm, fate_rnd, pc, log=True):
    tr_groups = [(monster.stats['treasure_group'], monster.stats['treasure_amount'])]
    if 'affixes' in monster.stats:
        for affix in monster.stats['affixes']:
            try:
                tr_groups.append((affix['treasure_group'], affix['treasure_amount']))
            except KeyError:
                pass

    treasure_list = []
    for tr_group, tr_amount in tr_groups:
        actual_amount = fate_rnd.expo_rnd(0, round(tr_amount * 2))
        rnd_roll = random.randrange(0, 10001)
        tr_ids_list = dbrequests.treasure_get(realm.db.cursor, monster.stats['lvl'], tr_group, rnd_roll)
        for i in range(0, actual_amount):
            rnd_id = tr_ids_list[random.randrange(0, len(tr_ids_list))]
            new_tr = treasure.Treasure(rnd_id, monster.stats['lvl'], realm.db.cursor, realm.tilesets, realm.resources,
                                       realm.pygame_settings.audio, fate_rnd, mob_stats=monster.stats)
            treasure.loot_validate(new_tr.props)
            treasure_list.append(new_tr)

    # SPECIAL BLACKROCK STATEMENT
    if (realm.maze.stage_index == realm.maze.chapter['stage_number'] - 1
            and not [mob for mob in realm.maze.mobs if mob.alive]):
        new_tr = treasure.Treasure(7, monster.stats['lvl'], realm.db.cursor, realm.tilesets, realm.resources,
                                   realm.pygame_settings.audio, fate_rnd)
        treasure.loot_validate(new_tr.props)
        treasure_list.append(new_tr)

        # Special Blackrock statement. If the item in player's inventory, monsters, traps and doors have to be rerolled.
        for i in range(0, realm.maze.chapter['stage_number'] - 1):
            dbrequests.chapter_progress_set(realm.db, pc.char_sheet.id, i, 1, 0, 1, 0, 0, 1)
        realm.spawn_realmtext('new_txt', "That dismal item evokes a sense $n of evil presence!", (0, 0), (0, -24),
                                           'azure', pc, None, 240, 'def_bold', 24)
        realm.sound_inrealm('realmtext_noise', pc.x_sq, pc.y_sq)

    return treasure_list


def generate_gold(monster, realm, fate_rnd, pc):
    gold_list = [monster.stats['gold']]     # value is in percents of default gold item amount value.
    if 'affixes' in monster.stats:
        for affix in monster.stats['affixes']:
            try:
                gold_list.append(affix['additional_gold'])  # affixed monster can have additional gold drop
            except KeyError:
                pass

    treasure_list = []
    for gold_pile in gold_list:
        new_gold = treasure.Treasure(6, monster.stats['lvl'], realm.db.cursor, realm.tilesets, realm.resources,
                                   realm.pygame_settings.audio, fate_rnd)
        amount = new_gold.props['amount'] + new_gold.props['amount'] * gold_pile // 100
        new_gold.props['amount'] = amount * monster.stats['lvl']
        new_gold.props['amount'] += (new_gold.props['amount'] * pc.char_sheet.profs['prof_findgold'] // 1000)

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