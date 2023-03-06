import random


class Lock:
    def __init__(self, lvl, magical=False, code=None):
        self.lvl = lvl
        self.magical = magical
        self.code = code
        self.jammed = False
        self.exp = 50

    def unlock(self, wins_dict, pc, lockpick=None, lockpick_mod=None):
        # checking for keys
        pc_keys = pc.char_sheet.inventory_search_by_id(14, level=self.lvl)
        if self.magical:
            wins_dict['realm'].spawn_realmtext('new_txt', "The lock is unpickable!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
            return False
        elif self.jammed:
            wins_dict['realm'].spawn_realmtext('new_txt', "The lock is jammed!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)
            wins_dict['realm'].pygame_settings.audio.sound('mech_hard')
            return False
        elif lockpick is not None:
            lvl_dif = min(1, lockpick.props['lvl'] - self.lvl)
            skill = pc.char_sheet.profs['prof_picklock'] + lvl_dif * 250 + lockpick_mod     # 25% per level penalty
            rnd_roll = random.randrange(0, 1001)
            if rnd_roll == 1000 or rnd_roll - skill >= 500:
                self.jammed = True
                wins_dict['realm'].spawn_realmtext('new_txt', "I've jammed $n the lock!", (0, 0), (0, -24), None, pc, None,
                                                   120, 'def_bold', 24)
                wins_dict['realm'].pygame_settings.audio.sound('lock_jam')
                lockpick.props['condition'] = 0
                return False
            if rnd_roll == 0 or skill >= rnd_roll:
                wins_dict['realm'].spawn_realmtext('new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)

                exp = self.exp + self.exp * wins_dict['realm'].maze.EXP_SCALE_RATE * (self.lvl - 1)
                pc.char_sheet.experience_get(wins_dict, pc, self.lvl, exp)
                wins_dict['pools'].updated = True
                wins_dict['charstats'].updated = True
                wins_dict['realm'].pygame_settings.audio.sound('lock_operate')
                lockpick.props['condition'] -= round(self.lvl / lockpick.props['lvl'] * 100)
                return True
            else:
                wins_dict['realm'].spawn_realmtext('new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120,
                                                   'def_bold', 24)
                wins_dict['realm'].pygame_settings.audio.sound('mech_hard')
                lockpick.props['condition'] -= round(self.lvl / lockpick.props['lvl'] * 200)
                return False
        elif len(pc_keys) > 0:
            pc.char_sheet.inventory[pc.char_sheet.inventory.index(pc_keys[0])] = None
            wins_dict['inventory'].updated = True
            wins_dict['realm'].spawn_realmtext('new_txt', "I have a key $n for this one!", (0, 0), (0, -24),
                                               None, pc, None, 120, 'def_bold', 24)
            wins_dict['realm'].pygame_settings.audio.sound('lock_operate')
            wins_dict['realm'].pygame_settings.audio.sound(pc_keys[0].props['sound_pickup'])
            return True
