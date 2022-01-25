# char inventory window
import pygame
from library import textinput, pydraw
from objects import ui


# from objects import maze, pc, charsheet


class Inventory:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.inventory_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.pc = None
        self.inv_w = 320
        self.inv_h = 510
        self.offset_x = 8
        self.offset_y = 8
        self.inv_sckt_total = 24
        self.inv_sockets_list = []
        self.eq_sockets_list = None
        self.inv_sockets_image = None

        self.gold_sum = None

        self.rendered_inv = pygame.Surface((self.inv_w, self.inv_h)).convert()

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)

    def end(self):
        self.inventory_ui.decoratives.clear()
        self.inventory_ui.interactives.clear()
        self.inv_sockets_list.clear()
        self.eq_sockets_list = None

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
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
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.inv_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.inv_h):
                return False
            for i in range(len(self.inv_sockets_list) - 1, -1, -1):
                if self.inv_sockets_list[i].rendered_rect.collidepoint(
                        (mouse_x - self.offset_x, mouse_y - self.offset_y)):
                    if not self.inv_sockets_list[i].mouse_over:
                        self.inv_sockets_list[i].mouse_over = True
                        if not self.inv_sockets_list[i].popup_active:
                            self.context_info_update(self.inv_sockets_list[i], wins_dict, active_wins)
                else:
                    if self.inv_sockets_list[i].mouse_over:
                        self.inv_sockets_list[i].mouse_over = False
                        if self.inv_sockets_list[i].popup_active:
                            self.inv_sockets_list[i].popup_active = False
                            if wins_dict['context'] in active_wins:
                                active_wins.remove(wins_dict['context'])
            for i in range(len(self.eq_sockets_list) - 1, -1, -1):
                if self.eq_sockets_list[i].rendered_rect.collidepoint(
                        (mouse_x - self.offset_x, mouse_y - self.offset_y)):
                    if not self.eq_sockets_list[i].mouse_over:
                        self.eq_sockets_list[i].mouse_over = True
                        if not self.eq_sockets_list[i].popup_active:
                            self.context_info_update(self.eq_sockets_list[i], wins_dict, active_wins)
                else:
                    if self.eq_sockets_list[i].mouse_over:
                        self.eq_sockets_list[i].mouse_over = False
                        if self.eq_sockets_list[i].popup_active:
                            self.eq_sockets_list[i].popup_active = False
                            if wins_dict['context'] in active_wins:
                                active_wins.remove(wins_dict['context'])
            return True

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.inventory_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.inventory_ui.page:
            return
        if wins_dict['realm'] in active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                active_wins.remove(wins_dict['inventory'])
                active_wins.insert(0, wins_dict['inventory'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                if self.offset_x < 0:
                    self.offset_x = 0
                elif self.offset_x > pygame_settings.screen_res[0] - self.inv_w:
                    self.offset_x = pygame_settings.screen_res[0] - self.inv_w
                if self.offset_y < 0:
                    self.offset_y = 0
                elif self.offset_y > pygame_settings.screen_res[1] - self.inv_h:
                    self.offset_y = pygame_settings.screen_res[1] - self.inv_h

        # PAGE 0
        if m_bttn == 1 and 'itm' in element.tags:
            # removing popup if active
            if wins_dict['context'] in active_wins:
                active_wins.remove(wins_dict['context'])
            item_info = [element.tags[0], element.id]
            if mb_event == 'down' and self.mouse_pointer.drag_item is None:
                if item_info[1] < len(item_info[0]) and item_info[0][item_info[1]] is not None:
                    self.mouse_pointer.drag_item = item_info
                    # exchange between inventory socket and mouse

                    item_down = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                    self.mouse_pointer.image = item_down.props['image_inventory'][0]

            elif mb_event == 'up' and self.mouse_pointer.drag_item is not None:
                item_dragging = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                if item_info[1] < len(item_info[0]):
                    if item_info[0][item_info[1]] is None:
                        item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = \
                            self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
                    else:
                        if self.mouse_pointer.drag_item[1] >= len(self.mouse_pointer.drag_item[0]):
                            self.mouse_pointer.drag_item[0].append(None)
                            self.mouse_pointer.drag_item[1] = len(self.mouse_pointer.drag_item[0]) - 1
                        item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = \
                            self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]
                else:
                    item_info[0].append(item_dragging)
                    item_info[1] = len(item_info[0]) - 1
                    self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = None

                if (item_info[0][item_info[1]].props['item_type'] not in item_info[0].filters['item_types']
                        or item_dragging.props['item_type'] not in self.mouse_pointer.drag_item[0].filters['item_types']):
                    item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = \
                        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][item_info[1]]

                if (self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] is None
                        and self.mouse_pointer.drag_item[0] == wins_dict['realm'].maze.loot):
                    # wins_dict['realm'].loot_short.remove(item_dragging)
                    del self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]

                self.mouse_pointer.drag_item = None
                self.mouse_pointer.image = None

                self.clean_inv_tail()

                self.pc.char_sheet.calc_stats()
            self.render_slots(wins_dict, active_wins)

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
        pass

    def clean_inv_all(self):
        for sckt in reversed(self.pc.char_sheet.inventory):
            if sckt is None:
                self.pc.char_sheet.inventory.remove(sckt)

    def context_info_update(self, element, wins_dict, active_wins):
        # Here I need to write making changes to context_info_rich element
        if 'itm' in element.tags:
            if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
                inv_itm = element.tags[0][element.id]
                self.context_define(inv_itm, element, wins_dict, active_wins)

    def context_define(self, itm, element, wins_dict, active_wins):
        if itm.props['item_type'] in ('wpn_melee', 'wpn_ranged'):
            wins_dict['context'].update_elements_weapon(self.pc, itm, self.mouse_pointer.xy)
        element.popup_active = True
        active_wins.insert(0, wins_dict['context'])

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
        inv_panel = self.inventory_ui.panel_add('inv_panel', (0, 0), (self.inv_w, self.inv_h), images=(inv_image,),
                                                page=None)

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
            inv_socket = self.inventory_ui.panel_add(i, (s_x, s_y), (inv_sckt_size, inv_sckt_size),
                                                     images=(self.inv_sckt_img,), page=None, img_stretch=True,
                                                     tags=(self.pc.char_sheet.inventory, 'itm'))
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
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2, 48),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[0], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2, 108),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[1], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2 - 60, 108),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[2], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2 + 60, 108),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[3], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2 - 60, 168),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[4], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2 + 60, 168),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[5], 'itm')),
            self.inventory_ui.panel_add(0, (self.inv_w // 2 - inv_sckt_size // 2 - 60, 48),
                                        (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                        img_stretch=True, tags=(self.pc.char_sheet.equipped[6], 'itm')),
        )

        # window header
        header_texture = self.inventory_ui.random_texture((self.inv_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.inv_w, 19),
                                   (self.inventory_ui.resources.colors['gray_light'],
                                    self.inventory_ui.resources.colors['gray_dark'],
                                    self.inventory_ui.resources.colors['gray_mid'],
                                    self.inventory_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.inventory_ui.text_add('win_header', (0, 0), (self.inv_w, 19),
                                                caption='Inventory',
                                                h_align='center', v_align='middle', cap_color='sun',
                                                images=(header_img,))

        self.gold_sum = self.inventory_ui.text_add('inv_gold', (inv_sckt_left - 1 + 24,
                                                                inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 8),
                                                   caption='* 600,000,000', cap_font='def_bold',
                                                   h_align='left', v_align='bottom', size=(self.inv_w // 2, 24),
                                                   cap_color='bright_gold')

        coins_icon = self.inventory_ui.panel_add('coins_icon',
                                                 (inv_sckt_left - 1,
                                                  inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                                 (24, 24),
                                                 images=(self.inventory_ui.tilesets.get_image(
                                                     *self.inventory_ui.resources.sprites['gold_coins_icon'])),
                                                 page=None, img_stretch=True)

        self.inventory_ui.interactives.extend(self.eq_sockets_list)
        self.inventory_ui.interactives.append(self.gold_sum)
        self.inventory_ui.interactives.append(win_header)
        self.inventory_ui.interactives.append(coins_icon)
        self.inventory_ui.interactives.append(inv_panel)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.inventory_ui.tick(pygame_settings, mouse_pointer)
        if self.inventory_ui.updated:
            self.render()

    def render_slots(self, wins_dict, active_wins):
        for win in ('inventory','skillbook'):
            if wins_dict[win] in active_wins:
                wins_dict[win].render()

    def render(self, inv=True, eq=True, gold=True):
        # backpack update
        if self.pc is not None:
            if gold:
                self.gold_sum.text_obj.caption = str(self.pc.char_sheet.gold_coins)
                self.gold_sum.text_obj.render()
                self.gold_sum.render()
            if inv:
                for s_ind in range(0, len(self.inv_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.inventory) or self.pc.char_sheet.inventory[s_ind] is None:
                        self.inv_sockets_list[s_ind].images = (self.inv_sckt_img,)
                    elif (self.mouse_pointer.drag_item is not None and self.mouse_pointer.drag_item[0] == self.pc.char_sheet.inventory
                        and s_ind == self.mouse_pointer.drag_item[1]):
                        self.inv_sockets_list[s_ind].images = (self.inv_sckt_img,)
                    else:
                        self.inv_sockets_list[s_ind].images = self.pc.char_sheet.inventory[s_ind].props[
                            'image_inventory']
            if eq:
                for s_ind in range(0, len(self.eq_sockets_list)):
                    if len(self.pc.char_sheet.equipped[s_ind]) == 0 or self.pc.char_sheet.equipped[s_ind][0] is None:
                        self.eq_sockets_list[s_ind].images = (self.inv_sckt_img,)
                    else:
                        self.eq_sockets_list[s_ind].images = self.pc.char_sheet.equipped[s_ind][0].props['image_inventory']

        self.inventory_ui.draw(self.rendered_inv)

    def draw(self, surface):
        surface.blit(self.rendered_inv, (self.offset_x, self.offset_y))
