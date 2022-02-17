# options window
import pygame
from library import textinput, pydraw, maths
from components import ui


class Options:
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
        self.win_w = 272
        self.win_h = 28 + 8 + 40 + 8 + 40 + 8 + 40 + 8
        self.offset_x = 8
        self.offset_y = 8

        self.updated = False
        self.win_rendered = None

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)
        self.updated = True
        self.offset_x = (self.pygame_settings.screen_res[0] - self.win_w) // 2
        self.offset_y = (self.pygame_settings.screen_res[1] - self.win_h) // 2
        self.active_wins.insert(0, self.wins_dict['options'])
        self.wins_dict['realm'].pause = True

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.active_wins.remove(self.wins_dict['options'])

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
            elif event.key == pygame.K_SPACE:
                pass

        # return True if interaction was made to prevent other windows from responding to this event
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))
        return True

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
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['options'])
                self.active_wins.insert(0, self.wins_dict['options'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])

        # PAGE 0
        if element.id == 'bttn_save_exit' and m_bttn == 1 and mb_event == 'up':
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, self.wins_dict['overlay'], 'fade_out',
                                                         (20, None))
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self, 'game_save_and_exit',
                                                         ())
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['overlay'], 'fade_in',
                                                         (20, None))
        elif element.id == 'bttn_trade' and m_bttn == 1 and mb_event == 'up':
            self.end()
            self.wins_dict['realm'].pause = False
            self.wins_dict['trade'].launch(self.pc)
        elif element.id == 'bttn_continue' and m_bttn == 1 and mb_event == 'up':
            self.end()
            self.wins_dict['realm'].pause = False

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def game_save_and_exit(self):
        self.wins_dict['pools'].close_all_wins(self.pc)
        self.active_wins.clear()
        self.wins_dict['pools'].pc = None
        self.wins_dict['app_title'].char_save(self.pc, self.wins_dict['realm'].maze)
        self.wins_dict['app_title'].maze_save(self.pc, self.wins_dict['realm'].maze)
        self.wins_dict['app_title'].create_savegames()
        self.wins_dict['app_title'].char_loaded_info_update()
        self.active_wins.append(self.wins_dict['app_title'])

    # interface creation
    def create_elements(self, log=True):
        border_w = 8
        menu_btn_h = 40
        menu_btn_w = 256
        bttn_save_exit = self.win_ui.button_add('bttn_save_exit', xy=(0,0), caption='Save and Exit',
                                         size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                         cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        bttn_save_exit.rendered_rect.midtop = (self.win_w // 2, 28)
        self.win_ui.interactives.append(bttn_save_exit)

        bttn_trade = self.win_ui.button_add('bttn_trade', xy=(0, 0), caption='Trading Post',
                                                size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                                page=None)
        bttn_trade.rendered_rect.midtop = (self.win_w // 2, 28 + 8 + menu_btn_h)
        self.win_ui.interactives.append(bttn_trade)

        bttn_continue = self.win_ui.button_add('bttn_continue', xy=(0, 0), caption='Continue',
                                               size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                               cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                               page=None)
        bttn_continue.rendered_rect.midtop = (self.win_w // 2, 28 + (8 + menu_btn_h) * 2)
        self.win_ui.interactives.append(bttn_continue)

        opt_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        opt_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                             self.resources.colors['gray_dark'],
                             self.resources.colors['gray_mid'],
                             self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=opt_texture)

        opt_panel = self.win_ui.panel_add('opt_panel', (0, 0), (self.win_w, self.win_h), images=(opt_image,), page=None)

        # window header
        header_texture = self.win_ui.random_texture((self.win_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w, 19),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.win_ui.text_add('win_header', (0, 0), (self.win_w, 19),
                                          caption='Options',
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(opt_panel)
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render(self, chs=True):
        # update
        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))

