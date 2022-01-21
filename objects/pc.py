class PC:
    def __init__(self, x_sq, y_sq, location, anim_set, char_sheet, state=2, speed=0.1):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.dest_x_sq = self.prev_x_sq = self.x_sq
        self.dest_y_sq = self.prev_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.speed = speed
        self.attack_timer = 0
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

        self.image = anim_seq['images']
        self.anim_timings = anim_seq['timings']

    def tick(self, realm):
        if self.move_instr_x != 0 or self.move_instr_y != 0:
            self.move(self.move_instr_x, self.move_instr_y, realm)
            if self.anim_timer >= self.frame_timing:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1

    # movement
    def move(self, step_x, step_y, realm):
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
        self.dest_x_sq = round(self.x_sq + step_x * self.speed)
        self.dest_y_sq = round(self.y_sq + step_y * self.speed)

        if not realm.maze.flag_array[self.dest_y_sq][self.dest_x_sq].mov:
            if realm.maze.flag_array[round(self.y_sq)][self.dest_x_sq].mov:
                step_y = 0
            elif realm.maze.flag_array[self.dest_y_sq][round(self.x_sq)].mov:
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

            # if abs(realm.ren_x_sq - realm.view_maze_x_sq) >= 1 or abs(realm.ren_y_sq - realm.view_maze_y_sq) >= 1:
            if abs(self.x_sq - self.prev_x_sq) >= 1 or abs(self.y_sq - self.prev_y_sq) >= 1:

                # visibility update

                # realm.calc_vision_alt()
                realm.calc_vision_alt()
                self.prev_x_sq = self.x_sq
                self.prev_y_sq = self.y_sq
                """

                # creating shortlists
                realm.shortlists_update()

                realm.render_update()"""


    def state_change(self, new_state):
        # check if state change is possible
        if self.state == new_state:
            return

        # change state
        self.state = new_state
        self.animate()