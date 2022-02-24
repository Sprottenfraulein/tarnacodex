class Stairs:
    def __init__(self, x_sq, y_sq, off_x, off_y, dest, room, image, tilename):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = off_x
        self.off_y = off_y
        self.dest = dest
        self.room = room
        self.image = image
        self.tilename = tilename

    def use(self, wins_dict, active_wins, pc):
        if self.dest == 'up':
            if pc.location[1] > 0:
                pc.location[1] -= 1

                wins_dict['app_title'].location_change(pc, 'down')
            else:
                wins_dict['app_title'].ending_check(pc)
        elif self.dest == 'down' and pc.location[1] < wins_dict['realm'].maze.chapter['stage_number'] - 1:
            pc.location[1] += 1
            wins_dict['app_title'].location_change(pc, 'up')
