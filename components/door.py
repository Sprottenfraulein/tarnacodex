class Door:
    def __init__(self, x_sq, y_sq, alignment, tileset, lvl=1, shut=True, lock=None, trap=None, grate=False):
        self.tileset = tileset
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = self.off_y = 0
        self.alignment = alignment
        self.lvl = lvl
        self.shut = shut
        self.lock = lock
        self.trap = trap
        self.grate = grate
        self.image_update()

    def use(self, pc):
        if not self.shut:
            self.shut = True
            self.image_update()
            return True
        elif self.trap is not None:
            if not self.trap.detect():
                self.trap.trigger()
            return True
        elif self.lock is None:
            self.shut = False
            self.image_update()
            return True
        elif self.lock.unlock(pc):
            self.lock = None
            self.image_update()
            return True
        return False

    def image_update(self):
        if self.alignment:
            align = 'ver'
            self.off_x = 0
            self.off_y = -24
        else:
            align = 'hor'
            self.off_x = -24
            self.off_y = 0
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

