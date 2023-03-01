class Furniture:
    def __init__(self, furn_type, x_sq, y_sq, alignment, room, image_query, tile_sets, solid, off_x_sq=0, off_y_sq=0):
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

    def image_update(self, tile_sets):
        self.image = tile_sets.get_image(*self.image_query)

    def use(self, wins_dict, active_wins, pc, maze_module):
        wins_dict['realm'].spawn_realmtext('new_txt', "It looks like nothing special.", (0, 0), (0, -24), None, pc, None,
                                           120, 'def_bold', 24)
