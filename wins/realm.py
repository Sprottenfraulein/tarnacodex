import pygame
from library import calc2darray, maths, logfun, typography
from components import realmtext, skillfuncs, gamesave
import math


class Realm:
    def __init__(self, pygame_settings, resources, tile_sets, anims, db, mouse_pointer, schedule_man):
        self.pygame_settings = pygame_settings
        self.resources = resources
        self.tile_sets = tile_sets
        self.anims = anims
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man

        self.doors_short = set()
        self.traps_short = set()
        self.loot_short = set()
        self.mobs_short = set()

        self.text_short = []

        self.draw_view_maze = False

        self.redraw_maze_decor = True
        self.redraw_maze_obj = True
        self.redraw_maze_loot = True
        self.redraw_maze_mobs = True
        self.redraw_maze_text = True

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

        self.view_maze_surface = None
        self.vision_sq_prev = None

        self.dark_edges = self.tile_sets.get_image('dark_edges', (24, 24), (0, 1, 2, 3))
        self.target_mark = self.tile_sets.get_image('interface', (24, 24), (10, 11, 12, 13))

    def view_resize(self, wins_dict, w, h):
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
        framed_wins = (wins_dict['charstats'], wins_dict['pools'], wins_dict['hotbar'], wins_dict['inventory'], wins_dict['skillbook'])
        for win in framed_wins:
            win.offset_x, win.offset_y = maths.rect_sticky_edges((win.offset_x, win.offset_y, win.win_w, win.win_h),
                                                                 [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
            win.offset_x, win.offset_y = maths.rect_in_bounds(win.offset_x, win.offset_y, win.win_w, win.win_h, 0,
                                                              0, w, h)
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)

    def launch(self, wins_dict, active_wins):
        wins_dict['realm'].view_resize(wins_dict, self.pygame_settings.screen_res[0], self.pygame_settings.screen_res[1])
        # creating dedicated schedule
        self.schedule_man.new_schedule('realm_tasks')
        # game pack must include dungeon set, character
        self.view_maze_follow = self.pc
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
        # visibility update
        self.calc_vision_alt()
        # creating shortlists
        self.doors_short = set()
        self.traps_short = set()
        self.loot_short = set()
        self.mobs_short = set()

        self.text_short = []

        self.shortlists_update(everything=True)
        self.render_update()

        if wins_dict['hotbar'].pc != self.pc:
            wins_dict['hotbar'].launch(self.pc)

        if wins_dict['pools'].pc != self.pc:
            wins_dict['pools'].launch(self.pc)

        if wins_dict['pools'] not in active_wins:
            active_wins.insert(0, wins_dict['pools'])

        self.pc.ready()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        if not self.pc.alive:
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
                wins_dict['app_title'].chapter_end(wins_dict, active_wins, self.maze.chapter)
            if event.key == pygame.K_l:
                pass
            if event.key == pygame.K_h:
                pass
            if event.key == pygame.K_p:
                if wins_dict['pools'] in active_wins:
                    active_wins.remove(wins_dict['pools'])
                else:
                    wins_dict['pools'].render()
                    active_wins.insert(0, wins_dict['pools'])
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
                self.hot_activate(wins_dict, resources, 0, True)
            elif event.key == pygame.K_2 and self.pc.char_sheet.hotbar[1] is not None:
                self.hot_activate(wins_dict, resources, 1, True)
            elif event.key == pygame.K_3 and self.pc.char_sheet.hotbar[2] is not None:
                self.hot_activate(wins_dict, resources, 2, True)
            elif event.key == pygame.K_4 and self.pc.char_sheet.hotbar[3] is not None:
                self.hot_activate(wins_dict, resources, 3, True)
            elif event.key == pygame.K_5 and self.pc.char_sheet.hotbar[4] is not None:
                self.hot_activate(wins_dict, resources, 4, True)
            elif event.key == pygame.K_6 and self.pc.char_sheet.hotbar[5] is not None:
                self.hot_activate(wins_dict, resources, 5, True)
            elif event.key == pygame.K_7 and self.pc.char_sheet.hotbar[6] is not None:
                self.hot_activate(wins_dict, resources, 6, True)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # removing popup if active
            if wins_dict['context'] in active_wins:
                active_wins.remove(wins_dict['context'])
            if self.mouse_pointer.drag_item is not None:
                return

            can_move = True
            if event.button == 1 and self.pc.char_sheet.hotbar[-2] is not None:
                can_move = self.hot_activate(wins_dict, resources, -2, False)
            elif event.button == 3 and self.pc.char_sheet.hotbar[-1] is not None:
                can_move = self.hot_activate(wins_dict, resources, -1, False)
            if can_move and event.button == 1:
                can_move = self.square_check(self.mouse_pointer.xy, wins_dict, active_wins)
            if can_move and event.button == 1:
                self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(self.mouse_pointer.xy)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button != 1:
                return
            self.pc.move_instr_x = self.pc.move_instr_y = 0

            if self.mouse_pointer.drag_item is None:
                return
            self.pc_loot_drop(self.mouse_pointer.xy, wins_dict, active_wins, log)

        elif event.type == pygame.MOUSEMOTION:
            self.mob_check(self.mouse_pointer.xy, None, wins_dict, active_wins)
            if self.pc.move_instr_y != 0 or self.pc.move_instr_x != 0:
                self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(self.mouse_pointer.xy)

    def hot_activate(self, wins_dict, resources, index, no_aim):
        if 'skill_id' in self.pc.char_sheet.hotbar[index].props:
            return getattr(skillfuncs, self.pc.char_sheet.hotbar[index].props['function_name'])(
                wins_dict, resources.fate_rnd, self.pc, self.pc.char_sheet.hotbar[index],
                wins_dict['hotbar'].hot_sockets_list[index], no_aim
            )
        elif ('treasure_id' in self.pc.char_sheet.hotbar[index].props
                and self.pc.char_sheet.hotbar[index].props['use_skill'] is not None):
            return getattr(skillfuncs, self.pc.char_sheet.hotbar[index].props['use_skill'].props['function_name'])(
                wins_dict, resources.fate_rnd, self.pc, self.pc.char_sheet.hotbar[index].props['use_skill'],
                wins_dict['hotbar'].hot_sockets_list[index], no_aim
            )
        return True

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.maze.tick()
        self.pc.tick(self, self.resources.fate_rnd, wins_dict, active_wins)
        for mob in self.mobs_short:
            mob.tick(wins_dict, active_wins, self)

        for i in range(len(self.text_short) -1, -1, -1):
            self.text_short[i].tick()

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
                                if k == 1 and self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(
                                        self.pc.y_sq) == ren_pos_y:
                                    self.pc_display(surface, self.ren_x_sq, self.ren_y_sq)

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

    def calc_vision_alt(self):
        orig_xy = round(self.pc.x_sq), round(self.pc.y_sq)
        # realm.calc_vision(realm.maze.flag_array, orig_xy, 100, (12, 8), r_max=10)
        self.vision_sq_prev = calc2darray.calc_vision_rays(self.maze.flag_array, orig_xy[0], orig_xy[1], 10,
                                                           self.vision_sq_prev)

    def mouse_move(self, mouse_xy):
        rads = maths.xy_dist_to_rads(mouse_xy[0], mouse_xy[1],
                                     (self.pc.x_sq - self.view_maze_x_sq - 0.4) * self.square_size * self.square_scale,
                                     (self.pc.y_sq - self.view_maze_y_sq - 0.4) * self.square_size * self.square_scale)

        if -1.9 < rads <= -1.1:
            move_instr_x = 0
            move_instr_y = 1
        elif 1.9 > rads > 1.1:
            move_instr_x = 0
            move_instr_y = -1
        elif rads < -2.7 or rads > 2.7:
            move_instr_x = 1
            move_instr_y = 0
        elif -0.3 < rads <= 0.3:
            move_instr_x = -1
            move_instr_y = 0
        elif 0.3 < rads <= 1.1:
            move_instr_x = -1
            move_instr_y = -1
        elif 1.9 < rads <= 2.7:
            move_instr_x = 1
            move_instr_y = -1
        elif -1.9 > rads >= -2.7:
            move_instr_x = 1
            move_instr_y = 1
        else:  # -0.3 > rads >= -1.1
            move_instr_x = -1
            move_instr_y = 1
        return move_instr_x, move_instr_y

    def pc_loot_drop(self, mouse_xy, wins_dict, active_wins, log=False):
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
                                        (0, 0), (0, -24), None, True, self.pc))
            self.schedule_man.task_add('realm_tasks', 8, self, 'remove_realmtext', ('new_txt',))
            return
        self.maze.spawn_loot(m_x_sq, m_y_sq, (item_dragging,))
        if not self.mouse_pointer.drag_item[0] == self.mouse_pointer.catcher:
            wins_dict['inventory'].updated = True
            wins_dict['hotbar'].updated = True
            wins_dict['skillbook'].updated = True
        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = None
        self.mouse_pointer.drag_item = None
        self.mouse_pointer.image = None
        # self.shortlists_update(loot=True)
        # self.render_update()

    def xy_pixels_to_squares(self, xy, do_round=True):
        x_sq = self.view_bleed_sq + self.view_maze_x_sq - 0.3 + xy[0] / self.square_size / self.square_scale
        y_sq = self.view_bleed_sq + self.view_maze_y_sq - 0.3 + xy[1] / self.square_size / self.square_scale
        if do_round:
            return round(x_sq), round(y_sq)
        else:
            return x_sq, y_sq

    def square_check(self, xy, wins_dict, active_wins):
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
                    wins_dict['realm'].spawn_realmtext('new_txt', "%s gold" % lt.props['amount'], (0, 0), (0, 0),
                                                       'bright_gold', lt, (0, 0), 45, 'large', 16, 0, 0)
                    self.pc.char_sheet.gold_coins += lt.props['amount']
                    self.maze.flag_array[y_sq][x_sq].item.remove(lt)
                    self.maze.loot.remove(lt)
                    # self.loot_short.remove(lt)
                    wins_dict['inventory'].updated = True
                    return False
                else:
                    self.maze.flag_array[y_sq][x_sq].item.remove(lt)
                    self.mouse_pointer.catcher[0] = lt
                    self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                    self.mouse_pointer.image = lt.props['image_floor'][0]
                    self.maze.loot.remove(lt)
                    # self.loot_short.remove(lt)
                    # self.render_update()
                    return False
        if flags.door is not None:
            # doors
            if flags.door.use(self.pc):
                self.maze.flag_array[y_sq][x_sq].mov = not flags.door.shut
                self.maze.flag_array[y_sq][x_sq].light = (not flags.door.shut) or (flags.door.grate)
                self.calc_vision_alt()
                self.shortlists_update(mobs=True)
                # self.render_update()
            return False
        if flags.obj is not None:
            # objects
            flags.obj.use(wins_dict, active_wins, self.pc)
            return False
        return True

    def mob_check(self, xy, m_bttn, wins_dict, active_wins):
        x_sq, y_sq = self.xy_pixels_to_squares(xy, do_round=False)
        for mon in self.mobs_short:
            if mon.alive == False:
                continue
            if not self.maze.flag_array[round(mon.y_sq)][round(mon.x_sq)].vis:
                continue
            if mon.x_sq <= x_sq + 0.5 < mon.x_sq + 1 and mon.y_sq <= y_sq + 0.5 < mon.y_sq + 1:
                wins_dict['target'].aim(mon, self)
                active_wins.insert(0, wins_dict['target'])
                return True
        try:
            active_wins.remove(wins_dict['target'])
            wins_dict['target'].drop_aim()
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
                # Somehow a few traps have None in their coordinates after all. I dont know why. Meanwhile...
                if tr.x_sq is None or tr.y_sq is None:
                    continue
                if left_sq <= tr.x_sq <= right_sq and top_sq <= tr.y_sq <= bottom_sq:
                    self.traps_short.add(tr)
                elif tr in self.traps_short:
                    self.traps_short.remove(tr)"""

        # mobs
        if mobs or everything:
            for mob in self.maze.mobs:
                # Mobs have to live in darkness, but freeze outside drawing canvas. So...
                if left_sq <= mob.x_sq <= right_sq and top_sq <= mob.y_sq <= bottom_sq:
                    self.mobs_short.add(mob)
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
                                        self.resources.colors['bg'], 'center', 'bottom', 144, 64, shadow=True)
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
