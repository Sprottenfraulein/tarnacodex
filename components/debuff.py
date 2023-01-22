# Debuff class, derived from dict with added timers


class DeBuff(dict):
    def __init__(self, de_buff, de_buff_dict=None):
        super().__init__()
        self.timer_freq = 0
        self.timer_dur = 0

        super().update(de_buff)
        self.timer_freq = self['frequency']
        self.timer_dur = self['duration'] * 60

        self.de_buff_dict = de_buff_dict
        if de_buff_dict is not None:
            de_buff_dict[self['de_buff_id']] = self

    def tick(self):
        if self.timer_dur > 0:
            self.timer_dur -= 1
            if self.timer_dur == 0:
                return False
        return True
