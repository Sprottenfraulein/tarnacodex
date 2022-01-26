# char skillbook window
import pygame
from library import textinput, pydraw
from components import ui


class SkillBook:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.skillbook_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.pc = None
        self.skb_w = 320
        self.skb_h = 510
        self.offset_x = 8
        self.offset_y = 8
        self.skb_sckt_total = 24
        self.skb_sockets_list = []
        self.skb_sockets_image = None

        self.gold_sum = None

        self.rendered_skb = pygame.Surface((self.skb_w, self.skb_h)).convert()

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)

    def end(self):
        self.skillbook_ui.decoratives.clear()
        self.skillbook_ui.interactives.clear()
        self.skb_sockets_list.clear()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.skillbook_ui.key_focus is not None:
                if self.skillbook_ui.key_focus.page is not None and self.skillbook_ui.key_focus.page != self.skillbook_ui.page:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.skillbook_ui.key_focus.mode = 0

                    self.skillbook_ui.key_focus.do_sound(2)

                    self.skillbook_ui.key_focus = None
                    return
                self.skillbook_ui.key_focus.text_obj.caption = textinput.do_edit(event.unicode,
                                                                                 self.skillbook_ui.key_focus.text_obj.caption,
                                                                                 self.skillbook_ui.key_focus.maxlen)

                self.skillbook_ui.key_focus.do_sound(1)

                self.skillbook_ui.key_focus.text_obj.actual_width, self.skillbook_ui.key_focus.text_obj.max_height = self.skillbook_ui.key_focus.text_obj.get_text_height()
                self.skillbook_ui.key_focus.text_obj.render()
                self.skillbook_ui.key_focus.render()
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.skb_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.skb_h):
                return False
            for i in range(len(self.skb_sockets_list) - 1, -1, -1):
                if self.skb_sockets_list[i].page is not None and self.skb_sockets_list[i].page != self.skillbook_ui.page:
                    continue
                if self.skb_sockets_list[i].rendered_rect.collidepoint((mouse_x - self.offset_x, mouse_y - self.offset_y)):
                    if not self.skb_sockets_list[i].mouse_over:
                        self.skb_sockets_list[i].mouse_over = True
                        if not self.skb_sockets_list[i].popup_active:
                            self.context_info_update(self.skb_sockets_list[i], wins_dict, active_wins)
                else:
                    if self.skb_sockets_list[i].mouse_over:
                        self.skb_sockets_list[i].mouse_over = False
                        if self.skb_sockets_list[i].popup_active:
                            self.skb_sockets_list[i].popup_active = False
                            if wins_dict['context'] in active_wins:
                                active_wins.remove(wins_dict['context'])
            return True

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.skillbook_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.skillbook_ui.page:
            return
        if wins_dict['realm'] in active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                active_wins.remove(wins_dict['skillbook'])
                active_wins.insert(0, wins_dict['skillbook'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                if self.offset_x < 0:
                    self.offset_x = 0
                elif self.offset_x > pygame_settings.screen_res[0] - self.skb_w:
                    self.offset_x = pygame_settings.screen_res[0] - self.skb_w
                if self.offset_y < 0:
                    self.offset_y = 0
                elif self.offset_y > pygame_settings.screen_res[1] - self.skb_h:
                    self.offset_y = pygame_settings.screen_res[1] - self.skb_h

        # PAGE 0
        if m_bttn == 1 and 'skill' in element.tags:
            # removing popup if active
            if wins_dict['context'] in active_wins:
                active_wins.remove(wins_dict['context'])
            item_info = [element.tags[0], element.id]
            if mb_event == 'down' and self.mouse_pointer.drag_item is None:
                if item_info[1] < len(item_info[0]) and item_info[0][item_info[1]] is not None:
                    self.mouse_pointer.drag_item = item_info
                    # exchange between inventory socket and mouse

                    item_down = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                    self.mouse_pointer.image = item_down.props['image_book'][0]

            elif mb_event == 'up' and self.mouse_pointer.drag_item is not None:
                item_dragging = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                if item_info[1] < len(item_info[0]):
                    if item_info[0][item_info[1]] is None:
                        item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                            self.mouse_pointer.drag_item[1]] = \
                            self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                                item_info[1]]
                    else:
                        if self.mouse_pointer.drag_item[1] >= len(self.mouse_pointer.drag_item[0]):
                            self.mouse_pointer.drag_item[0].append(None)
                            self.mouse_pointer.drag_item[1] = len(self.mouse_pointer.drag_item[0]) - 1
                        item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                            self.mouse_pointer.drag_item[1]] = \
                            self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                                item_info[1]]
                else:
                    item_info[0].append(item_dragging)
                    item_info[1] = len(item_info[0]) - 1
                    self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] = None

                if (item_info[0][item_info[1]].props['item_type'] not in item_info[0].filters['item_types']
                        or item_dragging.props['item_type'] not in self.mouse_pointer.drag_item[0].filters[
                            'item_types']):
                    item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                        self.mouse_pointer.drag_item[1]] = \
                        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                            item_info[1]]

                if (self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] is None
                        and self.mouse_pointer.drag_item[0] == wins_dict['realm'].maze.loot):
                    # wins_dict['realm'].loot_short.remove(item_dragging)
                    del self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]

                self.mouse_pointer.drag_item = None
                self.mouse_pointer.image = None

                self.clean_skb_tail()
            self.render_slots(wins_dict, active_wins)

        self.skillbook_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def clean_skb_tail(self):
        for i in range(len(self.pc.char_sheet.skills) - 1, -1, -1):
            if self.pc.char_sheet.skills[i] is None:
                del self.pc.char_sheet.skills[i]
            else:
                break
        else:
            self.pc.char_sheet.skills.clear()

    def clean_skb_all(self):
        for sckt in reversed(self.pc.char_sheet.skills):
            if sckt is None:
                self.pc.char_sheet.skills.remove(sckt)

    def context_info_update(self, element, wins_dict, active_wins):
        # Here I need to write making changes to context_info_rich element
        if 'skill' in element.tags:
            if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
                inv_itm = element.tags[0][element.id]
                self.context_define(inv_itm, element, wins_dict, active_wins)

    def context_define(self, skill, element, wins_dict, active_wins):
        if skill.props['item_type'] in ('skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc'):
            wins_dict['context'].update_elements_skill(self.pc, skill, self.mouse_pointer.xy)
        element.popup_active = True
        active_wins.insert(0, wins_dict['context'])

    # interface creation
    def create_elements(self, log=True):
        skb_sckt_size = 48
        skb_sckt_left = 16
        skb_sckt_top = 256
        skb_sckt_per_row = 6
        # INVENTORY
        skb_texture = self.skillbook_ui.random_texture((self.skb_w, self.skb_h), 'black_rock')
        skb_image = pydraw.square((0, 0), (self.skb_w, self.skb_h),
                                  (self.skillbook_ui.resources.colors['gray_light'],
                             self.skillbook_ui.resources.colors['gray_dark'],
                             self.skillbook_ui.resources.colors['gray_mid'],
                             self.skillbook_ui.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=skb_texture)
        # INVENTORY BACKGROUND
        skb_image = pydraw.square((skb_sckt_left - 1, skb_sckt_top - 1),
                                  (skb_sckt_per_row * skb_sckt_size + 2,
                                   self.skb_sckt_total // skb_sckt_per_row * skb_sckt_size + 2),
                                  (self.skillbook_ui.resources.colors['gray_light'],
                                   self.skillbook_ui.resources.colors['gray_dark'],
                                   self.skillbook_ui.resources.colors['gray_mid'],
                                   self.skillbook_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=skb_image, same_surface=True)
        skb_panel = self.skillbook_ui.panel_add('skb_panel', (0, 0), (self.skb_w, self.skb_h), images=(skb_image,), page=None)

        # INVENTORY SOCKETS
        self.skb_sckt_img = pydraw.square((0, 0), (skb_sckt_size, skb_sckt_size),
                                          (self.skillbook_ui.resources.colors['gray_light'],
                                      self.skillbook_ui.resources.colors['gray_dark'],
                                      self.skillbook_ui.resources.colors['gray_mid'],
                                      self.skillbook_ui.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                          sq_image=None)
        for i in range(0, 24):
            s_x = skb_sckt_left + skb_sckt_size * (i % skb_sckt_per_row)
            s_y = skb_sckt_top + skb_sckt_size * (i // skb_sckt_per_row)
            skb_socket = self.skillbook_ui.panel_add(i, (s_x, s_y), (skb_sckt_size, skb_sckt_size),
                                                     images=(self.skb_sckt_img,), page=None, img_stretch=True,
                                                     tags=(self.pc.char_sheet.skills, 'skill'))
            self.skillbook_ui.interactives.append(skb_socket)
            self.skb_sockets_list.append(skb_socket)

        # window header
        header_texture = self.skillbook_ui.random_texture((self.skb_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.skb_w, 19),
                                   (self.skillbook_ui.resources.colors['gray_light'],
                                    self.skillbook_ui.resources.colors['gray_dark'],
                                    self.skillbook_ui.resources.colors['gray_mid'],
                                    self.skillbook_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.skillbook_ui.text_add('win_header', (0, 0), (self.skb_w, 19),
                                                caption='Skillbook',
                                                h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        self.skillbook_ui.interactives.append(win_header)
        self.skillbook_ui.decoratives.append(skb_panel)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer, fate_rnd):
        self.skillbook_ui.tick(pygame_settings, mouse_pointer)
        if self.skillbook_ui.updated:
            self.render()

    def render_slots(self, wins_dict, active_wins):
        for win in ('inventory','skillbook'):
            if wins_dict[win] in active_wins:
                wins_dict[win].render()

    def render(self, skb=True):
        # backpack update
        if self.pc is not None:
            if skb:
                for s_ind in range(0, len(self.skb_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.skills) or self.pc.char_sheet.skills[s_ind] is None:
                        self.skb_sockets_list[s_ind].images = (self.skb_sckt_img,)
                    elif (self.mouse_pointer.drag_item is not None and self.mouse_pointer.drag_item[
                        0] == self.pc.char_sheet.skills
                          and s_ind == self.mouse_pointer.drag_item[1]):
                        self.skb_sockets_list[s_ind].images = (self.skb_sckt_img,)
                    else:
                        self.skb_sockets_list[s_ind].images = self.pc.char_sheet.skills[s_ind].props[
                            'image_book']

        self.skillbook_ui.draw(self.rendered_skb)

    def draw(self, surface):
        surface.blit(self.rendered_skb, (self.offset_x, self.offset_y))

