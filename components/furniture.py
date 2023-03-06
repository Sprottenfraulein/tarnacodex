class Furniture:
    def __init__(self, furn_type, x_sq, y_sq, alignment, room, image_query, tile_sets, solid, off_x_sq=0, off_y_sq=0, render_later=False):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x_sq = off_x_sq
        self.off_y_sq = off_y_sq
        self.alignment = alignment
        self.room = room
        self.solid = solid
        self.image_query = image_query

        self.image = None
        self.furn_type = furn_type

        self.image_update(tile_sets)
        self.render_later = render_later

    def image_update(self, tile_sets):
        self.image = tile_sets.get_image(*self.image_query)

    def use(self, wins_dict, active_wins, pc, maze_module):
        wins_dict['realm'].spawn_realmtext('new_txt', "It looks like nothing special.", (0, 0), (0, -24), None, pc, None,
                                           120, 'def_bold', 24)


class Remains(Furniture):
    def __init__(self, x_sq, y_sq, room, tile_sets, inventory, gold):
        super().__init__('remains', x_sq, y_sq, 0, room, ('dung_furniture', (24, 24), (8, )), tile_sets, 1)
        self.inventory = inventory
        self.gold = gold

    def use(self, wins_dict, active_wins, pc, maze_module):
        if self.inventory is None:
            wins_dict['realm'].spawn_realmtext('new_txt', "It looks like a dead body.", (0, 0), (0, -24), None, pc,
                                               None,
                                               120, 'def_bold', 24)
            return
        exceed_list = []
        for itm in self.inventory:
            for i in range(0, pc.char_sheet.inventory.items_max):
                if pc.char_sheet.inventory[i] is None:
                    pc.char_sheet.inventory[i] = itm
                    pc.moved_item_cooldown_check(pc.char_sheet.inventory[i],
                                                 wins_dict['inventory'].inv_sockets_list[i])
                    wins_dict['inventory'].updated = True
                    break
            else:
                exceed_list.append(itm)
        wins_dict['realm'].maze.flag_array[round(self.y_sq)][round(self.x_sq)].mov = True
        self.solid = False
        pc.char_sheet.gold_coins = round(pc.char_sheet.gold_coins + self.gold)
        if exceed_list:
            from components.lootgen import drop_loot
            drop_loot(pc.x_sq, pc.y_sq, wins_dict['realm'], exceed_list)
        self.inventory = None
        self.image_query = ('dung_furniture', (24, 24), (9, ))
        self.image_update(wins_dict['realm'].tilesets)
        wins_dict['realm'].sound_inrealm('cloth_pickup', pc.x_sq, pc.y_sq)
