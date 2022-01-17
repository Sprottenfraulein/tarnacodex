# char inventory window
import pygame
import settings
from library import ui, textinput, pydraw
# from objects import maze, pc, charsheet


class Inventory:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.animations = animations
        self.inventory_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.pc = None
        self.inv_w = 320
        self.inv_h = 510
        self.inv_offset_x = 8
        self.inv_offset_y = 8
        self.inv_sckt_total = 24
        self.inv_sockets_list = []
        self.eq_sockets_list = None
        self.inv_sockets_image = None
        self.drag_socket = None

        self.rendered_inv = pygame.Surface((self.inv_w, self.inv_h))
        self.create_elements(log=True)

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
        click_x, click_y = self.mouse_pointer.xy
        return self.ui_click(self.inventory_ui.mouse_actions((click_x - self.inv_offset_x, click_y - self.inv_offset_y), event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.inventory_ui.page:
            return
        if wins_dict['realm'] in active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        # PAGE 0
        if m_bttn == 1 and element.id in ('inv_socket', 'eq_socket'):
            catch_excess = [None]
            if element.id == 'inv_socket':
                itm_index = (self.pc.char_sheet.inventory, self.inv_sockets_list.index(element), element.id)
            if element.id == 'eq_socket':
                itm_index = (self.pc.char_sheet.equipped, self.eq_sockets_list.index(element), element.id)
            if mb_event == 'down' and self.mouse_pointer.drag_loot is None:
                if itm_index[1] < len(itm_index[0]) and itm_index[0][itm_index[1]] is not None:
                    self.drag_socket = list(itm_index)
                    # exchange between inventory socket and mouse
                    self.mouse_pointer.drag_loot, itm_index[0][itm_index[1]] = itm_index[0][itm_index[1]], None
                    self.mouse_pointer.image = self.mouse_pointer.drag_loot.props['image_inventory'][0]
                    self.clean_inv_tail()
            elif mb_event == 'up' and self.mouse_pointer.drag_loot is not None:
                if not self.mouse_pointer.drag_loot.stashed:
                    self.drag_socket = [catch_excess, 0, None]
                if itm_index[1] < len(itm_index[0]):
                    if itm_index[0][itm_index[1]] is None:
                        itm_index[0][itm_index[1]] = self.mouse_pointer.drag_loot
                    elif self.drag_socket[1] < len(self.drag_socket[0]):
                        self.drag_socket[0][self.drag_socket[1]] = itm_index[0][itm_index[1]]
                        itm_index[0][itm_index[1]] = self.mouse_pointer.drag_loot
                    else:
                        self.drag_socket[0].append(itm_index[0][itm_index[1]])
                        self.drag_socket[1] = len(self.drag_socket[0]) - 1
                        itm_index[0][itm_index[1]] = self.mouse_pointer.drag_loot

                else:
                    self.pc.char_sheet.inventory.append(self.mouse_pointer.drag_loot)
                self.mouse_pointer.drag_loot.stashed = True
                self.mouse_pointer.drag_loot = None
                self.mouse_pointer.image = None
                if self.drag_socket[1] >= len(self.drag_socket[0]):
                    self.drag_socket[0].append(None)
                    self.drag_socket[1] = len(self.drag_socket[0]) - 1
                if ((element.id == 'eq_socket' and self.pc.char_sheet.eq_ids[itm_index[1]]
                    not in itm_index[0][itm_index[1]].props['equipment_type'])
                    or (self.drag_socket[0][self.drag_socket[1]] is not None
                    and self.drag_socket[2] == 'eq_socket' and self.pc.char_sheet.eq_ids[self.drag_socket[1]]
                    not in self.drag_socket[0][self.drag_socket[1]].props['equipment_type'])):
                        itm_index[0][itm_index[1]], self.drag_socket[0][self.drag_socket[1]] = \
                            self.drag_socket[0][self.drag_socket[1]], itm_index[0][itm_index[1]]

                if catch_excess[0] is not None:
                    self.mouse_pointer.drag_loot = catch_excess.pop()
                    self.mouse_pointer.drag_loot.stashed = False
                    self.mouse_pointer.image = self.mouse_pointer.drag_loot.props['image_inventory'][0]
            self.render()

        self.inventory_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def clean_inv_tail(self):
        for i in range(len(self.pc.char_sheet.inventory) - 1, -1, -1):
            if self.pc.char_sheet.inventory[i] is None:
                del self.pc.char_sheet.inventory[i]
            else:
                break
        else:
            self.pc.char_sheet.inventory.clear()

    def clean_inv_all(self):
        for sckt in reversed(self.pc.char_sheet.inventory):
            if sckt is None:
                self.pc.char_sheet.inventory.remove(sckt)

    # interface creation
    def create_elements(self, log=True):
        inv_sckt_size = 48
        inv_sckt_left = 16
        inv_sckt_top = 256
        inv_sckt_per_row = 6
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
                                   self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                  (self.inventory_ui.resources.colors['gray_light'],
                                   self.inventory_ui.resources.colors['gray_dark'],
                                   self.inventory_ui.resources.colors['gray_mid'],
                                   self.inventory_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=inv_image, same_surface=True)
        inv_panel = self.inventory_ui.panel_add('inv_panel', (0, 0), (self.inv_w, self.inv_h), images=(inv_image,), page=None)
        # INVENTORY SOCKETS
        self.inv_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                     (self.inventory_ui.resources.colors['gray_light'],
                                      self.inventory_ui.resources.colors['gray_dark'],
                                      self.inventory_ui.resources.colors['gray_mid'],
                                      self.inventory_ui.resources.colors['gray_darker']),
                                     sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                     sq_image=None)
        for i in range(0, 24):
            s_x = inv_sckt_left + inv_sckt_size * (i % inv_sckt_per_row)
            s_y = inv_sckt_top + inv_sckt_size * (i // inv_sckt_per_row)
            inv_socket = self.inventory_ui.panel_add('inv_socket', (s_x, s_y), (inv_sckt_size, inv_sckt_size),
                                                     images=(self.inv_sckt_img,), page=None, img_stretch=True)
            self.inventory_ui.interactives.append(inv_socket)
            self.inv_sockets_list.append(inv_socket)

        eq_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                     (self.inventory_ui.resources.colors['gray_light'],
                                      self.inventory_ui.resources.colors['gray_dark'],
                                      self.inventory_ui.resources.colors['gray_mid'],
                                      self.inventory_ui.resources.colors['gray_darker']),
                                     sq_outsize=1, sq_bsize=2, sq_ldir=2, sq_fill=False,
                                     sq_image=None)
        # EQUIPPED ITEMS
        # panel ids must match char_sheet.equipped keys
        self.eq_sockets_list = (
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 84),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 144),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 144),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 - 60, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True),
            self.inventory_ui.panel_add('eq_socket', (self.inv_w // 2 - inv_sckt_size // 2 + 60, 24),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None, img_stretch=True)
        )
        self.inventory_ui.interactives.extend(self.eq_sockets_list)

        win_name = self.inventory_ui.text_add('inv_win_title', (0, 0),
                                            caption='Inventory',
                                            h_align='left', v_align='top', size=(self.inv_w, 16), cap_color='sun')

        gold_sum = self.inventory_ui.text_add('inv_gold', (inv_sckt_left - 1,
                                              inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                              caption='* 600,000,000', cap_font='def_bold',
                                              h_align='left', v_align='top', size=(self.inv_w //2, 16),
                                              cap_color='bright_gold')
        self.inventory_ui.interactives.append(gold_sum)
        self.inventory_ui.decoratives.append(win_name)
        self.inventory_ui.decoratives.append(inv_panel)


    def tick(self, pygame_settings, mouse_pointer):
        self.inventory_ui.tick(pygame_settings, mouse_pointer)

    def render(self, inv=True, eq=True):
        # backpack update
        if self.pc is not None:
            if inv:
                for s_ind in range(0, len(self.inv_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.inventory) or self.pc.char_sheet.inventory[s_ind] is None:
                        self.inv_sockets_list[s_ind].images = (self.inv_sckt_img,)
                    else:
                        self.inv_sockets_list[s_ind].images = self.pc.char_sheet.inventory[s_ind].props['image_inventory']
            if eq:
                for s_ind in range(0, len(self.eq_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.equipped) or self.pc.char_sheet.equipped[s_ind] is None:
                        self.eq_sockets_list[s_ind].images = (self.inv_sckt_img,)
                    else:
                        self.eq_sockets_list[s_ind].images = self.pc.char_sheet.equipped[s_ind].props['image_inventory']

        self.inventory_ui.draw(self.rendered_inv)

    def draw(self, surface):
        surface.blit(self.rendered_inv, (self.inv_offset_x, self.inv_offset_y))

