# char inventory window
import pygame
import settings
from library import ui, textinput, pydraw
from objects import maze, pc, charsheet


class Inventory:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.animations = animations
        self.inventory_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.inv_w = 320
        self.inv_h = 510
        self.inv_offset_x = 8
        self.inv_offset_y = 8
        self.rendered_inv = pygame.Surface((self.inv_w, self.inv_h))
        self.create_elements(log=True)
        self.render()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        if event.type == pygame.KEYDOWN:
            if self.inventory_ui.key_focus is not None:
                if self.inventory_ui.key_focus.page is not None and self.inventory_ui.key_focus.page != self.inventory_ui.page:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.inventory_ui.key_focus.mode = 0

                    self.inventory_ui.key_focus.do_sound(2)

                    self.inventory_ui.key_focus = None
                    return
                self.inventory_ui.key_focus.text_obj.caption = textinput.do_edit(event.unicode,
                                                                                 self.inventory_ui.key_focus.text_obj.caption,
                                                                                 self.inventory_ui.key_focus.maxlen)

                self.inventory_ui.key_focus.do_sound(1)

                self.inventory_ui.key_focus.text_obj.actual_width, self.inventory_ui.key_focus.text_obj.max_height = self.inventory_ui.key_focus.text_obj.get_text_height()
                self.inventory_ui.key_focus.text_obj.render()
                self.inventory_ui.key_focus.render()
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # light up main menu buttons on hovering
            pass

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.inventory_ui.mouse_actions(event), pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.inventory_ui.page:
            return
        # PAGE 0

        self.inventory_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        inv_sckt_size = 48
        inv_sckt_left = 16
        inv_sckt_top = 256
        inv_sckt_per_row = 6
        inv_sckt_total = 24
        # INVENTORY
        inv_texture = self.inventory_ui.random_texture((self.inv_w, self.inv_h), 'black_rock')
        inv_image = pydraw.square((0, 0), (self.inv_w, self.inv_h),
                              (self.inventory_ui.resources.colors['gray_light'],
                             self.inventory_ui.resources.colors['gray_dark'],
                             self.inventory_ui.resources.colors['gray_mid'],
                             self.inventory_ui.resources.colors['black']),
                              sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                              sq_image=inv_texture)
        # INVENTORY BACKGROUND
        inv_image = pydraw.square((inv_sckt_left - 1, inv_sckt_top - 1),
                                  (inv_sckt_per_row * inv_sckt_size + 2,
                                   inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                  (self.inventory_ui.resources.colors['gray_light'],
                                   self.inventory_ui.resources.colors['gray_dark'],
                                   self.inventory_ui.resources.colors['gray_mid'],
                                   self.inventory_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=inv_image, same_surface=True)
        inv_panel = self.inventory_ui.panel_add('inv_panel', (0, 0), (self.inv_w, self.inv_h), images=(inv_image,), page=None)
        # INVENTORY SOCKETS
        inv_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                     (self.inventory_ui.resources.colors['gray_light'],
                                      self.inventory_ui.resources.colors['gray_dark'],
                                      self.inventory_ui.resources.colors['gray_mid'],
                                      self.inventory_ui.resources.colors['gray_darker']),
                                     sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                     sq_image=None)
        for i in range(0, 24):
            s_x = inv_sckt_left + inv_sckt_size * (i % inv_sckt_per_row)
            s_y = inv_sckt_top + inv_sckt_size * (i // inv_sckt_per_row)
            inv_socket = self.inventory_ui.panel_add('inv_sckt_%s' % i, (s_x, s_y), (inv_sckt_size, inv_sckt_size),
                                                     images=(inv_sckt_img,), page=None)
            self.inventory_ui.interactives.append(inv_socket)

        eq_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                     (self.inventory_ui.resources.colors['gray_light'],
                                      self.inventory_ui.resources.colors['gray_dark'],
                                      self.inventory_ui.resources.colors['gray_mid'],
                                      self.inventory_ui.resources.colors['gray_darker']),
                                     sq_outsize=1, sq_bsize=2, sq_ldir=2, sq_fill=False,
                                     sq_image=None)
        # EQUIPPED ITEMS
        eqs_list = (
            self.inventory_ui.panel_add('inv_eq_head', (self.inv_w // 2 - inv_sckt_size // 2, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_chest', (self.inv_w // 2 - inv_sckt_size // 2, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_mainhand', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_offhand', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_ring1', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 144),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_ring1', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 144),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_mainhand', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None),
            self.inventory_ui.panel_add('inv_eq_offhand', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None)
        )
        for eqs in eqs_list:
            self.inventory_ui.interactives.append(eqs)

        win_name = self.inventory_ui.text_add('inv_win_title', (0, 0),
                                            caption='Inventory',
                                            h_align='left', v_align='top', size=(self.inv_w, 16), cap_color='sun')

        gold_sum = self.inventory_ui.text_add('inv_gold', (inv_sckt_left - 1,
                                              inv_sckt_top + inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                              caption='* 600,000,000', cap_font='def_bold',
                                              h_align='left', v_align='top', size=(self.inv_w //2, 16),
                                              cap_color='bright_gold')
        self.inventory_ui.interactives.append(gold_sum)
        self.inventory_ui.interactives.append(win_name)
        self.inventory_ui.interactives.append(inv_panel)


    def tick(self, pygame_settings, mouse_pointer):
        self.inventory_ui.tick(pygame_settings, mouse_pointer)

    def render(self):
        self.inventory_ui.draw(self.rendered_inv)

    def draw(self, surface):
        surface.blit(self.rendered_inv, (self.inv_offset_x, self.inv_offset_y))

