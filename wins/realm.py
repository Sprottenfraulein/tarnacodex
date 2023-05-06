import pygame
import random
from library import calc2darray, maths, logfun, typography, particle
from components import realmtext, skillfuncs, projectile, maze
import math


class Realm:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man):
        self.pygame_settings = pygame_settings
        self.resources = resources
        self.tilesets = tilesets
        self.animations = animations
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.wins_dict = None
        self.active_wins = None

        self.doors_short = set()
        self.traps_short = set()
        self.loot_short = set()
        self.mobs_short = []

        self.loot_spawn_list = []
        self.text_short = []
        self.missiles_list = []
        self.jumping_objects = []
        self.particle_list = []

        self.draw_view_maze = False

        self.redraw_maze_decor = True
        self.redraw_maze_obj = True
        self.redraw_maze_loot = True
        self.redraw_maze_mobs = True
        self.redraw_maze_text = True
        self.redraw_missiles = True
        self.redraw_particles = True

        self.redraw_pc = True
        self.square_size = 24
        self.square_scale = 2
        self.view_bleed_sq = 1
        self.view_maze_top = 24
        self.view_maze_left = 24
        self.view_maze_x_sq = 0
        self.view_maze_y_sq = 0
        self.view_maze_h_div = 2  # 2 - center , 3 - char to the left, 1.5 - char to the right
        self.view_maze_v_div = 2.6
        self.view_maze_width_sq = math.ceil(self.pygame_settings.screen_res[0] / self.square_scale / self.square_size)
        self.view_maze_height_sq = math.ceil(self.pygame_settings.screen_res[1] / self.square_scale / self.square_size)

        self.view_offset_x_sq = round(self.view_maze_width_sq / 2) * -1
        self.view_offset_y_sq = round(self.view_maze_height_sq / 2) * -1

        self.ren_x_sq, self.ren_y_sq = 0, 0

        self.view_size_scaled = self.pygame_settings.screen_res

        self.view_maze_follow = None
        self.maze = None
        self.pc = None

        self.location_label = typography.Typography(self.pygame_settings, 'Player character location', (
            self.view_size_scaled[0], 0
        ), 'def_normal', 24, self.resources.colors['sun'], self.resources.colors['bg'],
                                                    'right', 'top', self.view_size_scaled[0] // 2, 24, shadow=True)

        self.view_maze_surface = None
        self.vision_sq_prev = None
        self.shade_color = self.border_color = self.bg_color = None
        self.set_shadings((0, 0, 0))

        self.dark_edges = self.dark_edges_get(self.tilesets.sets_dict['dark_edges'], self.border_color)
        self.shade_square = pygame.Surface((24, 24)).convert_alpha()
        self.shade_square.fill(self.shade_color)
        self.target_mark = self.tilesets.get_image('interface', (24, 24), (10, 11, 12, 13))

        self.pause = False
        self.controls_enabled = True

        self.buttons_pressed = set()
        self.last_skill = None
        self.last_skill_timer = 60

        self.vision_dist = 0

    def dark_edges_get(self, tiles, shade_color):
        tiles.set_colorkey((0,0,0), pygame.RLEACCEL)
        self.tilesets.sets_dict['dark_edges_color'] = pygame.Surface(tiles.get_size()).convert()
        self.tilesets.sets_dict['dark_edges_color'].fill(shade_color)
        self.tilesets.sets_dict['dark_edges_color'].blit(tiles, (0,0))
        self.tilesets.sets_dict['dark_edges_color'].set_colorkey((0,255,0), pygame.RLEACCEL)
        return self.tilesets.get_image('dark_edges_color', (24, 24), (0, 1, 2, 3))

    def set_shadings(self, color):
        self.shade_color = color
        self.border_color = color[0] // 3, color[1] // 3, color[2] // 3
        self.bg_color = color[0] // 4, color[1] // 4, color[2] // 4

    def view_resize(self, w, h):
        self.view_maze_width_sq = math.ceil(w / self.square_scale / self.square_size)
        self.view_maze_height_sq = math.ceil(h / self.square_scale / self.square_size)
        if (self.view_maze_surface is None or self.view_maze_surface.get_rect().size
                != ((self.view_maze_width_sq + self.view_bleed_sq * 2) * self.square_size,
                    (self.view_maze_height_sq + self.view_bleed_sq * 2) * self.square_size)):
            self.view_maze_surface = pygame.Surface(
                ((self.view_maze_width_sq + self.view_bleed_sq * 2) * self.square_size,
                 (self.view_maze_height_sq + self.view_bleed_sq * 2) * self.square_size),
                pygame.HWSURFACE).convert()
        self.view_size_scaled = (w, h)
        framed_wins = (
            self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'],
            self.wins_dict['inventory'], self.wins_dict['skillbook'], self.wins_dict['debuffs']
        )
        for win in framed_wins:
            win.offset_x, win.offset_y = maths.rect_sticky_edges((win.offset_x, win.offset_y, win.win_w, win.win_h),
                                                                 [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow
                                                                  in framed_wins])
            win.offset_x, win.offset_y = maths.rect_in_bounds(win.offset_x, win.offset_y, win.win_w, win.win_h, 0,
                                                              0, w, h)
        self.location_label.x = self.view_size_scaled[0]
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)

    def launch(self):
        self.set_shadings(self.resources.colors[self.maze.shading_color])
        self.dark_edges = self.dark_edges_get(self.tilesets.sets_dict['dark_edges'], self.border_color)
        self.shade_square.fill(self.shade_color)

        self.wins_dict['realm'].view_resize(self.pygame_settings.screen_res[0], self.pygame_settings.screen_res[1])
        # creating dedicated schedule
        self.schedule_man.new_schedule('realm_tasks')
        # game pack must include dungeon set, character
        self.view_maze_follow = self.pc
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
        # visibility update
        self.calc_vision_alt()
        # creating shortlists
        self.doors_short.clear()
        self.traps_short.clear()
        self.loot_short.clear()
        self.mobs_short.clear()
        self.particle_list.clear()
        self.missiles_list.clear()

        self.text_short.clear()

        self.shortlists_update(everything=True)
        self.location_label_update()
        self.render_update()

        if self.wins_dict['hotbar'].pc != self.pc:
            self.wins_dict['hotbar'].launch(self.pc)
        if self.wins_dict['inventory'].pc != self.pc:
            self.wins_dict['inventory'].launch(self.pc)
        if self.wins_dict['skillbook'].pc != self.pc:
            self.wins_dict['skillbook'].launch(self.pc)
        if self.wins_dict['pools'].pc != self.pc:
            self.wins_dict['pools'].launch(self.pc)
        if self.wins_dict['tasks'].pc != self.pc:
            self.wins_dict['tasks'].launch(self.pc)

        self.wins_dict['map'].restart(self.pc)

        if self.wins_dict['pools'] not in self.active_wins:
            self.active_wins.insert(0, self.wins_dict['pools'])
        if self.wins_dict['hotbar'] not in self.active_wins:
            self.active_wins.insert(0, self.wins_dict['hotbar'])

        self.wins_dict['target'].drop_aim()
        self.wins_dict['debuffs'].update(self.pc)

        self.pc.ready()
        self.pause = False
        self.controls_enabled = True

    def event_check(self, event, log=False):
        if not self.pc.alive or not self.controls_enabled:
            pygame.event.clear()
            return
        # character and gui controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.buttons_pressed.add(1)
            elif event.key == pygame.K_2:
                self.buttons_pressed.add(2)
            elif event.key == pygame.K_3:
                self.buttons_pressed.add(3)
            elif event.key == pygame.K_4:
                self.buttons_pressed.add(4)
            elif event.key == pygame.K_5:
                self.buttons_pressed.add(5)
            elif event.key == pygame.K_6:
                self.buttons_pressed.add(6)
            elif event.key == pygame.K_7:
                self.buttons_pressed.add(7)
            elif event.key == pygame.K_8:
                self.buttons_pressed.add(8)
            elif event.key == pygame.K_9:
                self.buttons_pressed.add(9)
            elif event.key == pygame.K_0:
                self.buttons_pressed.add(0)

            if event.key == pygame.K_v:
                self.view_offset_x_sq = round(self.mouse_pointer.xy[0] / self.square_size / self.square_scale) * -1
                self.view_offset_y_sq = round(self.mouse_pointer.xy[1] / self.square_size / self.square_scale) * -1
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
            if event.key == pygame.K_m:
                self.wins_dict['map'].restart(self.pc)

            # CHANGE SCALE
            if event.key == pygame.K_KP_PLUS and self.square_scale < 4:
                self.pc.x_sq = round(self.pc.x_sq)
                self.pc.y_sq = round(self.pc.y_sq)
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
                self.square_scale += 1
                self.view_maze_width_sq = math.ceil(
                    self.pygame_settings.screen_res[0] / self.square_scale / self.square_size)
                self.view_maze_height_sq = math.ceil(
                    self.pygame_settings.screen_res[1] / self.square_scale / self.square_size)
                self.view_offset_x_sq = round(self.view_maze_width_sq / 2) * -1
                self.view_offset_y_sq = round(self.view_maze_height_sq / 2) * -1
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
            if event.key == pygame.K_KP_MINUS and self.square_scale > 2:
                self.pc.x_sq = round(self.pc.x_sq)
                self.pc.y_sq = round(self.pc.y_sq)
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
                self.square_scale -= 1
                self.view_maze_width_sq = math.ceil(
                    self.pygame_settings.screen_res[0] / self.square_scale / self.square_size)
                self.view_maze_height_sq = math.ceil(
                    self.pygame_settings.screen_res[1] / self.square_scale / self.square_size)
                self.view_offset_x_sq = round(self.view_maze_width_sq / 2) * -1
                self.view_offset_y_sq = round(self.view_maze_height_sq / 2) * -1
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)

            if event.key == pygame.K_p:
                pass
            if event.key == pygame.K_m:
                self.schedule_man.task_add('realm_tasks', 6, self, 'spawn_realmtext',
                                           ('new_txt', "I'd better have a black muffin.",
                                            (0, 0), (0, -24), None, self.pc, None, 120, 'def_bold', 24))

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_1:
                self.buttons_pressed.discard(1)
            elif event.key == pygame.K_2:
                self.buttons_pressed.discard(2)
            elif event.key == pygame.K_3:
                self.buttons_pressed.discard(3)
            elif event.key == pygame.K_4:
                self.buttons_pressed.discard(4)
            elif event.key == pygame.K_5:
                self.buttons_pressed.discard(5)
            elif event.key == pygame.K_6:
                self.buttons_pressed.discard(6)
            elif event.key == pygame.K_7:
                self.buttons_pressed.discard(7)
            elif event.key == pygame.K_8:
                self.buttons_pressed.discard(8)
            elif event.key == pygame.K_9:
                self.buttons_pressed.discard(9)
            elif event.key == pygame.K_0:
                self.buttons_pressed.discard(0)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # removing popup if active
            if self.wins_dict['context'] in self.active_wins:
                self.active_wins.remove(self.wins_dict['context'])
            if self.mouse_pointer.drag_item is not None:
                return

            if event.button == 1:
                self.buttons_pressed.add(11)
            if event.button == 3:
                self.buttons_pressed.add(13)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.buttons_pressed.discard(11)
            if event.button == 3:
                self.buttons_pressed.discard(13)

            if event.button != 1:
                return
            self.pc.move_instr_x = self.pc.move_instr_y = 0

            if self.mouse_pointer.drag_item is None:
                return
            self.pc_loot_drop(self.mouse_pointer.xy, log)

        elif event.type == pygame.MOUSEMOTION:
            if self.wins_dict['context'] in self.active_wins:
                self.active_wins.remove(self.wins_dict['context'])
            self.mob_check(self.mouse_pointer.xy, None)
            if self.pc.move_instr_y != 0 or self.pc.move_instr_x != 0:
                self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(self.mouse_pointer.xy)

    def hot_activate(self, index, no_aim):
        if 'skill_id' in self.pc.char_sheet.hotbar[index].props:
            return getattr(skillfuncs, self.pc.char_sheet.hotbar[index].props['function_name'])(
                self.wins_dict, self.resources.fate_rnd, self.pc, self.pc.char_sheet.hotbar[index],
                (self.pc.char_sheet.hotbar, index), no_aim
            )
        elif ('treasure_id' in self.pc.char_sheet.hotbar[index].props
              and self.pc.char_sheet.hotbar[index].props['use_skill'] is not None):
            return getattr(skillfuncs, self.pc.char_sheet.hotbar[index].props['use_skill'].props['function_name'])(
                self.wins_dict, self.resources.fate_rnd, self.pc, self.pc.char_sheet.hotbar[index].props['use_skill'],
                (self.pc.char_sheet.hotbar, index), no_aim
            )
        return True

    def tick(self):
        if self.pause:
            return

        if self.last_skill_timer > 0:
            self.last_skill_timer -= 1
        elif self.last_skill is not None:
            self.last_skill = None

        self.controls()

        self.maze.tick()
        self.pc.tick(self, self.resources.fate_rnd, self.wins_dict, self.active_wins)
        for mob in self.mobs_short:
            mob.tick(self.wins_dict, self.resources.fate_rnd, self)

        for i in range(len(self.text_short) - 1, -1, -1):
            self.text_short[i].tick()

        for i in range(len(self.missiles_list) - 1, -1, -1):
            if not self.missiles_list[i].tick(self.wins_dict, self.resources.fate_rnd):
                del self.missiles_list[i]

        for i in range(len(self.particle_list) - 1, -1, -1):
            if not self.particle_list[i].tick():
                del self.particle_list[i]

        if len(self.loot_spawn_list) > 0 and self.schedule_man.frame == 0:
            self.loot_spawn_add(*self.loot_spawn_list.pop())

        self.obj_jump(self.jumping_objects)

        self.monster_sound_ambience()

        self.render_update()

    def controls(self):
        if 1 in self.buttons_pressed and self.pc.char_sheet.hotbar[0] is not None:
            self.hot_activate(0, True)
        if 2 in self.buttons_pressed and self.pc.char_sheet.hotbar[1] is not None:
            self.hot_activate(1, True)
        if 3 in self.buttons_pressed and self.pc.char_sheet.hotbar[2] is not None:
            self.hot_activate(2, True)
        if 4 in self.buttons_pressed and self.pc.char_sheet.hotbar[3] is not None:
            self.hot_activate(3, True)
        if 5 in self.buttons_pressed and self.pc.char_sheet.hotbar[4] is not None:
            self.hot_activate(4, True)
        if 6 in self.buttons_pressed and self.pc.char_sheet.hotbar[5] is not None:
            self.hot_activate(5, True)
        if 7 in self.buttons_pressed and self.pc.char_sheet.hotbar[6] is not None:
            self.hot_activate(6, True)
        if 8 in self.buttons_pressed and self.pc.char_sheet.hotbar[7] is not None:
            self.hot_activate(7, True)
        if 9 in self.buttons_pressed and self.pc.char_sheet.hotbar[8] is not None:
            self.hot_activate(8, True)
        if 0 in self.buttons_pressed and self.pc.char_sheet.hotbar[9] is not None:
            self.hot_activate(9, True)

        can_move = True
        if 11 in self.buttons_pressed and self.pc.char_sheet.hotbar[-2] is not None and self.pc.move_instr_x == self.pc.move_instr_y == 0:
            can_move = self.hot_activate(-2, False)
        if 13 in self.buttons_pressed and self.pc.char_sheet.hotbar[-1] is not None:
            self.hot_activate(-1, False)

        if can_move and 11 in self.buttons_pressed and self.pc.move_instr_x == self.pc.move_instr_y == 0:
            can_move = self.square_check(self.mouse_pointer.xy)
        if can_move and 11 in self.buttons_pressed:
            self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(self.mouse_pointer.xy)

    def draw(self, surface):
        self.stage_display(surface)

    def stage_display(self, screen):
        # world and gui drawing
        if not self.draw_view_maze:
            return

        # screen.blit(self.view_maze_surface, (self.view_maze_left, self.view_maze_top))
        pygame.transform.scale(self.view_maze_surface.subsurface(
            (round((self.view_bleed_sq - (self.ren_x_sq - self.view_maze_x_sq)) * self.square_size),
             round((self.view_bleed_sq - (self.ren_y_sq - self.view_maze_y_sq)) * self.square_size),
             self.view_maze_width_sq * self.square_size,
             self.view_maze_height_sq * self.square_size,)
        ), self.view_size_scaled, screen)

        if self.redraw_maze_text:
            for txt in self.text_short:
                txt.draw(screen,
                         (
                                     txt.x_sq - self.view_maze_x_sq - self.view_bleed_sq) * self.square_size * self.square_scale + txt.off_x,
                         (
                                     txt.y_sq - self.view_maze_y_sq - self.view_bleed_sq) * self.square_size * self.square_scale + txt.off_y)

        screen.blit(self.location_label.rendered_text, self.location_label.rendered_rect)

    def view_maze_update(self, x_sq, y_sq):
        self.view_maze_x_sq = x_sq + self.view_offset_x_sq
        self.view_maze_y_sq = y_sq + self.view_offset_y_sq

    def render_update(self):
        self.ren_x_sq = round(self.view_maze_x_sq)
        self.ren_y_sq = round(self.view_maze_y_sq)
        r_vm_x_sq = round(self.view_maze_x_sq - self.view_bleed_sq)
        r_vm_y_sq = round(self.view_maze_y_sq - self.view_bleed_sq)
        self.stage_render(self.view_maze_surface, r_vm_y_sq, r_vm_x_sq,
                          r_vm_y_sq + self.view_maze_height_sq + self.view_bleed_sq * 3,
                          r_vm_x_sq + self.view_maze_width_sq + self.view_bleed_sq * 3)

        if self.redraw_missiles:
            for missile in self.missiles_list:
                if self.maze.flag_array[round(missile.y_sq)][round(missile.x_sq)].vis:
                    self.view_maze_surface.blit(missile.image_strip[missile.frame_index],
                                                ((missile.x_sq - self.ren_x_sq) * self.square_size + missile.off_x,
                                                 (missile.y_sq - self.ren_y_sq) * self.square_size + missile.off_y))

        if self.redraw_particles:
            for part in self.particle_list:
                if self.maze.flag_array[round(part.y)][round(part.x)].vis:
                    self.view_maze_surface.blit(part.image_strip[part.frame_index],
                                                (round((part.x - self.ren_x_sq) * self.square_size + part.off_x),
                                                 round((part.y - self.ren_y_sq) * self.square_size + part.off_y)))

        self.draw_view_maze = True

    def stage_render(self, surface, top_sq, left_sq, bottom_sq, right_sq, clear=True):
        if clear:
            surface.fill(self.bg_color)
        for ren_pos_y in range(top_sq, bottom_sq):
            for ren_pos_x in range(left_sq, right_sq):
                if not ((0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width)):
                    continue
                flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                decor_array = self.maze.decor_array[ren_pos_y][ren_pos_x]
                if decor_array == ' ' or not flags.vis or decor_array[0] is None:
                    continue
                surface.blit(decor_array[0],
                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                              (ren_pos_y - self.ren_y_sq) * self.square_size))
                if flags.trap is not None and flags.trap.visible == 1:
                    surface.blit(flags.trap.images[self.maze.anim_frame % len(flags.trap.images)],
                                 ((flags.trap.x_sq - self.ren_x_sq) * self.square_size + flags.trap.off_x,
                                  (flags.trap.y_sq - self.ren_y_sq) * self.square_size + flags.trap.off_y))
                if self.pc.path is not None:
                    for wp in self.pc.path:
                        if wp[0] != ren_pos_x or wp[1] != ren_pos_y:
                            continue
                        surface.blit(self.target_mark[0],
                                     ((wp[0] - self.ren_x_sq + 0.15) * self.square_size,
                                      (wp[1] - self.ren_y_sq + 0.2) * self.square_size))

        for ren_pos_y in range(top_sq, bottom_sq):
            for ren_pos_x in range(left_sq, right_sq):
                if not ((0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width)):
                    continue
                flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                decor_array = self.maze.decor_array[ren_pos_y][ren_pos_x]
                if decor_array == ' ' or not flags.vis:
                    continue
                # drawing doors
                if flags.door is not None:
                    obj_image = flags.door.image[self.maze.anim_frame % len(flags.door.image)]
                    self.render_by_square(surface, ren_pos_x, ren_pos_y, flags.door, obj_image, self.maze.flag_array)

                if flags.obj is not None and not flags.obj.render_later:
                    obj_image = flags.obj.image[self.maze.anim_frame % len(flags.obj.image)]
                    self.render_by_square(surface, ren_pos_x, ren_pos_y, flags.obj, obj_image, self.maze.flag_array)

                # drawing loot
                if flags.item is not None:
                    offset = 0
                    for loot in flags.item:
                        try:
                            surface.blit(loot.props['image_floor'][self.maze.anim_frame],
                                         ((loot.x_sq - self.ren_x_sq + loot.off_x_sq) * self.square_size - offset,
                                          (loot.y_sq - self.ren_y_sq + loot.off_y_sq) * self.square_size - offset))
                        except IndexError:
                            surface.blit(
                                loot.props['image_floor'][
                                    (self.maze.anim_frame + 1) % (len(loot.props['image_floor']))],
                                ((loot.x_sq - self.ren_x_sq + loot.off_x_sq) * self.square_size - offset,
                                 (loot.y_sq - self.ren_y_sq + loot.off_y_sq) * self.square_size - offset))
                        offset += 4

                # mobs rendering
                if flags.mon is not None:
                    mon = flags.mon
                    if mon.aimed:
                        surface.blit(self.target_mark[self.maze.anim_frame],
                                     ((mon.x_sq - self.ren_x_sq + 0.15 + mon.off_x) * self.square_size,
                                      (mon.y_sq - self.ren_y_sq + 0.2 + mon.off_y) * self.square_size))
                    """if mon.waypoints is not None:
                        for wp in mon.waypoints:
                            surface.blit(self.target_mark[0],
                                         ((wp[0] - self.ren_x_sq + 0.15) * self.square_size,
                                          (wp[1] - self.ren_y_sq + 0.2) * self.square_size))"""
                    surface.blit(mon.image[mon.anim_frame],
                                 ((mon.x_sq - self.ren_x_sq - 0.1 + mon.off_x) * self.square_size,
                                  (mon.y_sq - self.ren_y_sq - 0.1 + mon.off_y) * self.square_size))
                    if mon.stats['grade']['grade_level'] > 0 and mon.hp > 0:
                        surface.blit(mon.anim_set['affix_mark']['images'][self.maze.anim_frame],
                                     ((mon.x_sq - self.ren_x_sq - 0.4 + mon.off_x) * self.square_size,
                                      (mon.y_sq - self.ren_y_sq - 0.4 + mon.off_y) * self.square_size))

                if self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(self.pc.y_sq) == ren_pos_y:
                    self.pc_display(surface, self.ren_x_sq, self.ren_y_sq)

                for ren_z in range(1, len(decor_array)):
                    # body
                    decor = decor_array[ren_z]
                    if decor is None:
                        continue
                    surface.blit(decor,
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))

                if (ren_pos_y > 0 and self.maze.flag_array[ren_pos_y - 1][ren_pos_x].vis
                        and self.maze.array[ren_pos_y][ren_pos_x] == '+'
                        and self.maze.array[ren_pos_y - 1][ren_pos_x] == '#'):
                    surface.blit(self.maze.tile_set['doorway_ver_bar'][0],
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq - 1) * self.square_size))
                elif (ren_pos_x > 0 and self.maze.flag_array[ren_pos_y][ren_pos_x - 1].vis
                      and self.maze.array[ren_pos_y][ren_pos_x] == '+'
                      and self.maze.array[ren_pos_y][ren_pos_x - 1] == '#'):
                    surface.blit(self.maze.tile_set['doorway_hor_bar'][0],
                                 ((ren_pos_x - self.ren_x_sq - 1) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))

                if flags.obj is not None and flags.obj.render_later:
                    obj_image = flags.obj.image[self.maze.anim_frame % len(flags.obj.image)]
                    self.render_by_square(surface, ren_pos_x, ren_pos_y, flags.obj, obj_image, self.maze.flag_array)

        for ren_pos_y in range(top_sq, bottom_sq):
            for ren_pos_x in range(left_sq, right_sq):
                if not ((0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width)):
                    continue
                flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                decor_array = self.maze.decor_array[ren_pos_y][ren_pos_x]
                if decor_array == ' ' or not flags.vis:
                    continue
                shade_rate = max(0, 9 - self.vision_dist + flags.map)
                if shade_rate > 0:
                    self.shade_square.set_alpha(25 * shade_rate)
                    surface.blit(self.shade_square,
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))
                if ren_pos_x + 1 < self.maze.width and not self.maze.flag_array[ren_pos_y][ren_pos_x + 1].vis:
                    surface.blit(self.dark_edges[0],
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))
                if ren_pos_y + 1 < self.maze.height and not self.maze.flag_array[ren_pos_y + 1][ren_pos_x].vis:
                    surface.blit(self.dark_edges[1],
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))
                if ren_pos_x - 1 > -1 and not self.maze.flag_array[ren_pos_y][ren_pos_x - 1].vis:
                    surface.blit(self.dark_edges[2],
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))
                if ren_pos_y - 1 > -1 and not self.maze.flag_array[ren_pos_y - 1][ren_pos_x].vis:
                    surface.blit(self.dark_edges[3],
                                 ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (ren_pos_y - self.ren_y_sq) * self.square_size))

    def render_by_square(self, surface, ren_pos_x, ren_pos_y, obj, image, flag_array):
        img_width = image.get_width()
        img_height = image.get_height()
        for i in range(0, img_width // self.square_size):
            for j in range(0, img_height // self.square_size):
                act_ren_pos_x = ren_pos_x + obj.off_x_sq + i
                act_ren_pos_y = ren_pos_y + obj.off_y_sq + j
                flags = flag_array[round(act_ren_pos_y)][round(act_ren_pos_x)]
                if flags.vis:
                    surface.blit(image.subsurface((i * self.square_size, j * self.square_size,
                                                   self.square_size, self.square_size)),
                                 ((act_ren_pos_x - self.ren_x_sq) * self.square_size,
                                  (act_ren_pos_y - self.ren_y_sq) * self.square_size))

    def pc_display(self, surface, x_sq, y_sq):
        surface.blit(self.pc.image[self.pc.anim_frame],
                     ((self.pc.x_sq - x_sq) * self.square_size + self.pc.off_x,
                      (self.pc.y_sq - y_sq) * self.square_size + self.pc.off_y))

    def end(self):
        # prepare game pack for return to BigLoop
        pass

    def calc_vision(self, flag_array=None, orig_xy=None, max_spaces=300, max_dist=10, r_max=20):
        flag_array = flag_array or self.maze.flag_array
        orig_xy = orig_xy or (round(self.pc.x_sq), round(self.pc.y_sq))

        sq_list = calc2darray.fill2d(flag_array, ('light',), orig_xy, orig_xy, max_spaces, max_dist,
                                     r_max=r_max)
        for sq_x, sq_y in sq_list:
            flag_array[sq_y][sq_x].vis = True

        darkening_list = [d_sq for d_sq in self.vision_sq_prev if d_sq not in sq_list]
        for d_sq_x, d_sq_y in darkening_list:
            try:
                flag_array[d_sq_y][d_sq_x].vis = False
            except IndexError:
                pass
        self.vision_sq_prev = sq_list

    def calc_vision_alt(self, xy_sq=None):
        if xy_sq is None:
            orig_xy = round(self.pc.x_sq), round(self.pc.y_sq)
        else:
            orig_xy = xy_sq
        self.vision_dist = max(self.maze.stage_dict['base_light'], round(
                self.pc.char_sheet.base_light + self.pc.char_sheet.base_light * self.pc.char_sheet.profs[
                    'prof_light'] // 1000))
        self.vision_sq_prev = calc2darray.calc_vision_rays(
            self.maze.flag_array, orig_xy[0], orig_xy[1], self.vision_dist, self.vision_sq_prev
        )
        if self.wins_dict['map'] in self.active_wins:
            self.wins_dict['map'].map_update_bulk(self.vision_sq_prev)
        self.traps_search(self.vision_sq_prev)

    def mouse_move(self, mouse_xy):
        rads = maths.xy_dist_to_rads((self.pc.x_sq - self.view_maze_x_sq - 0.8) * self.square_size * self.square_scale,
                                     (self.pc.y_sq - self.view_maze_y_sq - 0.8) * self.square_size * self.square_scale,
                                     mouse_xy[0], mouse_xy[1])

        if -1.95 < rads <= -1.17:
            move_instr_x = 0
            move_instr_y = -1
        elif 1.95 > rads > 1.17:
            move_instr_x = 0
            move_instr_y = 1
        elif rads < -2.73 or rads > 2.73:
            move_instr_x = -1
            move_instr_y = 0
        elif -0.39 < rads <= 0.39:
            move_instr_x = 1
            move_instr_y = 0
        elif 0.39 < rads <= 1.17:
            move_instr_x = 1
            move_instr_y = 1
        elif 1.95 < rads <= 2.73:
            move_instr_x = -1
            move_instr_y = 1
        elif -1.95 > rads >= -2.73:
            move_instr_x = -1
            move_instr_y = -1
        else:  # -0.3 > rads >= -1.1
            move_instr_x = 1
            move_instr_y = -1
        return move_instr_x, move_instr_y

    def pc_loot_drop(self, mouse_xy, log=False):
        m_x_sq, m_y_sq = self.xy_pixels_to_squares(mouse_xy)
        if m_x_sq < 0 or m_x_sq > self.maze.width - 1 or m_y_sq < 0 or m_y_sq > self.maze.height - 1:
            return
        if not calc2darray.cast_ray(self.maze.flag_array, self.pc.x_sq, self.pc.y_sq, m_x_sq, m_y_sq, sightonly=True):
            logfun.put('I can not see that area.', log)
            return
        if not self.maze.flag_array[m_y_sq][m_x_sq].floor:
            logfun.put('I must choose floor area to drop an item.', log)
            return
        item_dragging = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
        if 'skill_id' in item_dragging.props:
            self.schedule_man.task_add('realm_tasks', 1, self, 'spawn_realmtext',
                                       ('new_txt', "Don't bury talents in the ground!",
                                        (0, 0), (0, -24), None, self.pc))
            self.schedule_man.task_add('realm_tasks', 8, self, 'remove_realmtext', ('new_txt',))
            self.mouse_pointer.drag_item = None
            self.mouse_pointer.image = None
            return
        self.loot_spawn_add(item_dragging, m_x_sq, m_y_sq)
        if not self.mouse_pointer.drag_item[0] == self.mouse_pointer.catcher:
            self.wins_dict['inventory'].updated = True
            self.wins_dict['hotbar'].updated = True
            self.wins_dict['skillbook'].updated = True

        self.pc.moved_item_cooldown_check(self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], None)

        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = None
        self.mouse_pointer.drag_item = None
        self.mouse_pointer.image = None
        # self.shortlists_update(loot=True)
        # self.render_update()

    def traps_search(self, vision_list):
        skill_value = self.pc.char_sheet.profs['prof_detect']
        traps_detected = 0
        for x_sq, y_sq in vision_list:
            trap = self.maze.flag_array[y_sq][x_sq].trap
            if trap is None or trap.visible != 0:
                continue
            lvl_dif = min(1, self.pc.char_sheet.level - trap.lvl)
            rnd_roll = random.randrange(1, 1001)
            if skill_value + lvl_dif * 250 >= rnd_roll:
                trap.visible = 1
                traps_detected = True
            else:
                trap.visible = -1
        if traps_detected:
            """self.spawn_realmtext('new_txt', "Watch out for the traps!", (0, 0), (0, 24), 'fnt_attent',
                                 self.pc, None, 180, 'def_bold', 24)"""
            self.sound_inrealm('realmtext_noise', self.pc.x_sq, self.pc.y_sq)

    def xy_pixels_to_squares(self, xy, do_round=True):
        x_sq = self.view_bleed_sq + self.view_maze_x_sq - 0.3 + xy[0] / self.square_size / self.square_scale
        y_sq = self.view_bleed_sq + self.view_maze_y_sq - 0.3 + xy[1] / self.square_size / self.square_scale
        if do_round:
            return round(x_sq), round(y_sq)
        else:
            return x_sq, y_sq

    def square_check(self, xy):
        max_range = 3
        x_sq, y_sq = self.xy_pixels_to_squares(xy)
        try:
            flags = self.maze.flag_array[y_sq][x_sq]
        except IndexError:
            return True
        if not flags.vis:
            return True
        pc_dist = maths.get_distance(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        if pc_dist > max_range or not calc2darray.path2d(self.maze.flag_array, {'mov': False}, (x_sq, y_sq),
                                                         (round(self.pc.x_sq), round(self.pc.y_sq)), 100, 10, r_max=10)[
            0]:
            return True

        if len(flags.item) > 0:
            # picking up items
            self.coins_collect(self.pc.x_sq, self.pc.y_sq, radius=max_range)
            for lt in flags.item[::-1]:
                self.maze.flag_array[y_sq][x_sq].item.remove(lt)
                self.mouse_pointer.catcher[0] = lt
                self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                self.mouse_pointer.image = lt.props['image_floor'][0]
                self.maze.loot.remove(lt)
                self.sound_inrealm('item_move', x_sq, y_sq)
                # self.loot_short.remove(lt)
                # self.render_update()
                self.buttons_pressed.discard(11)
                return False
        if flags.obj is not None:
            # objects
            self.buttons_pressed.discard(11)
            flags.obj.use(self.wins_dict, self.active_wins, self.pc, maze)

            return False
        if flags.door is not None:
            # doors
            if flags.door.use(self.wins_dict, self.active_wins, self.pc):
                self.maze.flag_array[y_sq][x_sq].mov = not flags.door.shut
                self.maze.flag_array[y_sq][x_sq].light = (not flags.door.shut) or (flags.door.grate)
                self.calc_vision_alt()
                self.shortlists_update(mobs=True)
                # self.render_update()
            self.buttons_pressed.discard(11)
            return False
        return True

    def mob_check(self, xy, m_bttn):
        x_sq, y_sq = self.xy_pixels_to_squares(xy, do_round=False)
        for mon in self.mobs_short:
            if not mon.alive:
                continue
            if not self.maze.flag_array[round(mon.y_sq)][round(mon.x_sq)].vis:
                continue
            if mon.x_sq <= (x_sq + 0.5) < (mon.x_sq + 1) and mon.y_sq <= (y_sq + 0.5) < (mon.y_sq + 1):
                self.wins_dict['target'].aim(mon, self)
                return True
        try:
            self.active_wins.remove(self.wins_dict['target'])
            self.wins_dict['target'].drop_aim()
        except ValueError:
            pass
        return False

    def shortlists_update(self, everything=False, doors=False, loot=False, traps=False, mobs=False, texts=False):
        left_sq = round(self.view_maze_x_sq - self.view_bleed_sq)
        top_sq = round(self.view_maze_y_sq - self.view_bleed_sq)
        bottom_sq = top_sq + self.view_maze_height_sq + self.view_bleed_sq * 3
        right_sq = left_sq + self.view_maze_width_sq + self.view_bleed_sq * 3

        # doors
        """if doors or everything:
            for dr in self.maze.doors:
                if self.maze.flag_array[dr.y_sq][dr.x_sq].vis:
                    self.doors_short.add(dr)
                elif dr in self.doors_short:
                    self.doors_short.remove(dr)"""

        # loot
        """if loot or everything:
            for lt in self.maze.loot:
                if self.maze.flag_array[lt.y_sq][lt.x_sq].vis:
                    if (self.mouse_pointer.drag_item is None
                            or lt != self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]):
                        self.loot_short.add(lt)

                elif lt in self.loot_short:
                    self.loot_short.remove(lt)"""

        # traps
        """if traps or everything:
            for tr in self.maze.traps:
                # Traps that are on doors and chests have None coordinates.
                if tr.x_sq is None or tr.y_sq is None:
                    continue
                if left_sq <= tr.x_sq <= right_sq and top_sq <= tr.y_sq <= bottom_sq:
                    self.traps_short.add(tr)
                elif tr in self.traps_short:
                    self.traps_short.remove(tr)"""

        # mobs
        if mobs or everything:
            for mob in self.maze.mobs:
                if left_sq <= mob.x_sq <= right_sq and top_sq <= mob.y_sq <= bottom_sq:
                    if mob not in self.mobs_short:
                        self.mobs_short.append(mob)
                elif mob in self.mobs_short:
                    self.mobs_short.remove(mob)

        # texts
        if texts or everything:
            for txt in self.maze.text:
                if left_sq <= txt.x_sq <= right_sq and top_sq <= txt.y_sq <= bottom_sq:
                    self.text_short.append(txt)
                elif txt in self.text_short:
                    self.text_short.remove(txt)

    def spawn_realmtext(self, rt_id, caption, xy_sq, offset_xy, color=None, stick_obj=None, speed_xy=None,
                        kill_timer=None, font='def_bold', size=24, frict_x=0, frict_y=0, width=None):
        if speed_xy is None:
            speed_xy = (0, 0)
        if color is None:
            color = self.resources.colors['fnt_celeb']
        else:
            color = self.resources.colors[color]
        new_tpg = typography.Typography(self.pygame_settings,
                                        caption,
                                        (0, 0), font, size, color,
                                        self.resources.colors['bg'], 'center', 'bottom', width or 160, 1, shadow=True)
        new_rt = realmtext.RealmText(self, rt_id, xy_sq, text_obj=new_tpg, stick_obj=stick_obj, offset_xy=offset_xy,
                                     speed_xy=speed_xy, kill_timer=kill_timer, frict_x=frict_x, frict_y=frict_y)
        # Move text if there is another one in place.
        self.spread_realm_text(new_rt)

        self.maze.text.append(new_rt)
        self.text_short.append(new_rt)

    def spread_realm_text(self, txt):
        for txt2 in self.maze.text:
            if txt == txt2:
                continue
            if (
                    txt.stick_obj is not None and txt.stick_obj == txt2.stick_obj
                    and txt.off_y + txt.text_obj.rendered_rect.height > txt2.off_y
                    and txt.off_y < txt2.off_y + txt2.text_obj.rendered_rect.height
            ):
                txt2.off_y = txt.off_y - txt2.text_obj.rendered_rect.height
                self.spread_realm_text(txt2)

    def remove_realmtext(self, text_id=None):
        if text_id is None:
            self.maze.text.clear()
            self.text_short.clear()
            return
        for i in range(len(self.maze.text) - 1, -1, -1):
            if self.maze.text[i].id == text_id:
                del self.maze.text[i]
        for txt in self.text_short:
            if txt.id == text_id:
                self.text_short.remove(txt)
                return

    def spawn_projectile(self, origin_xy, dest_xy, attack, speed, image_pack, off_xy=None, duration=None,
                         destroy_on_limit=True, collision_limit=1, blast_radius=0, blast_sound=None, hit_freq=20):
        if off_xy is None:
            off_xy = (0, 0)
        distance = maths.get_distance(origin_xy[0], origin_xy[1], dest_xy[0], dest_xy[1])
        direction = maths.xy_dist_to_rads(origin_xy[0], origin_xy[1], dest_xy[0], dest_xy[1])
        speed_step_x_sq, speed_step_y_sq = maths.rads_dist_to_xy(origin_xy[0], origin_xy[1], direction, speed)
        speed_xy = speed_step_x_sq - origin_xy[0], speed_step_y_sq - origin_xy[1]
        if duration is None:
            duration = math.ceil(distance / speed)

        images = self.tilesets.anim_rotate_to_dir(image_pack, direction)

        new_missile = projectile.Projectile(origin_xy, off_xy, duration, speed_xy, images, attack,
                                            destroy_on_limit=destroy_on_limit, collision_limit=collision_limit,
                                            blast_radius=blast_radius, blast_sound=blast_sound, hit_freq=hit_freq)
        self.missiles_list.append(new_missile)

    def location_label_update(self):
        if self.pc.stage_entry == 'up':
            venture_direction = 'DESC'
        else:
            venture_direction = 'ASC'
        self.location_label.caption = '%s (%s, stage %s, lv.%s), %s.' % (
        self.maze.stage_dict['label'], self.maze.chapter['label'],
        self.pc.location[1] + 1, self.maze.lvl, venture_direction)
        self.location_label.render()

    def obj_jump(self, obj_list):
        for i in range(len(obj_list) - 1, -1, -1):
            if obj_list[i][1] > 0:
                obj_list[i][1] -= 1
            else:
                self.particle_list.append(particle.Particle((obj_list[i][0].x_sq, obj_list[i][0].y_sq),
                                                            (obj_list[i][0].off_x_sq, obj_list[i][0].off_y_sq),
                                                            self.animations.get_animation('effect_dust_cloud')[
                                                                'default'], 16, speed_xy=(-0.25, -0.25)))
                try:
                    sound = obj_list[i][0].props['sound_drop']
                except AttributeError:
                    sound = 'bag_drop'
                self.sound_inrealm(sound, obj_list[i][0].x_sq, obj_list[i][0].y_sq)
                del obj_list[i]
                continue
            obj_list[i][0].off_x_sq = math.sin(obj_list[i][1] / obj_list[i][2] * 3.14) * 2 * -1
            obj_list[i][0].off_y_sq = math.sin(obj_list[i][1] / obj_list[i][2] * 3.14) * 2 * -1

    def obj_jump_add(self, object):
        self.jumping_objects.append([object, 20, 20])

    def coins_collect(self, x_sq, y_sq, radius=2):
        collected = False
        for i in range(radius * -1, radius + 1):
            for j in range(radius * -1, radius + 1):
                try:
                    flags = self.maze.flag_array[round(y_sq) + j][round(x_sq) + i]
                except IndexError:
                    continue
                if not flags.item:
                    continue
                for itm in flags.item[::-1]:
                    if itm.props['treasure_id'] != 6:
                        continue
                    collected = True
                    self.spawn_realmtext('new_txt', "%s gold" % itm.props['amount'], (0, 0), (0, 0),
                                         'bright_gold', itm, (0, -0.1), 45, 'large', 16, 0, 0)
                    self.pc.char_sheet.gold_coins += itm.props['amount']
                    self.maze.loot.remove(itm)
                    # realm.loot_short.remove(itm)
                    flags.item.remove(itm)
        if collected:
            self.sound_inrealm('coins_pickup', self.pc.x_sq, self.pc.y_sq)
            self.wins_dict['inventory'].updated = True
            self.wins_dict['trade'].updated = True

    def loot_spawn_add(self, item, x_sq, y_sq):
        self.obj_jump_add(item)
        self.maze.spawn_loot(x_sq, y_sq, (item,))
        self.sound_inrealm('item_throw', x_sq, y_sq)

    def sound_inrealm(self, sound_name, x_sq, y_sq, forced=False, volume_rate=1):
        max_distance = 24
        distance = maths.get_distance(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        if distance > max_distance:
            return
        volume = max(0.001, (1 - round(distance / max_distance, 4))) * volume_rate
        direction = maths.xy_dist_to_rads(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        self.pygame_settings.audio.sound_panned(sound_name, direction, volume, forced)

    def monster_sound_ambience(self):
        pass
        """if self.maze.anim_frame != 0 or self.maze.anim_timer != 0:
            return
        if random.randrange(0, 12) > 0:
            return
        if len(self.mobs_short) == 0:
            return
        random_monster = random.choice(self.mobs_short)
        if random_monster.aggred:
            return
        self.sound_inrealm(random_monster.stats['sound_amb'], random_monster.x_sq, random_monster.y_sq)"""

    def hit_fx(self, x_sq, y_sq, dam_type, is_crit, forced_sound=True, for_pc=False):
        if dam_type == 'att_physical':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                                            self.animations.get_animation('effect_blood_cloud')[
                                                                'default'],
                                                            16, speed_xy=(0.25, 0.25)))
        elif dam_type == 'att_arcane':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (0, 0),
                                                            self.animations.get_animation('effect_arcane_dust')[
                                                                'default'],
                                                            29, speed_xy=(-0.25, -0.25)))
        elif dam_type == 'att_fire':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                                            self.animations.get_animation('effect_fire_burst')[
                                                                'default'],
                                                            29, speed_xy=(0, 0)))
        elif dam_type == 'att_poison':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                                            self.animations.get_animation('effect_poison_bubble')[
                                                                'default'],
                                                            30, speed_xy=(0, 0)))
        elif dam_type == 'att_ice':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                                            self.animations.get_animation('effect_ice_crystal')[
                                                                'default'],
                                                            29, speed_xy=(0, 0)))
        elif dam_type == 'att_lightning':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                                            self.animations.get_animation('effect_lightning_bolt')[
                                                                'default'],
                                                            29, speed_xy=(0, 0)))

        if for_pc:
            self.sound_inrealm(self.resources.sound_presets['damage'][dam_type], x_sq, y_sq, forced=forced_sound)
            self.pygame_settings.audio.sound('pc_hit')
            if is_crit:
                self.pygame_settings.audio.sound('hit_ring')
        else:
            self.sound_inrealm(self.resources.sound_presets['damage'][dam_type], x_sq, y_sq, forced=forced_sound)
            if is_crit:
                self.pygame_settings.audio.sound('hit_blast')
