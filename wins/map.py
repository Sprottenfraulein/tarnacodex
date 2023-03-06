# dialogue window
import pygame
import math
from library import textinput, pydraw, maths
from components import ui


class Map:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.pygame_settings = pygame_settings
        self.resources = resources
        self.tilesets = tilesets
        self.animations = animations
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.wins_dict = None
        self.active_wins = None
        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db, mouse_pointer)

        self.pc = None
        self.win_w = 0
        self.win_h = 0
        self.offset_x = pygame_settings.screen_res[0] - 128
        self.offset_y = 32
        self.scale = 3
        self.border_w = 2
        self.header_h = 19
        self.paper_margin_w = 24
        self.map_panel = None

        self.updated = False
        self.win_rendered = None

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)
        self.updated = True
        self.active_wins.insert(0, self.wins_dict['map'])
        self.win_align()
        self.pygame_settings.audio.sound('paper_show')

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        if self in self.active_wins:
            self.active_wins.remove(self)
        self.pc = None

    def restart(self, pc):
        self.end()
        self.launch(pc)

    def event_check(self, event, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.win_ui.key_focus is not None:
                if self.win_ui.key_focus.page is not None and self.win_ui.page not in self.win_ui.key_focus.page:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.win_ui.key_focus.mode = 0

                    self.win_ui.key_focus.do_sound(2)

                    self.win_ui.key_focus = None
                    return
                self.win_ui.key_focus.text_obj.caption = textinput.do_edit(event.unicode,
                                                                           self.win_ui.key_focus.text_obj.caption,
                                                                           self.win_ui.key_focus.maxlen)

                self.win_ui.key_focus.do_sound(1)

                self.win_ui.key_focus.render_all()
                self.win_ui.updated = True

        # return True if interaction was made to prevent other windows from responding to this event
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None:
            for inter in self.win_ui.interactives:
                inter.release(1)
                inter.release(3)
            self.win_ui.updated = True
            return
        element, m_bttn, mb_event = inter_click

        if self.wins_dict['realm'] in self.active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
            in_realm = True
        else:
            in_realm = False

        if self.wins_dict['realm'] in self.active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['map'])
                self.active_wins.insert(0, self.wins_dict['map'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                self.win_align()
        elif element.id == 'win_header' and m_bttn == 3 and mb_event == 'down':
            self.active_wins.remove(self)
            # self.pc.char_sheet.itemlist_cleanall_inventory(self.wins_dict, self.pc)
            # self.end()
            if in_realm:
                targ_win = self.wins_dict['pools']
                bttn_id = 'map'
            else:
                targ_win = self.wins_dict['app_title']
                bttn_id = 'quick_map'
            for el in targ_win.win_ui.interactives:
                if el.id == bttn_id:
                    el.sw_op = False
                    el.mouse_up(1)
            self.wins_dict['pools'].updated = in_realm

        if element.id == 'bttn_scale_plus' and m_bttn == 1 and mb_event == 'up':
            self.scale += ((self.scale + 1) * self.wins_dict['realm'].maze.height + self.header_h) < self.pygame_settings.screen_res[1]
            self.restart(self.pc)
        elif element.id == 'bttn_scale_minus' and m_bttn == 1 and mb_event == 'up':
            self.scale -= self.scale > 2
            self.restart(self.pc)

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def win_align(self):
        framed_wins = [fw for fw in (
            self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'],
            self.wins_dict['inventory'], self.wins_dict['skillbook'], self.wins_dict['tasks'],
            self.wins_dict['map']
        ) if fw in self.active_wins]
        self.offset_x, self.offset_y = maths.rect_sticky_edges(
            (self.offset_x, self.offset_y, self.win_w, self.win_h),
            [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                            self.win_h,
                                                            0, 0, self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        maze = self.wins_dict['realm'].maze
        self.win_w, self.win_h = (maze.width * self.scale + self.border_w * 2 + self.paper_margin_w * 2,
                                  maze.height * self.scale + self.border_w * 2 + self.paper_margin_w * 2 + self.header_h)

        while ((self.scale + 1) * self.wins_dict['realm'].maze.height + self.header_h) >= self.pygame_settings.screen_res[1]:
            self.scale -= 1

        dlg_texture = self.tilesets.get_image('paper', (self.win_w // math.ceil(self.scale / 2), (self.win_h - self.header_h) // math.ceil(self.scale / 2)), (0,))[0]
        map_image = pydraw.square((0, 0), (self.win_w, self.win_h - self.header_h),
                                  (self.win_ui.resources.colors['gray_light'],
                             self.win_ui.resources.colors['gray_dark'],
                             self.win_ui.resources.colors['gray_mid'],
                             self.win_ui.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=dlg_texture, img_stretch=True)

        self.map_panel = self.win_ui.panel_add('dlg_panel', (0, 19), (self.win_w, self.win_h - 19), images=(map_image,), page=None)
        for i in range(maze.height):
            for j in range(maze.width):
                self.map_update(j, i)
        self.updated = True

        bttn_scale_plus = self.win_ui.button_add('bttn_scale_plus', xy=(0, 0),
                                           caption='+', size=(self.header_h, self.header_h), cap_font='def_bold', cap_size=24,
                                           cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        self.win_ui.interactives.append(bttn_scale_plus)
        bttn_scale_minus = self.win_ui.button_add('bttn_scale_minus', xy=(self.header_h, 0),
                                                 caption='-', size=(self.header_h, self.header_h), cap_font='def_bold', cap_size=24,
                                                 cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                                 page=None)
        self.win_ui.interactives.append(bttn_scale_minus)

        # window header
        header_text = 'Map'
        header_texture = self.win_ui.random_texture((self.win_w // 2, self.header_h // 2), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w - self.header_h * 2, self.header_h),
                                   (self.win_ui.resources.colors['gray_light'],
                                    self.win_ui.resources.colors['gray_dark'],
                                    self.win_ui.resources.colors['gray_mid'],
                                    self.win_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture, img_stretch=True)
        win_header = self.win_ui.text_add('win_header', (self.header_h * 2, 0), (self.win_w - self.header_h * 2, self.header_h),
                                          caption=header_text,
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(self.map_panel)
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

    def map_update_bulk(self, sq_list):
        for x_sq, y_sq in sq_list:
            self.map_update(x_sq, y_sq)
        self.updated = True

    def map_update(self, x_sq, y_sq):
        maze = self.wins_dict['realm'].maze
        flags = maze.flag_array[y_sq][x_sq]
        if flags.map is None:
            return
        byte = maze.array[y_sq][x_sq]
        map_sign = None
        if byte == '0':
            map_sign = 'tr_floor'
        elif byte == '.':
            map_sign = 'gr_floor'
        elif byte == '#':
            map_sign = 'wall'
        if flags.door is not None:
            map_sign = 'door'
            if flags.door.lock:
                map_sign = 'locked'
        if flags.obj is not None and flags.obj in maze.exits:
            map_sign = 'exit'

        if map_sign == 'wall':
            pygame.draw.rect(self.map_panel.rendered_panel, (20, 20, 20), (
            x_sq * self.scale + self.paper_margin_w, y_sq * self.scale + self.paper_margin_w, self.scale,
            self.scale))
        elif map_sign == 'tr_floor':
            pygame.draw.rect(self.map_panel.rendered_panel, (216, 184, 68), (
            x_sq * self.scale + self.paper_margin_w, y_sq * self.scale + self.paper_margin_w, self.scale,
            self.scale))
        elif map_sign == 'gr_floor':
            pygame.draw.rect(self.map_panel.rendered_panel, (206, 171, 126), (
            x_sq * self.scale + self.paper_margin_w, y_sq * self.scale + self.paper_margin_w, self.scale,
            self.scale))
        elif map_sign == 'door':
            pygame.draw.rect(self.map_panel.rendered_panel, (150, 100, 0), (
            x_sq * self.scale - 1 + self.paper_margin_w, y_sq * self.scale - 1 + self.paper_margin_w,
            self.scale + 2, self.scale + 2))
        elif map_sign == 'locked':
            pygame.draw.rect(self.map_panel.rendered_panel, (150, 0, 0), (
            x_sq * self.scale - 1 + self.paper_margin_w, y_sq * self.scale - 1 + self.paper_margin_w,
            self.scale + 2, self.scale + 2))
        elif map_sign == 'exit':
            pygame.draw.rect(self.map_panel.rendered_panel, (0, 150, 150), (
            x_sq * self.scale - 1 + self.paper_margin_w, y_sq * self.scale - 1 + self.paper_margin_w,
            self.scale + 2, self.scale + 2))
        self.updated = True

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render(self, chs=True):
        # update
        # self.map_panel.render()
        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
        pygame.draw.rect(surface, (0, 150, 0), (
            self.offset_x + round(self.pc.x_sq) * self.scale - 1 + self.paper_margin_w,
            self.offset_y + round(self.pc.y_sq) * self.scale - 1 + self.paper_margin_w + self.header_h,
            self.scale + 2, self.scale + 2), width=1)
