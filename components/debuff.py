# Debuff class, derived from dict with added timers


class DeBuff(dict):
    def __init__(self, de_buff, de_buff_dict=None):
        super().__init__()
        self.timer_freq = 0
        self.timer_dur = 0

        super().update(de_buff)
        if self['frequency'] is not None:
            self.timer_freq = self['frequency'] * 60
        self.timer_dur = self['duration'] * 60

        self.de_buff_dict = de_buff_dict
        if de_buff_dict is not None:
            de_buff_dict[self['de_buff_id']] = self

    def tick(self):
        if self.timer_dur > 0:
            if self['frequency'] is not None:
                if self.timer_freq > 0:
                    self.timer_freq -= 1
                else:
                    self.timer_freq = self['frequency'] * 60
            self.timer_dur -= 1
            if self.timer_dur == 0:
                return False
        return True

    def effect(self, pc, wins_dict):
        if self['pool'] == 0 or 'mods' not in self:
            return
        if 'food_pool' in self['mods']:
            mod = self['mods']['food_pool']['value_base']
            if 'value_spread' in self['mods']['food_pool']:
                mod += self['mods']['food_pool']['value_spread']
            pc.char_sheet.food_get(mod)
            wins_dict['pools'].updated = True
