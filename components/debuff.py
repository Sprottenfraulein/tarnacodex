# Debuff class, derived from dict with added timers


class DeBuff(dict):
    def __init__(self):
        super().__init__()
        self.timer_freq = 0
        self.timer_dur = 0
