from components import lootgen, dbrequests, treasure


class Chest:
    def __init__(self, x_sq, y_sq, alignment, room, tileset, off_x=0, off_y=0, lvl=None, items_number=0,
                 treasure_group=None, item_type=None, char_type=None, container=None, disappear=False):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = off_x
        self.off_y = off_y
        self.alignment = alignment
        self.room = room
        self.tileset = tileset
        self.lock = None
        self.trap = None
        self.closed = True
        self.image = None
        self.image_update()

        self.lvl = lvl
        self.items_number = items_number
        self.treasure_group = treasure_group
        self.item_type = item_type
        self.char_type = char_type

        self.container = container
        self.disappear = disappear

    def image_update(self):
        if self.alignment:
            align = 'ver'
            """self.off_x = 0
            self.off_y = 0"""
        else:
            align = 'hor'
            """self.off_x = 0
            self.off_y = 0"""
        if self.lock is not None:
            if self.lock.magical:
                pos = 'mlock'
            else:
                pos = 'lock'
        elif self.closed:
            pos = 'shut'
        else:
            pos = 'open'
        image_name = 'chest_%s_%s' % (align, pos)
        self.image = self.tileset[image_name]

    def use(self, wins_dict, active_wins, pc):
        if not self.closed:
            self.closed = True
            self.image_update()
            return True
        elif self.trap is not None:
            if not self.trap.detect():
                self.trap.trigger()
            return True
        elif self.lock is None:
            self.closed = False
            self.container_unpack(wins_dict, active_wins, pc)
            self.image_update()
            return True
        elif self.lock.unlock(wins_dict, pc):
            self.lock = None
            self.image_update()
            return True
        return False

    def container_unpack(self, wins_dict, active_wins, pc):
        realm = wins_dict['realm']
        if self.items_number > 0:
            if self.container is None:
                self.container = []
            roll = 1
            goods_level_cap = self.lvl or pc.char_sheet.level
            good_ids = dbrequests.treasure_get(realm.db.cursor, goods_level_cap,
                                               self.treasure_group, roll, item_type=self.item_type,
                                               char_type=self.char_type)
            for j in good_ids:
                self.container.append(treasure.Treasure(j, goods_level_cap, realm.db.cursor,
                                                        realm.tilesets, realm.resources,
                                                        realm.pygame_settings.audio,
                                                        realm.resources.fate_rnd))
            self.items_number = 0
        if len(self.container) > 0:
            lootgen.drop_loot(self.x_sq, self.y_sq, realm, self.container)
            self.container.clear()
        if self.disappear:
            realm.maze.chests.remove(self)
            realm.maze.flag_array[self.y_sq][self.x_sq].obj = None
            realm.maze.flag_array[self.y_sq][self.x_sq].mov = True