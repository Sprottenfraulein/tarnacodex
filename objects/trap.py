class Trap:
    def __init__(self, x_sq, y_sq, maze_lvl, room, label, rang, dam_type, dam_val_base, dam_val_spread, lvl):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.maze_lvl = maze_lvl
        self.lvl = lvl
        self.room = room
        self.label = label
        self.range = rang
        self.dam_type = dam_type
        self.dam_val_base = dam_val_base
        self.dam_val_spread = dam_val_spread