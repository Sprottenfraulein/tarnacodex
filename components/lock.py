import random


class Lock:
    def __init__(self, lvl, magical=False, code=None):
        self.lvl = lvl
        self.magical = magical
        self.code = code

    def unlock(self, pc, key=None):
        # checking for lockpicks
        if self.magical:
            return False
        elif key is not None and key['code'] == self.code:
            pc.char_sheet.inventory_remove(key['id'])
            return True
        elif pc.char_sheet.inventory_search('lockpick'):
            lvl_dif = self.lvl - pc.char_sheet.level
            skill = pc.char_sheet.prof_picklock - lvl_dif * 250     # 25% per level penalty
            rnd_roll = random.randrange(0, 1001)
            if rnd_roll - skill >= 500:
                pc.char_sheet.inventory_remove('lockpick')
            if rnd_roll > skill:
                return True
            else:
                return False
