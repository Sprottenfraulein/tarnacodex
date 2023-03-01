class Stairs:
    def __init__(self, x_sq, y_sq, off_x_sq, off_y_sq, dest, room, image, tilename):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x_sq = off_x_sq
        self.off_y_sq = off_y_sq
        self.dest = dest
        self.room = room
        self.image = image
        self.tilename = tilename

    def use(self, wins_dict, active_wins, pc, maze_module):
        if pc.location[1] > 0 or self.dest == "down":
            wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': 'Move to the next stage?',
                'bttn_cancel': 'NO',
                'bttn_ok': 'YES'
            }
            wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'change_stage', (wins_dict, active_wins, pc))
            wins_dict['dialogue'].launch(pc)
        else:
            self.change_stage(wins_dict, active_wins, pc)

    def change_stage(self, wins_dict, active_wins, pc):
        if self.dest == 'up':
            if pc.location[1] > 0:
                pc.location[1] -= 1
                wins_dict['realm'].controls_enabled = False
                wins_dict['app_title'].location_change(pc, 'down')
            else:
                wins_dict['app_title'].ending_check(pc)
        elif self.dest == 'down' and pc.location[1] < wins_dict['realm'].maze.chapter['stage_number'] - 1:
            pc.location[1] += 1
            wins_dict['realm'].controls_enabled = False
            wins_dict['app_title'].location_change(pc, 'up')
