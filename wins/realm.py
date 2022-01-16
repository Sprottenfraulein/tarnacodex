import pygame
from library import calc2darray, maths
from objects import dbrequests
import math


class Realm:
    def __init__(self, pygame_settings, resources, tile_sets, anims, db, mouse_pointer):
        self.pygame_settings = pygame_settings
        self.resources = resources
        self.tile_sets = tile_sets
        self.anims = anims
        self.db = db
        self.mouse_pointer = mouse_pointer

        self.doors_short = set()
        self.traps_short = set()

        self.draw_view_maze = False
        self.redraw_maze_decor = True
        self.redraw_maze_obj = True
        self.redraw_pc = True
        self.square_size = 24
        self.square_scale = 2
        self.view_bleed_sq = 2
        self.view_maze_top = 24
        self.view_maze_left = 24
        self.view_maze_x_sq = 0
        self.view_maze_y_sq = 0
        self.view_maze_h_div = 2  # 2 - center , 3 - char to the left, 1.5 - char to the right
        self.view_maze_v_div = 2
        self.view_maze_width_sq = math.ceil(self.pygame_settings.screen_res[0] / self.square_scale / self.square_size)
        self.view_maze_height_sq = math.ceil(self.pygame_settings.screen_res[1] / self.square_scale / self.square_size)
        self.ren_x_sq, self.ren_y_sq = 0, 0

        self.view_size_scaled = self.pygame_settings.screen_res

        self.view_maze_follow = None
        self.maze = None
        self.pc = None

        self.view_maze_surface = None

    def launch(self, audio, settings):
        # game pack must include dungeon set, character
        self.view_maze_surface = pygame.Surface(((self.view_maze_width_sq + self.view_bleed_sq * 2) * self.square_size * self.square_scale,
                                                (self.view_maze_height_sq + self.view_bleed_sq * 2) * self.square_size * self.square_scale),
                                                pygame.HWSURFACE)
        self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
        self.render_update()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
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
                if self.view_maze_follow:
                    self.view_maze_follow = None
                else:
                    self.view_maze_follow = self.pc
            if event.key == pygame.K_i:
                # wins_dict['inventory'].launch(pygame_settings.audio)
                if wins_dict['inventory'] in active_wins:
                    active_wins.remove(wins_dict['inventory'])
                    self.view_maze_h_div = 2
                else:
                    active_wins.insert(0, wins_dict['inventory'])
                    self.view_maze_h_div = 1.5
                self.view_maze_update(self.pc.x_sq, self.pc.y_sq)
                self.render_update()
            if event.key == pygame.K_p:
                self.pc.char_sheet.inventory.append(dbrequests.treasure_get_by_id(self.db.cursor, 'treasure', 3))
                print(*self.pc.char_sheet.inventory)

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # self.view_maze_x_sq -= 1
                self.pc.move_instr_x = 0
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                # self.view_maze_y_sq -= 1
                self.pc.move_instr_y = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if not self.square_check(mouse_x, mouse_y, event.button) and event.button == 1:
                self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        elif event.type == pygame.MOUSEMOTION and (self.pc.move_instr_y != 0 or self.pc.move_instr_x != 0):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.pc.move_instr_x, self.pc.move_instr_y = self.mouse_move(mouse_x, mouse_y)

    def tick(self, pygame_settings, mouse_pointer):
        self.maze.tick()
        self.pc.tick(self)



    def draw(self, surface):
        self.stage_display(surface)

    def stage_display(self, screen):
        # world and gui drawing
        if not self.draw_view_maze:
            return

        if self.redraw_pc:
            self.pc_display(self.view_maze_surface)

        # screen.blit(self.view_maze_surface, (self.view_maze_left, self.view_maze_top))
        pygame.transform.scale(self.view_maze_surface.subsurface(
            (round((self.view_bleed_sq - (self.ren_x_sq - self.view_maze_x_sq)) * self.square_size),
             round((self.view_bleed_sq - (self.ren_y_sq - self.view_maze_y_sq)) * self.square_size),
             self.view_maze_width_sq * self.square_size,
             self.view_maze_height_sq * self.square_size,)
        ), self.view_size_scaled, screen)

    def view_maze_update(self, x_sq, y_sq):
        self.view_maze_x_sq = x_sq - round(self.view_maze_width_sq / self.view_maze_h_div) - 1
        self.view_maze_y_sq = y_sq - round(self.view_maze_height_sq / self.view_maze_v_div) - 1

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
                        try:
                            surface.blit(decors[0],
                                         ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                          (ren_pos_y - self.ren_y_sq) * self.square_size))
                        except TypeError:
                            # print('Realm.Stage_display: Wrong tile.')
                            pass

        if self.redraw_maze_obj:
            for dr in self.doors_short:
                if not self.maze.flag_array[dr.y_sq][dr.x_sq].vis:
                    continue
                try:
                    surface.blit(dr.image[self.maze.anim_frame],
                                 ((dr.x_sq - self.ren_x_sq) * self.square_size + dr.off_x,
                                  (dr.y_sq - self.ren_y_sq) * self.square_size + dr.off_y))
                except IndexError:
                    surface.blit(dr.image[(self.maze.anim_frame + 1) % (len(dr.image))],
                                 ((dr.x_sq - self.ren_x_sq) * self.square_size + dr.off_x,
                                  (dr.y_sq - self.ren_y_sq) * self.square_size + dr.off_y))

        ren_left = left_sq
        ren_right = right_sq
        ren_top = top_sq
        ren_bottom = bottom_sq

        ren_pos_x = ren_left
        ren_pos_y = ren_top

        ren_count = 0
        ren_max = (ren_right - ren_left) * (ren_bottom - ren_top)
        while ren_count < ren_max:
            # body
            if (0 <= ren_pos_y < self.maze.height) and (0 <= ren_pos_x < self.maze.width):

                flags = self.maze.flag_array[ren_pos_y][ren_pos_x]
                if flags.vis:
                    decors = self.maze.decor_array[ren_pos_y][ren_pos_x]

                    if len(decors) > 1:
                        for k in range(1, len(decors)):
                            if k == 1 and self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(
                                    self.pc.y_sq) == ren_pos_y:
                                surface.blit(self.pc.image[self.pc.anim_frame],
                                             ((self.pc.x_sq - self.ren_x_sq - 0.1) * self.square_size + self.pc.off_x,
                                              (self.pc.y_sq - self.ren_y_sq - 0.1) * self.square_size + self.pc.off_y))
                            if self.redraw_maze_decor:
                                try:
                                    surface.blit(decors[k],
                                                        ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                                         (ren_pos_y - self.ren_y_sq) * self.square_size))
                                except TypeError:
                                    # print('Realm.Stage_display: Wrong tile.')
                                    pass
                    else:
                        if self.redraw_pc and round(self.pc.x_sq) == ren_pos_x and round(
                                self.pc.y_sq) == ren_pos_y:
                            surface.blit(self.pc.image[self.pc.anim_frame],
                                         ((self.pc.x_sq - self.ren_x_sq - 0.1) * self.square_size + self.pc.off_x,
                                          (self.pc.y_sq - self.ren_y_sq - 0.1) * self.square_size + self.pc.off_y))

                    try:
                        if not self.maze.flag_array[ren_pos_y][ren_pos_x + 1].vis:
                            surface.blit(self.tile_sets.get_image('dark_edges', (24, 24), (0,))[0],
                                         ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                          (ren_pos_y - self.ren_y_sq) * self.square_size))
                        if not self.maze.flag_array[ren_pos_y + 1][ren_pos_x].vis:
                            surface.blit(self.tile_sets.get_image('dark_edges', (24, 24), (1,))[0],
                                         ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                          (ren_pos_y - self.ren_y_sq) * self.square_size))
                        if not self.maze.flag_array[ren_pos_y][ren_pos_x - 1].vis:
                            surface.blit(self.tile_sets.get_image('dark_edges', (24, 24), (2,))[0],
                                         ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                          (ren_pos_y - self.ren_y_sq) * self.square_size))
                        if not self.maze.flag_array[ren_pos_y - 1][ren_pos_x].vis:
                            surface.blit(self.tile_sets.get_image('dark_edges', (24, 24), (3,))[0],
                                         ((ren_pos_x - self.ren_x_sq) * self.square_size,
                                          (ren_pos_y - self.ren_y_sq) * self.square_size))

                    except IndexError:
                        # print('Realm.Stage_display: Wrong tile.')
                        pass

            if ren_pos_x == ren_right - 1 and ren_pos_y == ren_bottom - 1:
                break
            elif ren_pos_x == ren_left or ren_pos_y == ren_bottom - 1:
                ext = (ren_pos_y + 1 - ren_top + ren_pos_x + 1 - ren_left) - (ren_right - ren_left)
                if ext > 0:
                    ren_pos_x = ren_right - 1
                    ren_pos_y = ren_top + ext
                else:
                    ren_pos_x = ren_left + (ren_pos_y + 1 - ren_top + ren_pos_x + 1 - ren_left) - 1
                    ren_pos_y = ren_top
            else:
                ren_pos_x -= 1
                ren_pos_y += 1
                ren_count += 1

    def pc_display(self, surface):
        r_vm_x_sq = round(self.ren_x_sq + (round(self.pc.x_sq) - self.view_maze_x_sq) - 2)
        r_vm_y_sq = round(self.ren_y_sq + (round(self.pc.y_sq) - self.view_maze_y_sq) - 2)
        self.stage_render(self.view_maze_surface, r_vm_y_sq, r_vm_x_sq,
                          r_vm_y_sq + 4,
                          r_vm_x_sq + 4, clear=False)

    def end(self):
        # prepare game pack for return to BigLoop
        pass

    def calc_vision(self, flag_array, orig_xy, max_spaces, max_dist_hv, r_max=10):
        sq_list = calc2darray.fill2d(flag_array, {'light': False}, orig_xy, orig_xy, max_spaces, max_dist_hv,
                                     r_max=r_max)
        for sq_x, sq_y in sq_list:
            flag_array[sq_y][sq_x].vis = True

    def calc_vision_alt(self):
        orig_xy = round(self.pc.x_sq), round(self.pc.y_sq)
        # realm.calc_vision(realm.maze.flag_array, orig_xy, 100, (12, 8), r_max=10)
        calc2darray.calc_vision_rays(self.maze.flag_array, orig_xy[0], orig_xy[1], 10)

    def mouse_move(self, mouse_x, mouse_y):
        rads = maths.xy_dist_to_rads(mouse_x, mouse_y,
                                     (self.pc.x_sq - self.view_maze_x_sq - 1.4) * self.square_size * self.square_scale,
                                     (self.pc.y_sq - self.view_maze_y_sq - 1.4) * self.square_size * self.square_scale)

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
        else:   # -0.3 > rads >= -1.1
            move_instr_x = -1
            move_instr_y = 1
        return  move_instr_x, move_instr_y

    def square_check(self, mouse_x, mouse_y, m_bttn):
        mouse_x_sq = round(
            self.view_bleed_sq + self.view_maze_x_sq - 0.3 + mouse_x / self.square_size / self.square_scale)
        mouse_y_sq = round(
            self.view_bleed_sq + self.view_maze_y_sq - 0.3 + mouse_y / self.square_size / self.square_scale)
        try:
            flags = self.maze.flag_array[mouse_y_sq][mouse_x_sq]
        except IndexError:
            return False
        if not flags.vis:
            return None
        if flags.obj:
            # doors
            for dr in self.doors_short:
                if dr.x_sq == mouse_x_sq and dr.y_sq == mouse_y_sq:
                    if m_bttn != 1:
                        continue
                    pc_dist = maths.get_distance(self.pc.x_sq, self.pc.y_sq, mouse_x_sq, mouse_y_sq)
                    if pc_dist != 1:
                        return False
                    if dr.use(self.pc):
                        self.maze.flag_array[mouse_y_sq][mouse_x_sq].mov = not dr.shut
                        self.maze.flag_array[mouse_y_sq][mouse_x_sq].light = (not dr.shut) or (dr.grate)
                        self.calc_vision_alt()
                        self.render_update()
                    return True
        try:
            if flags.obj:
                print(flags.light, )
                return True
        except IndexError:
            pass
        return False

    def shortlists_update(self):
        left_sq = round(self.view_maze_x_sq - self.view_bleed_sq)
        top_sq = round(self.view_maze_y_sq - self.view_bleed_sq)
        bottom_sq = top_sq + self.view_maze_height_sq + self.view_bleed_sq * 3
        right_sq = left_sq + self.view_maze_width_sq + self.view_bleed_sq * 3

        # doors
        for dr in self.maze.doors:
            if left_sq <= dr.x_sq <= right_sq and top_sq <= dr.y_sq <= bottom_sq:
                self.doors_short.add(dr)
        # traps
        for tr in self.maze.traps:
            if tr.x_sq is None or tr.y_sq is None:
                continue
            if left_sq <= tr.x_sq <= right_sq and top_sq <= tr.y_sq <= bottom_sq:
                self.traps_short.add(tr)
