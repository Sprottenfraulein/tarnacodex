class Trigger:
    def __init__(self, x_sq, y_sq, alignment, tileset, grate_index_list, value=False, render_later=True):
        self.tileset = tileset
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x_sq = self.off_y_sq = 0
        self.alignment = alignment
        self.grate_index_list = grate_index_list
        self.value = value
        self.image = None
        self.image_update()
        self.render_later = render_later

    def use(self, wins_dict, active_wins, pc, maze):
        if (self.alignment and pc.x_sq < self.x_sq) or (not self.alignment and pc.y_sq < self.y_sq):
            return False
        self.value = not self.value
        sound = ('lock_jam', 'trap_operate')[self.value]
        for ind in self.grate_index_list:
            gr = wins_dict['realm'].maze.doors[ind]
            if gr.lock is not None:
                continue
            if self.value:
                gr.shut = False
                sound = 'metal_door_open'
            else:
                gr.shut = True
                sound = 'metal_door_shut'
            gr.image_update()
            flags = wins_dict['realm'].maze.flag_array[gr.y_sq][gr.x_sq]
            flags.mov = not gr.shut
        wins_dict['realm'].sound_inrealm(sound, self.x_sq, self.y_sq)
        self.image_update()
        return True

    def image_update(self):
        if self.alignment:
            align = 'ver'
        else:
            align = 'hor'
        if self.value:
            pos = 'down'
        else:
            pos = 'up'
        image_name = 'trigger_%s_%s' % (align, pos)
        self.image = self.tileset[image_name]
