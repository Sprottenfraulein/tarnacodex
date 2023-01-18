# splitter window
import pygame
import settings
from components import ui, treasure
from library import pydraw, maths, textinput


class Splitter:
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

        self.win_rendered = None
        self.win_w = 240
        self.win_h = 128
        self.offset_x = 0
        self.offset_y = 0

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.field_number_edit = None
        self.amount = 0
        self.value_min = 0
        self.value_max = 0
        self.delayed_action = None

        # self.create_elements()

        self.updated = True

    def launch(self, pc, label, def_value, value_min, value_max, delayed_action):
        self.pc = pc
        self.value_min = value_min
        self.value_max = value_max
        self.amount = def_value
        self.delayed_action = delayed_action
        self.create_elements(label, def_value)
        self.updated = True
        self.offset_x = (self.pygame_settings.screen_res[0] - self.win_w) // 2
        self.offset_y = (self.pygame_settings.screen_res[1] - self.win_h) // 2
        self.active_wins.insert(0, self.wins_dict['splitter'])
        self.pygame_settings.audio.sound('paper_show')

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        if self in self.active_wins:
            self.active_wins.remove(self)

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
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
                updated_number = int(textinput.do_edit(event.unicode, self.win_ui.key_focus.text_obj.caption,
                                                    self.win_ui.key_focus.maxlen, letters=False) or '0')
                if updated_number <= self.value_max:
                    self.win_ui.key_focus.text_obj.caption = str(updated_number)
                    self.amount = updated_number
                else:
                    self.win_ui.key_focus.text_obj.caption = str(self.value_max)
                    self.amount = self.value_max

                self.win_ui.key_focus.do_sound(1)

                self.win_ui.key_focus.render_all()
                self.win_ui.updated = True
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                # running delayed action
                if self.delayed_action is not None:
                    getattr(self.delayed_action[0], self.delayed_action[1])(self.amount)
                self.end()
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
                self.active_wins.remove(self.wins_dict['splitter'])
                self.active_wins.insert(0, self.wins_dict['splitter'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])

        if element.id in ('input_number',) and m_bttn == 1 and mb_event == 'down':
            self.win_ui.key_focus = element
        if self.win_ui.key_focus is not None and element.id != 'input_number':
            self.win_ui.key_focus = None
            self.field_number_edit.mode = 0

        if element.id == 'bttn_cancel' and m_bttn == 1 and mb_event == 'up':
            self.end()
        elif element.id == 'bttn_ok' and m_bttn == 1 and mb_event == 'up':
            # running delayed action
            if self.delayed_action is not None:
                getattr(self.delayed_action[0], self.delayed_action[1])(self.amount)
            self.end()

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def create_elements(self, label, def_value):
        # INVENTORY
        spl_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        spl_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=spl_texture)

        spl_panel = self.win_ui.panel_add('tar_panel', (0, 0), (self.win_w, self.win_h), images=(spl_image,),
                                          page=None)

        splitter_string = self.win_ui.text_add('splitter_string', xy=(4, 32), size=(self.win_w - 8, 24),
                                              caption=label, cap_font='def_bold',
                                              h_align='center', v_align='top', cap_color='sun',
                                              images=None)

        # NUMBER INPUT FIELD
        self.field_number_edit = self.win_ui.edit_add('input_number', (32, splitter_string.rendered_rect.bottom),
                                                      caption=str(def_value),
                                                      sounds=self.win_ui.snd_packs['text_input'],
                                                      cap_font='def_normal',
                                                      size=(self.win_w - 64, 28),
                                                      h_align='center', page=None)

        spl_btn_w = 80
        spl_btn_h = 24
        border_w = 8
        bttn_ok = self.win_ui.button_add('bttn_ok', xy=(0, 0), caption='OK',
                                         size=(spl_btn_w, spl_btn_h),
                                         cap_font='def_bold', cap_size=24,
                                         cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        bttn_ok.rendered_rect.bottomright = (self.win_w - border_w, self.win_h - border_w)
        self.win_ui.interactives.append(bttn_ok)
        bttn_cancel = self.win_ui.button_add('bttn_cancel', xy=(0, 0), caption='CANCEL',
                                         size=(spl_btn_w, spl_btn_h),
                                         cap_font='def_bold', cap_size=24,
                                         cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        bttn_cancel.rendered_rect.bottomleft = (border_w, self.win_h - border_w)
        self.win_ui.interactives.append(bttn_cancel)

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
                                          caption="Divide",
                                          h_align='center', v_align='middle', cap_color='sun',
                                          images=(header_img,))

        self.win_ui.interactives.append(self.field_number_edit)
        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(splitter_string)
        self.win_ui.decoratives.append(spl_panel)

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
