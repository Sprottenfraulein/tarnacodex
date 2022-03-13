import pygame
import random
from library import calc2darray, maths, logfun, typography, particle
from components import realmtext, skillfuncs, projectile
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

        self.dark_edges = self.tilesets.get_image('dark_edges', (24, 24), (0, 1, 2, 3))
        self.target_mark = self.tilesets.get_image('interface', (24, 24), (10, 11, 12, 13))

        self.pause = False
        self.controls_enabled = True

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
        self.view_size_scaled = (w,h)
        framed_wins = (self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'], self.wins_dict['inventory'], self.wins_dict['skillbook'])
        for win in framed_wins:
            win.offset_x, win.offset_y = maths.rect_sticky_edges((win.offset_x, win.offset_y, win.win_w, win.win_h),
                                                                 [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
            win.offset_x, win.offset_y = maths.rect_in_bounds(win.offset_x, win.offset_y, win.win_w, win.win_h, 0,
                                                              0, w, h)
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)

    def launch(self):
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

        if self.wins_dict['pools'] not in self.active_wins:
            self.active_wins.insert(0, self.wins_dict['pools'])
        if self.wins_dict['hotbar'] not in self.active_wins:
            self.active_wins.insert(0, self.wins_dict['hotbar'])

        self.wins_dict['target'].drop_aim()

        self.pc.ready()
        self.pause = False
        self.controls_enabled = True

    def event_check(self, event, log=True):
        if not self.pc.alive or not self.controls_enabled:
            return
        # character and gui controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # self.view_maze_x_sq -= 1
                self.pc.move_instr_x = -1
            if event.key == pygame.K_RIGHT:
                # self.view_maze_x_sq += 1
                self.pc.move_instr_x = 1
            if event.key == pygame.K_UP:
                # self.view_maze_y_sq -= 1
                self.pc.move_instr_y = -1
            if event.key == pygame.K_DOWN:
                # self.view_maze_y_sq += 1
                self.pc.move_instr_y = 1


            if event.key == pygame.K_v:
                self.view_offset_x_sq = round(self.mouse_pointer.xy[0] / self.square_size / self.square_scale) * -1
                self.view_offset_y_sq = round(self.mouse_pointer.xy[1] / self.square_size / self.square_scale) * -1
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
            if event.key == pygame.K_i:
                pass
            if event.key == pygame.K_s:
                self.wins_dict['app_title'].chapter_end(self.pc, self.maze.chapter)
            if event.key == pygame.K_l:
                pass
            if event.key == pygame.K_h:
                pass
            if event.key == pygame.K_p:
                pass
            if event.key == pygame.K_m:
                self.schedule_man.task_add('realm_tasks', 6, self, 'spawn_realmtext',
                                           ('new_txt', "I'd better have a black muffin.",
                                            (0, 0), (0, -24), None, self.pc, None, 120, 'def_bold', 24))

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # self.view_maze_x_sq -= 1
                self.pc.move_instr_x = 0
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                # self.view_maze_y_sq -= 1
                self.pc.move_instr_y = 0

            elif event.key == pygame.K_1 and self.pc.char_sheet.hotbar[0] is not None:
                self.hot_activate(0, True)
            elif event.key == pygame.K_2 and self.pc.char_sheet.hotbar[1] is not None:
                self.hot_activate(1, True)
            elif event.key == pygame.K_3 and self.pc.char_sheet.hotbar[2] is not None:
                self.hot_activate(2, True)
            elif event.key == pygame.K_4 and self.pc.char_sheet.hotbar[3] is not None:
                self.hot_activate(3, True)
            elif event.key == pygame.K_5 and self.pc.char_sheet.hotbar[4] is not None:
                self.hot_activate(4, True)
            elif event.key == pygame.K_6 and self.pc.char_sheet.hotbar[5] is not None:
                self.hot_activate(5, True)
            elif event.key == pygame.K_7 and self.pc.char_sheet.hotbar[6] is not None:
                self.hot_activate(6, True)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # removing popup if active
            if self.wins_dict['context'] in self.active_wins:
                self.active_wins.remove(self.wins_dict['context'])
            if self.mouse_pointer.drag_item is not None:
                return

            can_move = True
            if event.button == 1 and self.pc.char_sheet.hotbar[-2] is not None:
                can_move = self.hot_activate(-2, False)
            elif event.button == 3 and self.pc.char_sheet.hotbar[-1] is not None:
                can_move = self.hot_activate(-1, False)
            if can_move and event.button == 1:
                can_move = self.square_check(self.mouse_pointer.xy)
            if can_move and event.button == 1:
                self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(self.mouse_pointer.xy)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button != 1:
                return
            self.pc.move_instr_x = self.pc.move_instr_y = 0

            if self.mouse_pointer.drag_item is None:
                return
            self.pc_loot_drop(self.mouse_pointer.xy, log)

        elif event.type == pygame.MOUSEMOTION:
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

        self.maze.tick()
        self.pc.tick(self, self.resources.fate_rnd, self.wins_dict, self.active_wins)
        for mob in self.mobs_short:
            mob.tick(self.wins_dict, self.resources.fate_rnd, self)

        for i in range(len(self.text_short) -1, -1, -1):
            self.text_short[i].tick()

        for i in range(len(self.missiles_list) -1, -1, -1):
            if not self.missiles_list[i].tick(self.wins_dict, self.resources.fate_rnd):
                del self.missiles_list[i]

        for i in range(len(self.particle_list) -1, -1, -1):
            if not self.particle_list[i].tick():
                del self.particle_list[i]

        if len(self.loot_spawn_list) > 0 and self.schedule_man.frame == 0:
            self.loot_spawn_add(*self.loot_spawn_list.pop())

        self.obj_jump(self.jumping_objects)

        self.monster_sound_ambience()

        self.render_update()

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
                 (txt.x_sq - self.view_maze_x_sq - self.view_bleed_sq) * self.square_size * self.square_scale + txt.off_x,
                 (txt.y_sq - self.view_maze_y_sq - self.view_bleed_sq) * self.square_size * self.square_scale + txt.off_y)

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
                try:
                    self.view_maze_surface.blit(missile.images[self.maze.anim_frame],
                                 ((missile.x_sq - self.ren_x_sq) * self.square_size + missile.off_x,
                                  (missile.y_sq - self.ren_y_sq) * self.square_size + missile.off_y))
                except IndexError:
                    self.view_maze_surface.blit(missile.images[(self.maze.anim_frame + 1) % (len(missile.images))],
                                                ((missile.x_sq - self.ren_x_sq) * self.square_size + missile.off_x,
                                                 (missile.y_sq - self.ren_y_sq) * self.square_size + missile.off_y))

        if self.redraw_particles:
            for part in self.particle_list:
                self.view_maze_surface.blit(part.image_strip[part.frame_index],
                                            (round((part.x - self.ren_x_sq) * self.square_size + part.off_x),
                                             round((part.y - self.ren_y_sq) * self.square_size + part.off_y)))

        self.draw_view_maze = True

    def stage_render(self, surface, top_sq, left_sq, bottom_sq, right_sq, clear=True):
        if clear:
            surface.fill((1, 1, 1))

        for ren_pos_y in range(top_sq, bottom_sq):
            for ren_pos_x in range(left_sq, right_sq):
                if (0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width):
                    flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                    if flags.vis:
                        decors = self.maze.decor_array[ren_pos_y][ren_pos_x]
                        surface.blit(decors[0],
                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                              (ren_pos_y - self.ren_y_sq) * self.square_size))

        for ren_pos_y in range(top_sq, bottom_sq):
            for ren_pos_x in range(left_sq, right_sq):
                # body
                if (0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width):

                    flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                    if flags.vis:
                        decors = self.maze.decor_array[ren_pos_y][ren_pos_x]

                        if flags.trap is not None and flags.trap.visible == 1:
                            try:
                                surface.blit(flags.trap.images[self.maze.anim_frame],
                                             ((flags.trap.x_sq - self.ren_x_sq) * self.square_size + flags.trap.off_x,
                                              (flags.trap.y_sq - self.ren_y_sq) * self.square_size + flags.trap.off_y))
                            except IndexError:
                                surface.blit(flags.trap.images[(self.maze.anim_frame + 1) % (len(flags.trap.images))],
                                             ((flags.trap.x_sq - self.ren_x_sq) * self.square_size + flags.trap.off_x,
                                              (flags.trap.y_sq - self.ren_y_sq) * self.square_size + flags.trap.off_y))

                        # drawing doors
                        if flags.door is not None:
                            try:
                                surface.blit(flags.door.image[self.maze.anim_frame],
                                             ((flags.door.x_sq - self.ren_x_sq) * self.square_size + flags.door.off_x,
                                              (flags.door.y_sq - self.ren_y_sq) * self.square_size + flags.door.off_y))
                            except IndexError:
                                surface.blit(flags.door.image[(self.maze.anim_frame + 1) % (len(flags.door.image))],
                                             ((flags.door.x_sq - self.ren_x_sq) * self.square_size + flags.door.off_x,
                                              (flags.door.y_sq - self.ren_y_sq) * self.square_size + flags.door.off_y))
                            if flags.door.alignment:
                                if not self.maze.flag_array[flags.door.y_sq - 1][flags.door.x_sq].vis:
                                    surface.fill((1, 1, 1), ((flags.door.x_sq - self.ren_x_sq) * self.square_size,
                                                             (flags.door.y_sq - self.ren_y_sq - 1) * self.square_size,
                                                             self.square_size, self.square_size))
                            else:
                                if not self.maze.flag_array[flags.door.y_sq][flags.door.x_sq - 1].vis:
                                    surface.fill((1, 1, 1), ((flags.door.x_sq - self.ren_x_sq - 1) * self.square_size,
                                                             (flags.door.y_sq - self.ren_y_sq) * self.square_size,
                                                             self.square_size, self.square_size))

                        if flags.obj is not None:
                            try:
                                surface.blit(flags.obj.image[self.maze.anim_frame],
                                             ((flags.obj.x_sq - self.ren_x_sq) * self.square_size + flags.obj.off_x,
                                              (flags.obj.y_sq - self.ren_y_sq) * self.square_size + flags.obj.off_y))
                            except IndexError:
                                surface.blit(flags.obj.image[(self.maze.anim_frame + 1) % (len(flags.obj.image))],
                                             ((flags.obj.x_sq - self.ren_x_sq) * self.square_size + flags.obj.off_x,
                                              (flags.obj.y_sq - self.ren_y_sq) * self.square_size + flags.obj.off_y))

                        # drawing loot
                        if flags.item is not None:
                            for loot in flags.item:
                                try:
                                    surface.blit(loot.props['image_floor'][self.maze.anim_frame],
                                                 ((loot.x_sq - self.ren_x_sq) * self.square_size + loot.off_x,
                                                  (loot.y_sq - self.ren_y_sq) * self.square_size + loot.off_y))
                                except IndexError:
                                    surface.blit(
                                        loot.props['image_floor'][
                                            (self.maze.anim_frame + 1) % (len(loot.props['image_floor']))],
                                        ((loot.x_sq - self.ren_x_sq) * self.square_size + loot.off_x,
                                         (loot.y_sq - self.ren_y_sq) * self.square_size + loot.off_y))

                        if len(decors) > 1:
                            for k in range(1, len(decors)):
                                if self.redraw_maze_decor:
                                    try:
                                        surface.blit(decors[k],
                                                     ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                                      (ren_pos_y - self.ren_y_sq) * self.square_size))
                                    except TypeError:
                                        # print('Realm.Stage_display: Wrong tile.')
                                        pass
                        else:
                            if self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(self.pc.y_sq) == ren_pos_y:
                                self.pc_display(surface, self.ren_x_sq, self.ren_y_sq)

                        try:
                            if not self.maze.flag_array[ren_pos_y][ren_pos_x + 1].vis:
                                surface.blit(self.dark_edges[0],
                                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                              (ren_pos_y - self.ren_y_sq) * self.square_size))
                            if not self.maze.flag_array[ren_pos_y + 1][ren_pos_x].vis:
                                surface.blit(self.dark_edges[1],
                                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                              (ren_pos_y - self.ren_y_sq) * self.square_size))
                            if not self.maze.flag_array[ren_pos_y][ren_pos_x - 1].vis:
                                surface.blit(self.dark_edges[2],
                                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                              (ren_pos_y - self.ren_y_sq) * self.square_size))
                            if not self.maze.flag_array[ren_pos_y - 1][ren_pos_x].vis:
                                surface.blit(self.dark_edges[3],
                                             ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                              (ren_pos_y - self.ren_y_sq) * self.square_size))

                        except IndexError:
                            # print('Realm.Stage_display: Wrong tile.')
                            pass

                        # mobs rendering
                        if flags.mon is not None:
                            mon = flags.mon
                            if mon.aimed:
                                surface.blit(self.target_mark[self.maze.anim_frame],
                                             ((mon.x_sq - self.ren_x_sq + 0.15) * self.square_size + mon.off_x,
                                              (mon.y_sq - self.ren_y_sq + 0.2) * self.square_size + mon.off_y))
                            """if mon.waypoints is not None:
                                for wp in mon.waypoints:
                                    surface.blit(self.target_mark[0],
                                                 ((wp[0] - self.ren_x_sq + 0.15) * self.square_size,
                                                  (wp[1] - self.ren_y_sq + 0.2) * self.square_size))"""
                            surface.blit(mon.image[mon.anim_frame],
                                         ((mon.x_sq - self.ren_x_sq - 0.1) * self.square_size + mon.off_x,
                                          (mon.y_sq - self.ren_y_sq - 0.1) * self.square_size + mon.off_y))

                        if self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(self.pc.y_sq) == ren_pos_y:
                            self.pc_display(surface, self.ren_x_sq, self.ren_y_sq)

    def pc_display(self, surface, x_sq, y_sq):
        try:
            surface.blit(self.pc.image[self.pc.anim_frame],
                         ((self.pc.x_sq - x_sq - 0.1) * self.square_size + self.pc.off_x,
                          (self.pc.y_sq - y_sq - 0.1) * self.square_size + self.pc.off_y))
        except IndexError:
            surface.blit(self.pc.image[self.pc.anim_frame % len(self.pc.image)],
                         ((self.pc.x_sq - x_sq - 0.1) * self.square_size + self.pc.off_x,
                          (self.pc.y_sq - y_sq - 0.1) * self.square_size + self.pc.off_y))

    def end(self):
        # prepare game pack for return to BigLoop
        pass

    def calc_vision(self, flag_array=None, orig_xy=None, max_spaces=300, max_dist=10, r_max=20):
        flag_array = flag_array or self.maze.flag_array
        orig_xy = orig_xy or (round(self.pc.x_sq), round(self.pc.y_sq))

        sq_list = calc2darray.fill2d(flag_array, {'light': False}, orig_xy, orig_xy, max_spaces, max_dist,
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

        self.vision_sq_prev = calc2darray.calc_vision_rays(
            self.maze.flag_array, orig_xy[0], orig_xy[1],
            max(self.maze.stage_dict['base_light'], round(self.pc.char_sheet.base_light + self.pc.char_sheet.base_light * self.pc.char_sheet.profs['prof_light'] // 1000)),
            self.vision_sq_prev
        )
        self.traps_search(self.vision_sq_prev)

    def mouse_move(self, mouse_xy):
        rads = maths.xy_dist_to_rads((self.pc.x_sq - self.view_maze_x_sq - 0.4) * self.square_size * self.square_scale,
                                     (self.pc.y_sq - self.view_maze_y_sq - 0.4) * self.square_size * self.square_scale,
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
            self.spawn_realmtext('new_txt', "Watch out for the traps!", (0, 0), (0, 24), 'fnt_attent',
                                 self.pc, None, 180, 'def_bold', 24)
            self.sound_inrealm('realmtext_noise', self.pc.x_sq, self.pc.y_sq)

    def xy_pixels_to_squares(self, xy, do_round=True):
        x_sq = self.view_bleed_sq + self.view_maze_x_sq - 0.3 + xy[0] / self.square_size / self.square_scale
        y_sq = self.view_bleed_sq + self.view_maze_y_sq - 0.3 + xy[1] / self.square_size / self.square_scale
        if do_round:
            return round(x_sq), round(y_sq)
        else:
            return x_sq, y_sq

    def square_check(self, xy):
        x_sq, y_sq = self.xy_pixels_to_squares(xy)
        try:
            flags = self.maze.flag_array[y_sq][x_sq]
        except IndexError:
            return True
        if not flags.vis:
            return True
        pc_dist = maths.get_distance(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        if pc_dist > 3:
            return True

        if len(flags.item) > 0:
            # picking up items
            for lt in flags.item:
                if lt.props['treasure_id'] == 6:
                    self.coins_collect(lt, flags.item, self.pc)
                    return False
                else:
                    self.maze.flag_array[y_sq][x_sq].item.remove(lt)
                    self.mouse_pointer.catcher[0] = lt
                    self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                    self.mouse_pointer.image = lt.props['image_floor'][0]
                    self.maze.loot.remove(lt)
                    self.sound_inrealm('item_move', x_sq, y_sq)
                    # self.loot_short.remove(lt)
                    # self.render_update()
                    return False
        if flags.door is not None:
            # doors
            if flags.door.use(self.wins_dict, self.active_wins, self.pc):
                self.maze.flag_array[y_sq][x_sq].mov = not flags.door.shut
                self.maze.flag_array[y_sq][x_sq].light = (not flags.door.shut) or (flags.door.grate)
                self.calc_vision_alt()
                self.shortlists_update(mobs=True)
                # self.render_update()
            return False
        if flags.obj is not None:
            # objects
            flags.obj.use(self.wins_dict, self.active_wins, self.pc)
            return False
        return True

    def mob_check(self, xy, m_bttn):
        x_sq, y_sq = self.xy_pixels_to_squares(xy, do_round=False)
        for mon in self.mobs_short:
            if not mon.alive:
                continue
            if not self.maze.flag_array[round(mon.y_sq)][round(mon.x_sq)].vis:
                continue
            if mon.x_sq <= x_sq + 0.5 < mon.x_sq + 1 and mon.y_sq <= y_sq + 0.5 < mon.y_sq + 1:
                self.wins_dict['target'].aim(mon, self)
                self.active_wins.insert(0, self.wins_dict['target'])
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
                        kill_timer=None, font='def_bold', size=24, frict_x=0, frict_y=0):
        if speed_xy is None:
            speed_xy = (0,0)
        if color is None:
            color = self.resources.colors['fnt_celeb']
        else:
            color = self.resources.colors[color]
        new_tpg = typography.Typography(self.pygame_settings,
                                        caption,
                                        (0, 0), font, size, color,
                                        self.resources.colors['bg'], 'center', 'bottom', 160, 64, shadow=True)
        new_rt = realmtext.RealmText(self, rt_id, xy_sq, text_obj=new_tpg, stick_obj=stick_obj, offset_xy=offset_xy,
                                     speed_xy=speed_xy, kill_timer=kill_timer, frict_x=frict_x, frict_y=frict_y)
        self.maze.text.append(new_rt)
        self.text_short.append(new_rt)

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
                         destroy_on_limit=True, collision_limit=1, blast_radius=0):
        if off_xy is None:
            off_xy = (0,0)
        distance = maths.get_distance(origin_xy[0], origin_xy[1], dest_xy[0], dest_xy[1])
        direction = maths.xy_dist_to_rads(origin_xy[0], origin_xy[1], dest_xy[0], dest_xy[1])
        speed_step_x_sq, speed_step_y_sq = maths.rads_dist_to_xy(origin_xy[0], origin_xy[1], direction, speed)
        speed_xy = speed_step_x_sq - origin_xy[0], speed_step_y_sq - origin_xy[1]
        if duration is None:
            duration = math.ceil(distance / speed)

        images = self.tilesets.images_rotate_to_dir(image_pack, direction)

        new_missile = projectile.Projectile(origin_xy, off_xy, duration, speed_xy, images, attack,
                                            destroy_on_limit=destroy_on_limit,
                                            collision_limit=collision_limit, blast_radius=blast_radius)
        self.missiles_list.append(new_missile)

    def location_label_update(self):
        if self.pc.stage_entry == 'up':
            venture_direction = 'descended'
        else:
            venture_direction = 'ascended'
        self.location_label.caption = '%s (%s, stage %s, level %s), %s.' % (self.maze.stage_dict['label'], self.maze.chapter['label'],
                                                                  self.pc.location[1] + 1, self.maze.lvl, venture_direction)
        self.location_label.render()

    def obj_jump(self, obj_list):
        for i in range(len(obj_list) - 1, -1, -1):
            if obj_list[i][1] > 0:
                obj_list[i][1] -= 1
            else:
                self.particle_list.append(particle.Particle((obj_list[i][0].x_sq, obj_list[i][0].y_sq),
                                           (obj_list[i][0].off_x, obj_list[i][0].off_y),
                                           self.animations.get_animation('effect_dust_cloud')['default'], 16, speed_xy=(-0.25,-0.25)))
                try:
                    sound = obj_list[i][0].props['sound_drop']
                except AttributeError:
                    sound = 'bag_drop'
                self.sound_inrealm(sound, obj_list[i][0].x_sq, obj_list[i][0].y_sq)
                del obj_list[i]
                continue
            obj_list[i][0].off_x = math.sin(obj_list[i][1] / obj_list[i][2] * 3.14) * (self.square_size * self.square_scale) * -1
            obj_list[i][0].off_y = math.sin(obj_list[i][1] / obj_list[i][2] * 3.14) * (self.square_size * self.square_scale) * -1

    def obj_jump_add(self, object):
        self.jumping_objects.append([object, 20, 20])

    def coins_collect(self, itm, flag_items, pc):
        self.spawn_realmtext('new_txt', "%s gold" % itm.props['amount'], (0, 0), (0, 0),
                                           'bright_gold', itm, (0, 0), 45, 'large', 16, 0, 0)
        pc.char_sheet.gold_coins += itm.props['amount']
        self.sound_inrealm(itm.props['sound_pickup'], itm.x_sq, itm.y_sq)
        self.maze.loot.remove(itm)
        # realm.loot_short.remove(itm)
        self.wins_dict['inventory'].updated = True
        self.wins_dict['trade'].updated = True
        flag_items.remove(itm)

    def loot_spawn_add(self, item, x_sq, y_sq):
        self.obj_jump_add(item)
        self.maze.spawn_loot(x_sq, y_sq, (item,))
        self.sound_inrealm('item_throw', x_sq, y_sq)

    def sound_inrealm(self, sound_name, x_sq, y_sq, forced=False):
        max_distance = 17
        distance = maths.get_distance(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        if distance > max_distance:
            return
        volume = 1 - round(distance / max_distance, 2)
        direction = maths.xy_dist_to_rads(self.pc.x_sq, self.pc.y_sq, x_sq, y_sq)
        self.pygame_settings.audio.sound_panned(sound_name, direction, volume, forced)

    def monster_sound_ambience(self):
        if self.maze.anim_frame != 0 or self.maze.anim_timer != 0:
            return
        if random.randrange(0, 4) > 0:
            return
        if len(self.mobs_short) == 0:
            return
        random_monster = random.choice(self.mobs_short)
        if random_monster.aggred:
            return
        self.sound_inrealm(random_monster.stats['sound_amb'], random_monster.x_sq, random_monster.y_sq)

    def hit_fx(self, x_sq, y_sq, dam_type, is_crit, forced_sound=True, for_pc=False):
        if dam_type == 'att_physical':
            for i in range(-1, is_crit * 4):
                rnd_x_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + x_sq
                rnd_y_sq = random.randrange(-3 - is_crit, 4 + is_crit) / 10 + y_sq
                self.particle_list.append(particle.Particle((rnd_x_sq, rnd_y_sq), (-8, -8),
                                          self.animations.get_animation('effect_blood_cloud')['default'],
                                          16, speed_xy=(0.25, 0.25)))

        if for_pc:
            self.pygame_settings.audio.sound('pc_hit')
            if is_crit:
                self.pygame_settings.audio.sound('hit_blast')
        else:
            self.sound_inrealm(self.resources.sound_presets['damage'][dam_type], x_sq, y_sq, forced=forced_sound)
            if is_crit:
                self.pygame_settings.audio.sound('hit_blast')