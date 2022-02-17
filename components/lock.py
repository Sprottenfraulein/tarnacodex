import random


class Lock:
    def __init__(self, lvl, magical=False, code=None):
        self.lvl = lvl
        self.magical = magical
        self.code = code
        self.jammed = False

    def unlock(self, wins_dict, pc, lockpick=None, lockpick_mod=None):
        # checking for keys
        pc_keys = pc.char_sheet.inventory_search_by_id(14)
        if self.magical:
            wins_dict['realm'].spawn_realmtext('new_txt', "The lock is unpickable!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
            return False
        elif self.jammed:
            wins_dict['realm'].spawn_realmtext('new_txt', "The lock is jammed!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
            return False
        elif len(pc_keys) > 0:
            for i in range(len(pc_keys) - 1, -1, -1):
                if pc_keys[i].props['lvl'] == self.lvl:
                    pc.char_sheet.inventory[pc.char_sheet.inventory.index(pc_keys[i])] = None
                    wins_dict['inventory'].updated = True
                    wins_dict['realm'].spawn_realmtext('new_txt', "I have a key $n for this one!", (0, 0), (0, -24),
                                                       None, pc, None, 120, 'def_bold', 24)
                    return True
        elif lockpick is not None:
            lvl_dif = min(1, pc.char_sheet.level - self.lvl)
            skill = pc.char_sheet.profs['prof_picklock'] + lvl_dif * 250 + lockpick_mod     # 25% per level penalty
            rnd_roll = random.randrange(0, 1001)
            if rnd_roll - skill >= 500:
                self.jammed = True
                wins_dict['realm'].spawn_realmtext('new_txt', "I've jammed $n the lock!", (0, 0), (0, -24), None, pc, None,
                                                   120, 'def_bold', 24)
                return False
            if skill >= rnd_roll:
                wins_dict['realm'].spawn_realmtext('new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)

                exp = self.lvl * 100
                pc.char_sheet.experience_get(wins_dict, pc, exp)
                wins_dict['pools'].updated = True
                wins_dict['charstats'].updated = True
                wins_dict['realm'].spawn_realmtext('new_txt', '%s exp.' % (exp),
                                                   (0, 0), (0, -24), 'sun', pc, (0, -2), 60, 'large', 16, 0,
                                                   0.17)

                return True
            else:
                wins_dict['realm'].spawn_realmtext('new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)
                return False
