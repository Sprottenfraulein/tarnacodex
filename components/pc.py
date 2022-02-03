from library import maths
import random


class PC:
    def __init__(self, x_sq, y_sq, location, anim_set, char_sheet, state=2, speed=0.08):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.prev_x_sq = self.x_sq
        self.prev_y_sq = self.y_sq
        self.off_x = self.off_y = 0
        self.speed = speed
        self.busy_timer = 0
        self.busy = None
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

        self.hot_cooling_set = set()

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
        if self.busy is None and (self.move_instr_x != 0 or self.move_instr_y != 0):
            self.move(self.move_instr_x, self.move_instr_y, realm, wins_dict, active_wins)

        elif self.busy is not None:
            if self.busy_timer > self.busy['time']:
                self.busy = None
                if self.state > 3:
                    self.state_change(self.state - 4)
            else:
                self.busy_timer += 1

        if self.busy is not None or (self.move_instr_x != 0 or self.move_instr_y != 0):
            if self.anim_timer > self.frame_timing:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= len(self.image):
                    self.anim_frame -= len(self.image)
                self.frame_timing = self.anim_timings[self.anim_frame]
            else:
                self.anim_timer += 1

        if not self.hot_cooling_set:
            return

        set_upd = False
        for i in self.hot_cooling_set:
            cooling_skill = i.tags[0][i.id]
            if cooling_skill.cooldown_timer > 0:
                cooling_skill.cooldown_timer -= 1
            else:
                set_upd = True
        if set_upd:
            self.hot_cooling_set = set(filter(lambda x: x.tags[0][x.id].cooldown_timer > 0, self.hot_cooling_set))

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

        if not (0 <= dest_x_sq < realm.maze.width) or not (0 <= dest_y_sq < realm.maze.height):
            return
        """if not realm.maze.flag_array[dest_y_sq][dest_x_sq].mov:
            if realm.maze.flag_array[round(self.y_sq)][dest_x_sq].mov:
                step_y = 0
            elif realm.maze.flag_array[dest_y_sq][round(self.x_sq)].mov:
                step_x = 0
            else:
                return"""
        may_x, may_y = self.sq_is_free(realm, dest_x_sq, dest_y_sq)
        step_x *= may_x
        step_y *= may_y


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

                self.char_sheet.food -= 5
                if not self.char_sheet.food % 20:
                    wins_dict['pools'].updated = True

                realm.shortlists_update(everything=True)

                flags = realm.maze.flag_array[int(self.y_sq + 0.5)][int(self.x_sq + 0.5)]
                if flags.item is None:
                    return
                for itm in flags.item:
                    if itm.props['treasure_id'] == 6:
                        self.char_sheet.gold_coins += itm.props['amount']
                        realm.maze.loot.remove(itm)
                        # realm.loot_short.remove(itm)
                        if wins_dict['inventory'] in active_wins:
                            wins_dict['inventory'].render()
                        flags.item.remove(itm)
                        break

    def sq_is_free(self, realm, sq_x, sq_y):
        step_x, step_y = 1, 1
        if sq_x != round(self.x_sq) or sq_y != round(self.y_sq):
            if realm.maze.flag_array[sq_y][sq_x].mon is not None and realm.maze.flag_array[sq_y][sq_x].mon.alive:
                if realm.maze.flag_array[round(self.y_sq)][sq_x].mon is None or not realm.maze.flag_array[round(self.y_sq)][sq_x].mon.alive:
                    step_y = 0
                    # self.move_instr_x *= -1
                elif realm.maze.flag_array[sq_y][round(self.x_sq)].mon is None or not realm.maze.flag_array[sq_y][round(self.x_sq)].mon.alive:
                    step_x = 0
                    # self.move_instr_y *= -1
                else:
                    step_x = step_y = 0
            if not realm.maze.flag_array[sq_y][sq_x].mov:
                if realm.maze.flag_array[round(self.y_sq)][sq_x].mov:
                    step_y = 0
                    # self.move_instr_x *= -1

                elif realm.maze.flag_array[sq_y][round(self.x_sq)].mov:
                    step_x = 0
                    # self.move_instr_y *= -1
                else:
                    step_x = step_y = 0
        return step_x, step_y

    def act(self, wins_dict, aim_xy, skill):
        self.face_point(aim_xy[0], aim_xy[1])
        self.state_change(self.state + 4)

        self.busy = skill.props
        skill.cooldown_timer = skill.props['cooldown']
        self.check_cooldowns(wins_dict)

        self.busy_timer = 0

        self.anim_frame = 0
        self.anim_timer = 0

    def wound(self, wins_dict, monster, chosen_attack):
        if chosen_attack['range'] > 0:
            pc_def = self.char_sheet.defences['def_ranged']
        else:
            pc_def = self.char_sheet.defences['def_melee']

        pc_def += self.char_sheet.defences[self.char_sheet.att_def_dict[chosen_attack['attack_type']]]  # Sum in percents

        rnd_dmg = random.randrange(chosen_attack['attack_val_base'], chosen_attack['attack_val_base'] + chosen_attack['attack_val_spread'])
        if random.randrange(1, 101) <= monster.stats['crit_chance']:
            rnd_dmg *= 4
            is_crit = True
        else:
            is_crit = False

        damage = rnd_dmg - (rnd_dmg * pc_def // 1000)

        self.char_sheet.hp_get(rnd_dmg * -1)

        wins_dict['pools'].updated = True

        if is_crit:
            info_color = 'fnt_attent'
            info_size = 20
        else:
            info_color = 'fnt_attent'
            info_size = 16

        inf_sp_x = maths.sign(monster.x_sq - self.x_sq) * -4
        inf_sp_y = 3
        inf_crit_sp_y = 2
        if is_crit:
            wins_dict['realm'].spawn_realmtext(None, 'Critical hit!', (0, 0), None,
                                               color=info_color, stick_obj=self, speed_xy=(0, inf_crit_sp_y),
                                               kill_timer=25,
                                               font='large', size=16, frict_y=0.1)

        wins_dict['realm'].spawn_realmtext(None, str(damage * -1), (0, 0), None,
                                           color=info_color, stick_obj=self, speed_xy=(inf_sp_x, inf_sp_y),
                                           kill_timer=25,
                                           font='large', size=info_size, frict_x=0.1, frict_y=0.15)

    def check_cooldowns(self, wins_dict):
        hotbar = wins_dict['hotbar']
        for sckt in hotbar.hot_sockets_list:
            if sckt.tags[0][sckt.id] is not None and self.busy == sckt.tags[0][sckt.id].props:
                self.hot_cooling_set.add(sckt)

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
