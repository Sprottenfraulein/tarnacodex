class Door:
    def __init__(self, x_sq, y_sq, alignment, tileset, lvl=1, shut=True, lock=None, trap=None, grate=False):
        self.tileset = tileset
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x_sq = self.off_y_sq = 0
        self.alignment = alignment
        self.lvl = lvl
        self.shut = shut
        self.lock = lock
        self.trap = trap
        self.grate = grate
        self.image_update()

    def use(self, wins_dict, active_wins, pc):
        if not self.shut:
            if controlled(wins_dict, self):
                return True
            self.shut = True
            self.image_update()
            if self.grate:
                wins_dict['realm'].sound_inrealm('metal_door_shut', self.x_sq, self.y_sq)
            else:
                wins_dict['realm'].sound_inrealm('wooden_door_shut', self.x_sq, self.y_sq)
            return True
        elif self.trap is not None and self.trap.mode == 1:
            if self.trap.visible == 1:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Trap caution',
                    'text': "You are going to trigger the trap! $n Continue?",
                    'bttn_cancel': 'NO',
                    'bttn_ok': 'YES'
                }
                wins_dict['dialogue'].delayed_action['bttn_ok'] = (self.trap, 'trigger', (wins_dict, pc))
                wins_dict['dialogue'].launch(pc)
            elif not self.trap.detect(wins_dict, pc) and self.trap.mode == 1:
                self.trap.trigger(wins_dict, pc)
            return True
        elif self.lock is None:
            if controlled(wins_dict, self):
                return True
            self.shut = False
            self.image_update()
            if self.grate:
                wins_dict['realm'].sound_inrealm('metal_door_open', self.x_sq, self.y_sq)
            else:
                wins_dict['realm'].sound_inrealm('wooden_door_open', self.x_sq, self.y_sq)
            return True
        elif self.lock.unlock(wins_dict, pc):
            self.lock = None
            self.image_update()
            return True
        return False

    def image_update(self):
        if self.alignment:
            align = 'ver'
            self.off_x_sq = 0
            self.off_y_sq = -1
        else:
            align = 'hor'
            self.off_x_sq = -1
            self.off_y_sq = 0
        if self.grate:
            typ = 'grate'
        else:
            typ = 'door'
        if self.lock is not None:
            if self.lock.magical:
                pos = 'mlock'
            else:
                pos = 'lock'
        elif self.shut:
            pos = 'shut'
        else:
            pos = 'open'
        image_name = '%s_%s_%s' % (typ, align, pos)
        self.image = self.tileset[image_name]


def controlled(wins_dict, door):
    ind = wins_dict['realm'].maze.doors.index(door)
    for trigger in wins_dict['realm'].maze.triggers:
        if ind in trigger.grate_index_list:
            wins_dict['realm'].spawn_realmtext('new_txt', "It's operated from somewhere else.", (0, 0), (0, -24),
                                               None, wins_dict['realm'].pc, None, 120, 'def_bold', 24)
            wins_dict['realm'].pygame_settings.audio.sound('mech_hard')
            return True
