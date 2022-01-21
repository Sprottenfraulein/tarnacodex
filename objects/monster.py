import random
import math
from library import maths, calc2darray


class Monster:
    def __init__(self, x_sq, y_sq, anim_set, stats, state=2):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.dest_x_sq = self.origin_x_sq = self.x_sq
        self.dest_y_sq = self.origin_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.attack_timer = 0
        self.anim_set = anim_set
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_timings = None
        self.frame_timing = 0
        self.state = state
        self.image = None
        self.highlight = False
        self.animate()

        self.move_instr_x = 0
        self.move_instr_y = 0

        self.stats = stats
        self.hp = self.stats['hp_max'] // 1.6
        self.speed = self.stats['speed']
        self.aimed = False

        self.active_time = 60
        self.rest_time = 180
        self.active_time_spread = 30
        self.rest_time_spread = 120
        self.bhvr_timer = 0

        self.rest = True
        self.waypoint = None

    def animate(self):
        # monster states:
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
        if (not self.rest or self.waypoint is not None) and (self.move_instr_x != 0 or self.move_instr_y != 0):
            self.move(self.move_instr_x, self.move_instr_y, realm)
            if self.anim_timer >= self.frame_timing:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1

        if self.waypoint is not None:
            # self.move_instr_x, self.move_instr_y = maths.rads_dist_to_xy(self.x_sq, self.y_sq, maths.xy_dist_to_rads(self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq), self.speed)

            move_instr_x, move_instr_y = maths.sign(round(realm.pc.x_sq - self.x_sq)), \
                                                   maths.sign(round(realm.pc.y_sq - self.y_sq))

            self.move_instr_x = move_instr_x
            self.move_instr_y = move_instr_y

            if maths.get_distance(self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq) < 1:
                self.waypoint = None
            return

        elif self.bhvr_timer / 8 == self.bhvr_timer // 8:
            if 1 <= maths.get_distance(self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq) <= self.stats['aggro_distance']:
                if self.stats['xray'] or calc2darray.cast_ray(realm.maze.flag_array, self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq, True):
                    self.waypoint = (realm.pc.x_sq, realm.pc.y_sq)

        if self.bhvr_timer == 0:
            self.direction_change(realm)
            self.phase_change()
        else:
            self.bhvr_timer -= 1

    def phase_change(self):
        if self.rest:
            self.go()
        else:
            self.stop()

    def go(self):
        self.rest = False
        self.bhvr_timer = self.active_time + random.randrange(0, self.active_time_spread + 1)

    def stop(self):
        if self.waypoint is not None:
            self.waypoint = None
            self.bhvr_timer = (self.rest_time + random.randrange(0, self.rest_time_spread + 1)) // 4
        else:
            self.bhvr_timer = self.rest_time + random.randrange(0, self.rest_time_spread + 1)
        self.rest = True

    def direction_change(self, realm):
        if self.stats['area_distance'] is None or maths.get_distance(self.origin_x_sq, self.origin_y_sq, self.x_sq,
                                                                     self.y_sq) < self.stats['area_distance']:
            self.move_instr_x = random.randrange(-1, 2)
            self.move_instr_y = random.randrange(-1, 2)
        else:
            self.move_instr_x = maths.sign(self.origin_x_sq - self.x_sq)
            self.move_instr_y = maths.sign(self.origin_y_sq - self.y_sq)

    # movement
    def move(self, step_x, step_y, realm):
        # check if monster is already moving
        # if self.dest_x_sq != self.x_sq or self.dest_y_sq != self.y_sq:
        #     return
        # change monster state according to moving direction
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
        self.dest_x_sq = round(self.x_sq + step_x * self.speed / 100)
        self.dest_y_sq = round(self.y_sq + step_y * self.speed / 100)

        if not self.sq_is_free(realm, self.dest_x_sq, self.dest_y_sq):
            return

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = False

        self.x_sq += step_x * self.speed / 100
        self.y_sq += step_y * self.speed / 100

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = True

    def sq_is_free(self, realm, sq_x, sq_y):
        if sq_x != round(self.x_sq) or sq_y != round(self.y_sq):
            if (not realm.maze.flag_array[sq_y][sq_x].mov
                    or realm.maze.flag_array[sq_y][sq_x].mon):
                if (realm.maze.flag_array[round(self.y_sq)][sq_x].mov
                        or not realm.maze.flag_array[round(self.y_sq)][sq_x].mon):
                    step_y = 0
                    # self.move_instr_x *= -1
                    self.phase_change()
                elif (realm.maze.flag_array[sq_y][round(self.x_sq)].mov
                      or not realm.maze.flag_array[sq_y][round(self.x_sq)].mon):
                    step_x = 0
                    # self.move_instr_y *= -1
                    self.phase_change()
                return False
        return True


    def state_change(self, new_state):
        # check if state change is possible
        if self.state == new_state:
            return

        # change state
        self.state = new_state
        self.animate()
