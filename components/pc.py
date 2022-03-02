from library import maths
from components import treasure
import random


class PC:
    def __init__(self, x_sq, y_sq, location, anim_set, char_sheet, hardcore_char=False, state=2, speed=0.08):
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
        self.alive = True
        self.food_delta = 0
        self.hardcore_char = hardcore_char

        self.move_instr_x = 0
        self.move_instr_y = 0
        self.vision_sq_list = []

        self.location = location
        self.tradepost_level = 1
        self.stage_entry = None
        self.char_sheet = char_sheet
        self.char_portrait_index = 0

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
            self.anim_frame = self.anim_frame % len(self.image)
        self.frame_timing = self.anim_timings[self.anim_frame]

    def tick(self, realm, fate_rnd, wins_dict, active_wins):
        if not self.alive:
            return
        if self.busy is None and (self.move_instr_x != 0 or self.move_instr_y != 0):
            self.move(self.move_instr_x, self.move_instr_y, realm, wins_dict, active_wins)

        elif self.busy is not None:
            if self.busy_timer > self.busy['time']:
                self.busy = None
                if 3 < self.state < 8:
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
            if i[1].cooldown_timer > 0:
                i[1].cooldown_timer -= 1
            else:
                set_upd = True
        if set_upd:
            self.hot_cooling_set = set(filter(lambda x: x[1].cooldown_timer > 0, self.hot_cooling_set))

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
                self.food_change(wins_dict, -2)

                # Light source burns out gradually.
                if self.char_sheet.equipped[6][0] and not treasure.charge_change(self.char_sheet.equipped[6][0], -2):
                    self.char_sheet.equipped[6][0] = None
                    wins_dict['inventory'].updated = True
                    self.char_sheet.calc_stats()
                    wins_dict['realm'].spawn_realmtext(None, 'My torch has burnt out...', (0, 0), (0, -24),
                                                       'fnt_celeb', self, None, 240, 'def_bold', 24)
                    wins_dict['realm'].sound_inrealm('fire_putout', self.x_sq, self.y_sq)

                # visibility update
                realm.calc_vision_alt()
                self.prev_x_sq = self.x_sq
                self.prev_y_sq = self.y_sq

                realm.shortlists_update(everything=True)

                flags = realm.maze.flag_array[int(self.y_sq + 0.4)][int(self.x_sq + 0.4)]

                # Check for traps
                if flags.trap is not None and flags.trap.mode == 1:
                    flags.trap.trigger(wins_dict, self)

                # Check for gold coins on the floor
                if flags.item is None:
                    return
                for itm in flags.item:
                    if itm.props['treasure_id'] == 6:
                        realm.coins_collect(itm, flags.item, self)
                        break

        if self.anim_frame in (1, 3) and self.anim_timer == 0:
            rnd_step_sound = random.choice(
                ('pc_step_01', 'pc_step_02', 'pc_step_03', 'pc_step_04', 'pc_step_05',
                 'pc_step_06', 'pc_step_07'))
            snd_channel = wins_dict['realm'].pygame_settings.audio.sound(rnd_step_sound)
            snd_channel.set_volume(0.4)

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
        if aim_xy is not None:
            self.face_point(aim_xy[0], aim_xy[1])
        if 0 <= self.state < 4:
            self.state_change(self.state + 4)

        self.busy = skill.props

        self.add_cooldowns(wins_dict, skill.props['skill_id'])

        self.busy_timer = 0

        self.anim_frame = 0
        self.anim_timer = 0

    def wound(self, wins_dict, monster, chosen_attack, fate_rnd, no_crit=False, no_reflect=False, no_evade=False):
        inf_sp_x = maths.sign(monster.x_sq - self.x_sq) * -4
        inf_sp_y = 3
        inf_crit_sp_y = 2

        rnd_roll = random.randrange(1, 1001)
        if not no_evade and self.char_sheet.profs['prof_evade'] >= rnd_roll:
            wins_dict['realm'].spawn_realmtext(None, 'Miss!', (0, 0), None,
                                               color='fnt_celeb', stick_obj=self, speed_xy=(0, inf_crit_sp_y),
                                               kill_timer=25, font='large', size=16, frict_y=0.1)
            wins_dict['realm'].pygame_settings.audio.sound('melee_swipe')
            return

        rnd_dmg = random.randrange(chosen_attack['attack_val_base'], chosen_attack['attack_val_base'] + chosen_attack['attack_val_spread'] + 1)
        if not no_crit and random.randrange(1, 101) <= monster.stats['crit_chance'] and rnd_dmg * 2 < self.char_sheet.hp:
            rnd_dmg *= 2
            is_crit = True

        else:
            is_crit = False

        if chosen_attack['range'] > 0:
            pc_def_percent = self.char_sheet.defences['def_ranged']

            if not no_reflect:
                reflected_damage = rnd_dmg * self.char_sheet.profs['prof_reflect'] // 1000
                if reflected_damage > 0:
                    monster.wound(reflected_damage, chosen_attack['attack_type'], chosen_attack['range'], False, wins_dict, fate_rnd, self)
        else:
            pc_def_percent = self.char_sheet.defences['def_melee']

            if not no_reflect:
                thorns_damage = rnd_dmg * self.char_sheet.profs['prof_thorns'] // 1000
                if thorns_damage > 0:
                    monster.wound(thorns_damage, chosen_attack['attack_type'], chosen_attack['range'], False, wins_dict, fate_rnd, self)

        pc_def_points = self.char_sheet.defences[self.char_sheet.att_def_dict[chosen_attack['attack_type']]]
        damage = rnd_dmg - (rnd_dmg * pc_def_percent / 1000)
        damage = max(1, round(damage - damage * (pc_def_points / (pc_def_points + monster.stats['lvl'] * 20))))

        # Last HP last chance.
        if damage > self.char_sheet.hp > 1:
            damage = self.char_sheet.hp - 1

        self.char_sheet.hp_get(damage * -1)

        wins_dict['realm'].hit_fx(self.x_sq, self.y_sq, chosen_attack['attack_type'], is_crit, for_pc=True, forced_sound=False)

        # 100% HP damage = 10 points of condition
        if treasure.condition_equipment_change(self.char_sheet, round(-10 * rnd_dmg / self.char_sheet.pools['HP'])):
            self.char_sheet.calc_stats()

        wins_dict['pools'].updated = True

        if not no_crit and is_crit:
            info_color = 'fnt_attent'
            info_size = 20

        else:
            info_color = 'fnt_attent'
            info_size = 16

        if not no_crit and is_crit:
            wins_dict['realm'].spawn_realmtext(None, 'Critical hit!', (0, 0), None,
                                               color=info_color, stick_obj=self, speed_xy=(0, inf_crit_sp_y),
                                               kill_timer=25,
                                               font='large', size=16, frict_y=0.1)
            wins_dict['realm'].pygame_settings.audio.sound('hit_blast')

        wins_dict['realm'].spawn_realmtext(None, str(damage * -1), (0, 0), None,
                                           color=info_color, stick_obj=self, speed_xy=(inf_sp_x, inf_sp_y),
                                           kill_timer=25,
                                           font='large', size=info_size, frict_x=0.1, frict_y=0.15)

        if self.char_sheet.hp <= 0:
            self.state_change(8)
            wins_dict['realm'].pygame_settings.audio.sound('death_%s' % self.char_sheet.type)
            self.char_sheet.gold_coins -= self.char_sheet.gold_coins // 2

            if treasure.condition_equipment_change(self.char_sheet, -100):
                self.char_sheet.calc_stats()

            if self.hardcore_char:
                self.hardcore_char = 2
                wins_dict['demos'].death_hardcore(self, monster.stats, wins_dict['realm'].maze.chapter)
            else:
                self.char_sheet.hp_get(100, percent=True)
                wins_dict['demos'].death_soft(self, monster.stats, wins_dict['realm'].maze.chapter)

    def add_cooldowns(self, wins_dict, skill_id):
        """if 'skill_id' in socket.tags[0][socket.id].props:
            self.hot_cooling_set.add((socket, socket.tags[0][socket.id]))
        elif ('treasure_id' in socket.tags[0][socket.id].props
                and socket.tags[0][socket.id].props['use_skill']):
            self.hot_cooling_set.add((socket, socket.tags[0][socket.id].props['use_skill']))"""

        for i in range(0, len(self.char_sheet.skills)):
            if self.char_sheet.skills[i] is None:
                continue
            if self.char_sheet.skills[i].props['skill_id'] == skill_id:
                self.char_sheet.skills[i].cooldown_timer = self.char_sheet.skills[i].props['cooldown']
                self.hot_cooling_set.add((wins_dict['skillbook'].skb_sockets_list[i], self.char_sheet.skills[i]))

        for i in range(0, len(self.char_sheet.inventory)):
            if self.char_sheet.inventory[i] is None:
                continue
            if self.char_sheet.inventory[i].props['use_skill'] is None:
                continue
            if self.char_sheet.inventory[i].props['use_skill'].props['skill_id'] == skill_id:
                self.char_sheet.inventory[i].props['use_skill'].cooldown_timer = self.char_sheet.inventory[i].props['use_skill'].props['cooldown']
                self.hot_cooling_set.add((wins_dict['inventory'].inv_sockets_list[i], self.char_sheet.inventory[i].props['use_skill']))

        for i in range(0, len(self.char_sheet.equipped)):
            if self.char_sheet.equipped[i] is None:
                continue
            for j in range(0, len(self.char_sheet.equipped[i])):
                if self.char_sheet.equipped[i][j] is None:
                    continue
                if self.char_sheet.equipped[i][j].props['use_skill'] is None:
                    continue
                if self.char_sheet.equipped[i][j].props['use_skill'].props['skill_id'] == skill_id:
                    self.char_sheet.equipped[i][j].props['use_skill'].cooldown_timer = self.char_sheet.equipped[i][j].props['use_skill'].props['cooldown']
                    self.hot_cooling_set.add((wins_dict['equipped'].eq_sockets_list[i], self.char_sheet.equipped[i][j].props['use_skill']))

        for i in range(0, len(self.char_sheet.hotbar)):
            if self.char_sheet.hotbar[i] is None:
                continue
            if 'treasure_id' in self.char_sheet.hotbar[i].props:
                if self.char_sheet.hotbar[i].props['use_skill'] is None:
                    continue
                if self.char_sheet.hotbar[i].props['use_skill'].props['skill_id'] == skill_id:
                    self.char_sheet.hotbar[i].props['use_skill'].cooldown_timer = \
                    self.char_sheet.hotbar[i].props['use_skill'].props['cooldown']
                    self.hot_cooling_set.add(
                        (wins_dict['hotbar'].hot_sockets_list[i], self.char_sheet.hotbar[i].props['use_skill']))
            elif 'skill_id' in self.char_sheet.hotbar[i].props:
                if self.char_sheet.hotbar[i].props['skill_id'] == skill_id:
                    self.char_sheet.hotbar[i].cooldown_timer = self.char_sheet.hotbar[i].props['cooldown']
                    self.hot_cooling_set.add((wins_dict['hotbar'].hot_sockets_list[i], self.char_sheet.hotbar[i]))

    def moved_item_cooldown_check(self, item, socket):
        if 'skill_id' in item.props:
            for hcs in self.hot_cooling_set:
                if item == hcs[1]:
                    self.hot_cooling_set.remove(hcs)
                    self.hot_cooling_set.add((socket, item))
                    break
            else:
                for hcs in self.hot_cooling_set:
                    if item.props['skill_id'] == hcs[1].props['skill_id']:
                        item.cooldown_timer = hcs[1].cooldown_timer
                        self.hot_cooling_set.add((socket, item))
                        break
        elif 'treasure_id' in item.props and item.props['use_skill'] is not None:
            for hcs in self.hot_cooling_set:
                if item.props['use_skill'] == hcs[1]:
                    self.hot_cooling_set.remove(hcs)
                    self.hot_cooling_set.add((socket, item.props['use_skill']))
                    break
            else:
                for hcs in self.hot_cooling_set:
                    if item.props['use_skill'].props['skill_id'] == hcs[1].props['skill_id']:
                        item.props['use_skill'].cooldown_timer = hcs[1].cooldown_timer
                        self.hot_cooling_set.add((socket, item.props['use_skill']))
                        break

    def state_change(self, new_state):
        # check if state change is possible
        if self.state == new_state:
            return

        # change state
        self.state = new_state
        self.animate()

    def food_change(self, wins_dict, value):
        if self.char_sheet.food > 0:
            self.char_sheet.food_get(value)
            self.food_delta += abs(value)
        else:
            self.state_change(8)
            if self.hardcore_char:
                self.hardcore_char = 2
                wins_dict['demos'].death_hardcore(self, {'label': 'hunger'}, wins_dict['realm'].maze.chapter)
            else:
                self.char_sheet.food_get(100, percent=True)
                wins_dict['demos'].death_soft(self, {'label': 'hunger'}, wins_dict['realm'].maze.chapter)
        if self.food_delta >= 20:
            wins_dict['pools'].updated = True
            self.food_delta = 0

    def stop(self):
        self.alive = False
        self.move_instr_x = self.move_instr_y = 0

    def ready(self):
        self.alive = True
        self.state = 0
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
