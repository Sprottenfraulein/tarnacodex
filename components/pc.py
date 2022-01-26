from components import skillfuncs


class PC:
    def __init__(self, x_sq, y_sq, location, anim_set, char_sheet, state=2, speed=0.08):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.prev_x_sq = self.x_sq
        self.prev_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.speed = speed
        self.attack_timer = 0
        self.attacking = None
        self.anim_set = anim_set
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_timings = None
        self.frame_timing = 0
        self.state = state
        self.image = None
        self.animate()

        self.move_instr_x = 0
        self.move_instr_y = 0
        self.vision_sq_list = []

        self.location = location
        self.char_sheet = char_sheet

    def animate(self):
        # PC states:
        # 0 face north
        # 1 face east
        # 2 face south
        # 3 face west
        # 4 act north
        # 5 act east
        # 6 act south
        # 7 act west
        # 8 lay down
        if self.state == 0:
            anim_seq = self.anim_set['face_north']
        elif self.state == 1:
            anim_seq = self.anim_set['face_east']
        elif self.state == 2:
            anim_seq = self.anim_set['face_south']
        elif self.state == 3:
            anim_seq = self.anim_set['face_west']
        elif self.state == 4:
            anim_seq = self.anim_set['act_north']
        elif self.state == 5:
            anim_seq = self.anim_set['act_east']
        elif self.state == 6:
            anim_seq = self.anim_set['act_south']
        elif self.state == 7:
            anim_seq = self.anim_set['act_west']
        elif self.state == 8:
            anim_seq = self.anim_set['lay_down']

        self.image = anim_seq['images']
        self.anim_timings = anim_seq['timings']
        if self.anim_frame >= len(self.image):
            self.anim_frame -= len(self.image)
        self.frame_timing = self.anim_timings[self.anim_frame]

    def tick(self, realm, fate_rnd, wins_dict, active_wins):
        if self.attacking is None and (self.move_instr_x != 0 or self.move_instr_y != 0):
            self.move(self.move_instr_x, self.move_instr_y, realm, wins_dict, active_wins)

        elif self.attacking is not None:
            if self.attack_timer == self.attacking['commit_time']:
                aimed_obj = wins_dict['target'].mob_object
                getattr(skillfuncs, self.attacking['function_name'])(realm, fate_rnd, self, aimed_obj, self.attacking)
            if self.attack_timer > self.attacking['time']:
                self.attacking = None
                if self.state > 3:
                    self.state_change(self.state - 4)
            else:
                self.attack_timer += 1

        if self.attacking is not None or (self.move_instr_x != 0 or self.move_instr_y != 0):
            if self.anim_timer > self.frame_timing:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1

    # movement
    def move(self, step_x, step_y, realm, wins_dict, active_wins):
        # check if pc is already moving
        # if self.dest_x_sq != self.x_sq or self.dest_y_sq != self.y_sq:
        #     return
        # change pc state according to moving direction
        if step_y < 0:
            self.state_change(0)
        elif step_x > 0:
            self.state_change(1)
        elif step_y > 0:
            self.state_change(2)
        elif step_x < 0:
            self.state_change(3)

        if step_x != 0 and step_y != 0:
            step_x *= 0.8
            step_y *= 0.8
        dest_x_sq = round(self.x_sq + step_x * self.speed)
        dest_y_sq = round(self.y_sq + step_y * self.speed)

        if not realm.maze.flag_array[dest_y_sq][dest_x_sq].mov:
            if realm.maze.flag_array[round(self.y_sq)][dest_x_sq].mov:
                step_y = 0
            elif realm.maze.flag_array[dest_y_sq][round(self.x_sq)].mov:
                step_x = 0
            else:
                return

        # sq_flags = maze.flag_array[self.dest_y_sq][self.dest_x_sq]
        # sq_flags.mov = True

        self.x_sq += step_x * self.speed
        self.y_sq += step_y * self.speed

        # sq_flags = maze.flag_array[round(self.y_sq)][round(self.x_sq)]
        # sq_flags.mov = False
        if realm.view_maze_follow:
            realm.view_maze_update(self.x_sq, self.y_sq)

            if abs(self.x_sq - self.prev_x_sq) >= 1 or abs(self.y_sq - self.prev_y_sq) >= 1:
                # visibility update
                realm.calc_vision_alt()
                self.prev_x_sq = self.x_sq
                self.prev_y_sq = self.y_sq

                realm.shortlists_update(everything=True)

                if realm.maze.flag_array[dest_y_sq][dest_x_sq].item:
                    for loot in realm.loot_short:
                        if loot.props['treasure_id'] == 6 and loot.x_sq == round(self.x_sq) and loot.y_sq == round(self.y_sq):
                            self.char_sheet.gold_coins += loot.props['amount']
                            realm.maze.flag_array[dest_y_sq][dest_x_sq].item -= True
                            realm.maze.loot.remove(loot)
                            realm.loot_short.remove(loot)
                            if wins_dict['inventory'] in active_wins:
                                wins_dict['inventory'].render()
                            break

    def attack(self, target, skill_props):
        if self.attacking is not None:
            return
        self.face_point(target.mob_object.x_sq, target.mob_object.y_sq)
        self.state_change(self.state + 4)

        self.attacking = skill_props

        self.attack_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0

    def state_change(self, new_state):
        # check if state change is possible
        if self.state == new_state:
            return

        # change state
        self.state = new_state
        self.animate()

    def face_point(self, x_sq, y_sq):
        dist_x, dist_y = x_sq - self.x_sq, y_sq - self.y_sq
        if abs(dist_x) >= abs(dist_y):
            if dist_x > 0:
                self.state_change(1)
            else:
                self.state_change(3)
        else:
            if dist_y > 0:
                self.state_change(2)
            else:
                self.state_change(0)
