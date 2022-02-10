import random


class Lock:
    def __init__(self, lvl, magical=False, code=None):
        self.lvl = lvl
        self.magical = magical
        self.code = code
        self.jammed = False

    def unlock(self, wins_dict, pc, key=None, lockpick_mod=None):
        # checking for lockpicks
        if self.magical:
            return False
        elif self.jammed:
            wins_dict['realm'].spawn_realmtext('new_txt', "The lock is jammed!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
            return False
        elif key is not None and key['code'] == self.code:
            pc.char_sheet.inventory_remove(key['treasure_id'])
            return True
        elif lockpick_mod is not None:
            lvl_dif = min(1, pc.char_sheet.level - self.lvl)
            skill = pc.char_sheet.profs['prof_picklock'] + lvl_dif * 250 + lockpick_mod     # 25% per level penalty
            rnd_roll = random.randrange(0, 1001)
            if rnd_roll - skill >= 500:
                pc.char_sheet.inventory_remove('exp_lockpick')
                self.jammed = True
                wins_dict['realm'].spawn_realmtext('new_txt', "I've jammed $n the lock!", (0, 0), (0, -24), None, pc, None,
                                                   120, 'def_bold', 24)
                return False
            if skill >= rnd_roll:
                wins_dict['realm'].spawn_realmtext('new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)
                return True
            else:
                wins_dict['realm'].spawn_realmtext('new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)
                return False
