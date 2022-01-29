import random
import math
from library import maths, calc2darray, logfun, pickrandom
from components import lootgen


class Monster:
    def __init__(self, x_sq, y_sq, anim_set, stats, state=2):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.dest_x_sq = self.origin_x_sq = self.x_sq
        self.dest_y_sq = self.origin_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.attack_timer = 0
        self.attacking = False
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
        self.hp = self.stats['hp_max']
        self.speed = self.stats['speed']
        self.aimed = False

        self.active_time = 60
        self.rest_time = 60
        self.active_time_spread = 60
        self.rest_time_spread = 60
        self.bhvr_timer = 0

        self.alive = True
        self.rest = True
        self.waypoints = None
        self.wp_ind_list = None
        self.wp_index = None

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

    def tick(self, wins_dict, realm):
        if not self.alive:
            return
        if not self.attacking and ((not self.rest or self.waypoints is not None) and (self.move_instr_x != 0 or self.move_instr_y != 0)):
            self.move(self.move_instr_x, self.move_instr_y, realm)
            if self.anim_timer >= self.frame_timing:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1
        elif self.attacking:
            if self.attack_timer >= self.frame_timing:
                self.attack_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                    self.attacking = False
                    if self.state > 3:
                        self.state_change(self.state - 4)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.attack_timer += 1

        pc_distance = maths.get_distance(self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq)
        if pc_distance <= self.stats['melee_distance'] and not self.attacking:
            self.move_instr_x = self.move_instr_y = 0
            self.attack(wins_dict, realm.pc)

        if self.attacking:
            return

        if self.waypoints is not None:
            if maths.get_distance(self.x_sq, self.y_sq, self.waypoints[self.wp_index][0],
                                  self.waypoints[self.wp_index][1]) <= self.stats['melee_distance']:
                if self.wp_index == 0:
                    self.waypoints = None
                else:
                    self.dir_to_waypoint(self.wp_ind_list[self.wp_parent_index])
            else:
                wp_x, wp_y = self.waypoints[self.wp_index]
                self.move_instr_x, self.move_instr_y = maths.sign(wp_x - self.x_sq), maths.sign(wp_y - self.y_sq)
        elif self.bhvr_timer == 0 and self.stats['melee_distance'] < pc_distance <= self.stats['aggro_distance']:
            if calc2darray.cast_ray(realm.maze.flag_array, self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq, True):
                if self.attack_ranged(realm.pc, pc_distance):
                    return
                self.move_instr_x, self.move_instr_y = maths.sign(round(realm.pc.x_sq) - round(self.x_sq)), maths.sign(
                    round(realm.pc.y_sq) - round(self.y_sq))
                self.go()
            elif self.stats['xray'] == 1:
                self.calc_path(realm, (round(realm.pc.x_sq), round(realm.pc.y_sq)))
        else:
            if self.bhvr_timer == 0:
                self.direction_change(realm)
                self.phase_change()
            else:
                self.bhvr_timer -= 1

    def calc_path(self, realm, xy):
        goal_flag, self.waypoints, self.wp_ind_list = calc2darray.path2d(realm.maze.flag_array, {'mov': False},
                                                                         xy,
                                                                         (round(self.x_sq), round(self.y_sq)), 100, 10,
                                                                         r_max=10)
        if goal_flag:
            self.dir_to_waypoint(-1)
            return True
        else:
            self.waypoints = None
            return False

    def dir_to_waypoint(self, waypoint_index):
        wp_x, wp_y = self.waypoints[waypoint_index]
        self.wp_index = waypoint_index
        self.wp_parent_index = self.wp_ind_list[waypoint_index]
        self.move_instr_x, self.move_instr_y = maths.sign(wp_x - round(self.x_sq)), maths.sign(wp_y - round(self.y_sq))

    def phase_change(self):
        if self.rest:
            self.go()
        else:
            self.stop()

    def go(self):
        self.rest = False
        self.bhvr_timer = self.active_time + random.randrange(0, self.active_time_spread + 1)

    def stop(self):
        self.bhvr_timer = self.rest_time + random.randrange(0, self.rest_time_spread + 1)
        self.rest = True

    def direction_change(self, realm):
        if self.stats['area_distance'] is None or maths.get_distance(self.origin_x_sq, self.origin_y_sq, self.x_sq,
                                                                     self.y_sq) < self.stats['area_distance']:
            self.move_instr_x = random.randrange(-1, 2)
            self.move_instr_y = random.randrange(-1, 2)
        elif calc2darray.cast_ray(realm.maze.flag_array, self.x_sq, self.y_sq, self.origin_x_sq, self.origin_y_sq, True):
            self.move_instr_x, self.move_instr_y = maths.sign(round(self.origin_x_sq) - round(self.x_sq)), maths.sign(
                round(self.origin_y_sq) - round(self.y_sq))
        elif not self.calc_path(realm, (round(self.origin_x_sq), round(self.origin_y_sq))):
                self.move_instr_x = random.randrange(-1, 2)
                self.move_instr_y = random.randrange(-1, 2)

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

        may_x, may_y = self.sq_is_free(realm, self.dest_x_sq, self.dest_y_sq)
        step_x *= may_x
        step_y *= may_y
        if step_x == 0 and step_y == 0:
            if self.waypoints is not None:
                self.waypoints = None
                self.phase_change()
            return

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = False

        self.x_sq += step_x * self.speed / 100
        self.y_sq += step_y * self.speed / 100

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = True

    def sq_is_free(self, realm, sq_x, sq_y):
        step_x, step_y = 1, 1
        if sq_x != round(self.x_sq) or sq_y != round(self.y_sq):
            if realm.maze.flag_array[sq_y][sq_x].mon:
                if not realm.maze.flag_array[round(self.y_sq)][sq_x].mon:
                    step_y = 0
                    # self.move_instr_x *= -1
                elif not realm.maze.flag_array[sq_y][round(self.x_sq)].mon:
                    step_x = 0
                    # self.move_instr_y *= -1
                else:
                    self.phase_change()
                    step_x = step_y = 0
            if not realm.maze.flag_array[sq_y][sq_x].mov:
                if realm.maze.flag_array[round(self.y_sq)][sq_x].mov:
                    step_y = 0
                    # self.move_instr_x *= -1

                elif realm.maze.flag_array[sq_y][round(self.x_sq)].mov:
                    step_x = 0
                    # self.move_instr_y *= -1
                else:
                    self.phase_change()
                    step_x = step_y = 0
        return step_x, step_y

    def attack(self, wins_dict, pc):
        if len(self.stats['attacks_melee']) == 0:
            return False
        self.face_point(pc.x_sq, pc.y_sq)
        self.state_change(self.state + 4)
        self.attacking = True

        attacks_list = [(att, att['chance']) for att in self.stats['attacks_melee']]
        chosen_attack = pickrandom.items_get(attacks_list)[0]

        pc.wound(wins_dict, self, chosen_attack)

        logfun.put('Monster MELEE Attack!', True)
        return True

    def attack_ranged(self, pc, distance):
        if len(self.stats['attacks_ranged']) == 0:
            return False
        available_attacks = [att for att in self.stats['attack_ranged'] if att['range'] <= distance]
        if len(available_attacks) == 0:
            return False
        self.face_point(pc.x_sq, pc.y_sq)
        self.state_change(self.state + 4)
        self.attacking = True
        logfun.put('Monster Ranged Attack!', True)
        return True

    def check(self, wins_dict, fate_rnd, pc):
        if self.hp <= 0:
            self.alive = False
            self.anim_frame = 0
            self.state_change(8)
            pc.char_sheet.experience_get(self.stats['exp'])
            wins_dict['pools'].updated = True
            loot_total = lootgen.generate_loot(self, wins_dict['realm'], fate_rnd, pc)
            loot_total.extend(lootgen.generate_gold(self, wins_dict['realm'], fate_rnd, pc))
            lootgen.drop_loot(round(self.x_sq), round(self.y_sq), wins_dict['realm'], loot_total)

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


