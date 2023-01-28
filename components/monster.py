import random
import math
from library import maths, calc2darray, logfun, pickrandom, particle
from components import lootgen


sprite_indexes = (
    'face_north',
    'face_east',
    'face_south',
    'face_west',
    'act_north',
    'act_east',
    'act_south',
    'act_west',
    'lay_down'
)


class Monster:
    def __init__(self, x_sq, y_sq, anim_set, stats, state=2):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.origin_x_sq = self.x_sq
        self.origin_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.attack_timer = 0
        self.attacking = None
        self.anim_set = anim_set
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_timings = None
        self.frame_timing = 0
        self.state = state
        self.image = None
        self.highlight = False
        if anim_set is not None:
            self.animate()

        self.move_instr_x = 0
        self.move_instr_y = 0

        self.stats = stats
        self.level = self.stats['lvl']
        self.hp = self.stats['hp_max']
        self.speed = self.stats['speed']
        self.aimed = False

        self.active_time = 35
        self.rest_time = 60
        self.active_time_spread = 25
        self.rest_time_spread = 120
        self.alert_time = 300
        self.bhvr_timer = 0

        self.alive = True
        self.rest = True
        self.aggred = False
        self.busy = False
        self.waypoints = None
        self.wp_ind_list = None
        self.wp_index = None
        self.wp_parent_index = None

        self.de_buff_dict = {}

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
        # 8 lay down a pochemy nerlzya napisat massiv [i]="face_"
        anim_seq = self.anim_set[sprite_indexes[self.state]]

        self.image = anim_seq['images']
        self.anim_timings = anim_seq['timings']
        if self.anim_frame >= len(self.image):
            self.anim_frame = self.anim_frame % len(self.image)
        self.frame_timing = self.anim_timings[self.anim_frame]

    def tick(self, wins_dict, fate_rnd, realm):
        if not self.alive:
            return
        if not self.attacking and ((not self.rest or self.waypoints is not None) and (self.move_instr_x != 0 or self.move_instr_y != 0)):
            self.move(self.move_instr_x, self.move_instr_y, realm)

        elif self.attacking is not None:
            if self.attack_timer > self.attacking['time']:
                self.attacking = None
                if self.state > 3:
                    self.state_change(self.state - 4)
            else:
                self.attack_timer += 1

        if self.attacking or (not self.rest and (self.move_instr_x != 0 or self.move_instr_y != 0)):
            if self.anim_timer > self.frame_timing:
                self.anim_timer = 0
                if self.anim_frame + 1 < len(self.image):
                    self.anim_frame += 1
                    self.frame_timing = self.anim_timings[self.anim_frame]
                elif not self.attacking:
                    self.anim_frame = 0
                    self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1

        pc_distance = maths.get_distance(self.x_sq, self.y_sq, realm.pc.x_sq, realm.pc.y_sq)
        if pc_distance <= self.stats['melee_distance'] and self.attacking is None:
            self.move_instr_x = self.move_instr_y = 0
            self.attack(wins_dict, fate_rnd, realm.pc)

        if self.attacking is not None:
            return

        if self.waypoints is not None:
            if maths.get_distance(self.x_sq, self.y_sq, self.waypoints[self.wp_index][0],
                                  self.waypoints[self.wp_index][1]) < 0.5:
                self.busy = False
                if self.wp_index == 0:
                    self.waypoints = None
                else:
                    self.dir_to_waypoint(self.wp_ind_list[self.wp_parent_index])
            else:
                wp_x, wp_y = self.waypoints[self.wp_index]
                self.move_instr_x, self.move_instr_y = maths.sign(wp_x - self.x_sq), maths.sign(wp_y - self.y_sq)
        elif not self.busy and pc_distance <= self.stats['aggro_distance'] * (realm.pc.char_sheet.profs['prof_provoke'] + 1000) // 1000:
            self.intercept(wins_dict, pc_distance)
        else:
            if self.bhvr_timer > 0:
                self.bhvr_timer -= 1
            else:
                self.busy = False
                self.direction_change(realm)
                self.phase_change(realm)

    def calc_path(self, realm, xy):
        goal_flag, self.waypoints, self.wp_ind_list = calc2darray.path2d(
            realm.maze.flag_array, {'mov': False}, xy, (round(self.x_sq), round(self.y_sq)), 100, 10, r_max=10
        )
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
        self.rest = False

    def phase_change(self, realm):
        if self.rest:
            self.go()
        else:
            self.wait(realm)

    def go(self):
        self.rest = False
        if self.aggred:
            self.bhvr_timer = self.alert_time
        else:
            self.bhvr_timer = self.active_time + random.randrange(0, self.active_time_spread + 1)

    def wait(self, realm):
        self.bhvr_timer = self.rest_time + random.randrange(0, self.rest_time_spread + 1)
        self.rest = True
        if self.aggred:
            self.aggred = False
            self.calc_path(realm, (round(realm.pc.x_sq), round(realm.pc.y_sq)))

    def stop(self):
        self.alive = False
        self.move_instr_x = self.move_instr_y = 0

    def direction_change(self, realm):
        if self.stats['area_distance'] is None or maths.get_distance(
                self.origin_x_sq, self.origin_y_sq, self.x_sq, self.y_sq
        ) < self.stats['area_distance']:
            dirs_x, dirs_y = self.get_free_dirs(realm)
            self.move_instr_x, self.move_instr_y = random.choice(dirs_x), random.choice(dirs_y)
            return
        if (realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].vis or
                realm.maze.flag_array[round(realm.pc.y_sq)][round(realm.pc.x_sq)].vis):
            self.phase_change(realm)
            return
        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = None
        self.x_sq = self.origin_x_sq
        self.y_sq = self.origin_y_sq
        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = self

    def get_free_dirs(self, realm):
        x_dirs = [0]
        y_dirs = [0]
        try:
            if ((realm.maze.flag_array[round(self.y_sq) + 1][round(self.x_sq)].mon is None
                 or not realm.maze.flag_array[round(self.y_sq) + 1][round(self.x_sq)].mon.alive)
               and realm.maze.flag_array[round(self.y_sq) + 1][round(self.x_sq)].mov):
                y_dirs.append(1)
        except IndexError:
            pass
        try:
            if ((realm.maze.flag_array[round(self.y_sq) - 1][round(self.x_sq)].mon is None
                 or not realm.maze.flag_array[round(self.y_sq) - 1][round(self.x_sq)].mon.alive)
               and realm.maze.flag_array[round(self.y_sq) - 1][round(self.x_sq)].mov):
                y_dirs.append(-1)
        except IndexError:
            pass
        try:
            if ((realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) + 1].mon is None
                 or not realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) + 1].mon.alive)
               and realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) + 1].mov):
                x_dirs.append(1)
        except IndexError:
            pass
        try:
            if ((realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) - 1].mon is None
                 or not realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) - 1].mon.alive)
               and realm.maze.flag_array[round(self.y_sq)][round(self.x_sq) - 1].mov):
                x_dirs.append(-1)
        except IndexError:
            pass
        return x_dirs, y_dirs

    def intercept(self, wins_dict, pc_distance):
        realm = wins_dict['realm']
        self.busy = True
        if calc2darray.cast_ray(realm.maze.flag_array, round(self.x_sq), round(self.y_sq), round(realm.pc.x_sq), round(realm.pc.y_sq), True):
            if self.attack_ranged(realm.pc, wins_dict, pc_distance):
                return
            self.calc_path(realm, (round(realm.pc.x_sq), round(realm.pc.y_sq)))
        elif self.stats['xray'] == 1:
            self.calc_path(realm, (round(realm.pc.x_sq), round(realm.pc.y_sq)))
        else:
            return
        if not self.aggred:
            try:
                realm.sound_inrealm(self.stats['sound_aggro'], self.x_sq, self.y_sq)
            except KeyError:
                pass
            self.aggred = True

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
        dest_x_sq = round(self.x_sq + step_x * self.speed / 100)
        dest_y_sq = round(self.y_sq + step_y * self.speed / 100)

        if not (0 <= dest_x_sq < realm.maze.width):
            dest_x_sq = round(self.x_sq)
            step_x = 0
        if not (0 <= dest_y_sq < realm.maze.height):
            dest_y_sq = round(self.y_sq)
            step_y = 0

        may_x, may_y = self.sq_is_free(realm, dest_x_sq, dest_y_sq)
        step_x *= may_x
        step_y *= may_y

        if step_x == 0 and step_y == 0:
            self.waypoints = None
            self.x_sq = round(self.x_sq)
            self.y_sq = round(self.y_sq)
            self.direction_change(realm)
            return

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = None

        self.x_sq = round(self.x_sq + step_x * self.speed / 100, 2)
        self.y_sq = round(self.y_sq + step_y * self.speed / 100, 2)

        realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = self

    def sq_is_free(self, realm, sq_x, sq_y):
        if round(sq_x) != round(self.x_sq) or round(sq_y) != round(self.y_sq):
            if not realm.maze.flag_array[sq_y][sq_x].mov:
                for yy, xx, sy, sx in (round(self.y_sq), sq_x, 0, 1), (sq_y, round(self.x_sq), 1, 0):
                    if ((realm.maze.flag_array[yy][xx].mon is None or not realm.maze.flag_array[yy][xx].mon.alive)
                       and realm.maze.flag_array[yy][xx].mov):
                        return sx, sy
                return 0, 0
            elif realm.maze.flag_array[sq_y][sq_x].mon is not None and realm.maze.flag_array[sq_y][sq_x].mon.alive:
                realm.maze.flag_array[sq_y][sq_x].mon.waypoints = None
                realm.maze.flag_array[sq_y][sq_x].mon.direction_change(realm)
                return 0, 0
        return 1, 1

    def attack(self, wins_dict, fate_rnd, pc):
        if len(self.stats['attacks_melee']) == 0:
            return False
        self.face_point(pc.x_sq, pc.y_sq)
        self.state_change(self.state + 4)

        attacks_list = [(att, att['chance']) for att in self.stats['attacks_melee']]
        self.attacking = pickrandom.items_get(attacks_list)[0]

        pc.wound(wins_dict, self, self.attacking, fate_rnd)

        wins_dict['realm'].sound_inrealm(self.attacking['sound_attack'], self.x_sq, self.y_sq)

        self.attack_timer = 0

        self.anim_frame = 0
        self.anim_timer = 0
        return True

    def attack_ranged(self, pc, wins_dict, distance):
        if len(self.stats['attacks_ranged']) == 0:
            return False
        self.face_point(pc.x_sq, pc.y_sq)
        self.state_change(self.state + 4)

        attacks_list = [(att, att['chance']) for att in self.stats['attacks_ranged']]
        self.attacking = pickrandom.items_get(attacks_list)[0]

        rnd_attack = random.randrange(self.attacking['attack_val_base'],
                                      self.attacking['attack_val_base'] + self.attacking['attack_val_spread'] + 1)
        if random.randrange(1, 101) <= self.stats['crit_chance']:
            rnd_attack *= 2
            is_crit = True
        else:
            is_crit = False

        anim_pack = (
            self.anim_set['missile_nw'],
            self.anim_set['missile_w']
        )
        speed = 0.1
        wins_dict['realm'].spawn_projectile((self.x_sq, self.y_sq), (pc.x_sq, pc.y_sq),
                                            (rnd_attack, self.attacking['attack_type'], is_crit, self),
                                            speed, anim_pack, collision_limit=1, blast_radius=self.attacking['blast_radius'],
                                            blast_sound=self.attacking['sound_blast'])

        wins_dict['realm'].sound_inrealm(self.attacking['sound_attack'], self.x_sq, self.y_sq)

        self.attack_timer = 0

        self.anim_frame = 0
        self.anim_timer = 0
        return True

    def wound(self, damage, dam_type, ranged, is_crit, wins_dict, fate_rnd, pc, no_reflect=False):
        if not self.alive:
            return
        self.hp -= damage

        wins_dict['realm'].hit_fx(self.x_sq, self.y_sq, dam_type, is_crit)
        # wins_dict['realm'].schedule_man.task_add('realm_tasks', 1, wins_dict['realm'].pygame_settings.audio, 'sound',
        #                             ('hit_physical',))

        if is_crit:
            info_color = 'fnt_header'
            info_size = 20
        else:
            info_color = 'fnt_celeb'
            info_size = 16

        inf_sp_x = maths.sign(pc.x_sq - self.x_sq) * -4
        inf_sp_y = -3
        inf_crit_sp_y = -2
        if is_crit:
            wins_dict['realm'].spawn_realmtext(None, 'Critical hit!', (0, 0), None,
                                  color=info_color, stick_obj=self, speed_xy=(0, inf_crit_sp_y), kill_timer=25,
                                  font='large', size=16, frict_y=0.1)

        wins_dict['realm'].spawn_realmtext(None, str(damage * -1), (0, 0), None,
                              color=info_color, stick_obj=self, speed_xy=(inf_sp_x, inf_sp_y), kill_timer=25,
                              font='large', size=info_size, frict_x=0.1, frict_y=0.15)

        if not no_reflect and self.stats['reflect_attack'] > 0:
            reflected_damage = damage * self.stats['reflect_attack'] // 100
            if reflected_damage > 0:
                attack = {
                    'attack_type': dam_type,
                    'attack_val_base': reflected_damage,
                    'attack_val_spread': 0,
                    'range': ranged
                }
                pc.wound(wins_dict, self, attack, fate_rnd, no_crit=True, no_reflect=True, no_evade=True)

        self.check(wins_dict, fate_rnd, pc)
        if self.alive and not self.attacking and not self.busy:
            self.intercept(wins_dict, maths.get_distance(self.x_sq, self.y_sq, pc.x_sq, pc.y_sq))

    def check(self, wins_dict, fate_rnd, pc):
        if self.hp > 0:
            return
        self.alive = False
        self.anim_frame = 0
        self.state_change(8)

        pc.char_sheet.experience_get(wins_dict, pc, self.stats['exp'])
        if 'affixes' in self.stats:
            for aff in self.stats['affixes']:
                if aff['additional_exp'] is None:
                    continue
                pc.char_sheet.experience_get(wins_dict, pc, self.stats['exp'] * aff['additional_exp'] // 100)

        for mob in wins_dict['realm'].maze.mobs:
            if mob.alive:
                break
        else:
            exp = 100 * wins_dict['realm'].maze.lvl
            pc.char_sheet.experience_get(wins_dict, pc, exp)
            wins_dict['realm'].spawn_realmtext('new_txt', "This place is safer now!", (0, 0), (0, -24), None, pc, None, 120,
                                               'def_bold', 24)
            wins_dict['realm'].spawn_realmtext('new_txt', '%s exp.' % (exp),
                                               (0, 0), (0, -24), 'sun', pc, (0, -2), 60, 'large', 16, 0,
                                               0.17)


        wins_dict['pools'].updated = True
        wins_dict['charstats'].updated = True

        loot_total = lootgen.generate_loot(self, wins_dict['realm'], fate_rnd, pc)
        loot_total.extend(lootgen.generate_gold(self, wins_dict['realm'], fate_rnd, pc))

        lootgen.drop_loot(round(self.x_sq), round(self.y_sq), wins_dict['realm'], loot_total)

        try:
            wins_dict['realm'].sound_inrealm(self.stats['sound_defeat'], self.x_sq, self.y_sq)
        except KeyError:
            pass
        # wins_dict['realm'].maze.flag_array[round(self.y_sq)][round(self.x_sq)].mon = None
        wins_dict['target'].drop_aim()

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
