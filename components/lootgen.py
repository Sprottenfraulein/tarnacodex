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
        rnd_roll = random.randrange(0, 10001)
        tr_ids_list = dbrequests.treasure_get(realm.db.cursor, monster.stats['lvl'], tr_group, rnd_roll)
        for i in range(0, tr_amount):
            rnd_id = tr_ids_list[random.randrange(0, len(tr_ids_list))]
            new_tr = treasure.Treasure(rnd_id, monster.stats['lvl'], realm.db.cursor, realm.tilesets, realm.resources,
                                       realm.pygame_settings.audio, fate_rnd)
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

        logfun.put('Blackrock has been dropped!', log)

    return treasure_list


def generate_gold(monster, realm, fate_rnd, pc):
    mon_gold = monster.stats['gold']
    if mon_gold is None:
        mon_gold = 0
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

        if new_gold.props['amount'] >= 100000:
            new_gold.props['grade'] = 3
        elif new_gold.props['amount'] >= 10000:
            new_gold.props['grade'] = 2
        elif new_gold.props['amount'] >= 1000:
            new_gold.props['grade'] = 1
        if new_gold.props['grade'] > 0:
            treasure.images_update(realm.db.cursor, new_gold.props, realm.tilesets)
            treasure.sounds_update(realm.db.cursor, new_gold.props, realm.pygame_settings.audio)

        treasure_list.append(new_gold)

    return treasure_list


def drop_loot(x_sq, y_sq, realm, loot_list):
    space_list = calc2darray.fill2d(realm.maze.flag_array, {'mov': False, 'obj': 'True', 'floor': False},
                                      (x_sq, y_sq), (x_sq, y_sq), len(loot_list) + 1, 5, r_max=20)
    for i in range(0, len(loot_list)):
        lt_x_sq, lt_y_sq = space_list[min(1 + i, len(space_list) - 1)]

        realm.maze.spawn_loot(lt_x_sq, lt_y_sq, (loot_list[i],))
    # realm.shortlists_update(loot=True)
