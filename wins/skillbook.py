# char skillbook window
import pygame
from library import textinput, pydraw, maths, itemlist
from components import ui


class SkillBook:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.pc = None
        self.win_w = 320
        self.win_h = 510
        self.offset_x = 8
        self.offset_y = 8
        self.skb_sckt_total = 36
        self.skb_sockets_list = []
        self.skb_sockets_image = None

        self.rendered_skb = pygame.Surface((self.win_w, self.win_h)).convert()

        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.skb_sockets_list.clear()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.win_ui.key_focus is not None:
                if self.win_ui.key_focus.page is not None and self.win_ui.key_focus.page != self.win_ui.page:
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

                self.win_ui.key_focus.text_obj.actual_width, self.win_ui.key_focus.text_obj.max_height = self.win_ui.key_focus.text_obj.get_text_height()
                self.win_ui.key_focus.text_obj.render()
                self.win_ui.key_focus.render()
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.win_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.win_h):
                return False
            for j in (self.skb_sockets_list, ):
                for i in range(len(j) - 1, -1, -1):
                    if j[i].page is not None and j[i].page != self.win_ui.page:
                        continue
                    if j[i].rendered_rect.collidepoint(
                            (mouse_x - self.offset_x, mouse_y - self.offset_y)):
                        if not j[i].mouse_over:
                            j[i].mouse_over = True
                            if not j[i].popup_active:
                                wins_dict['context'].context_info_update(self.pc, j[i], wins_dict, active_wins)
                    else:
                        if j[i].mouse_over:
                            j[i].mouse_over = False
                            if j[i].popup_active:
                                j[i].popup_active = False
                                if wins_dict['context'] in active_wins:
                                    active_wins.remove(wins_dict['context'])
            return True

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.win_ui.page:
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
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, pygame_settings.screen_res[0],
                                                                    pygame_settings.screen_res[1])
                framed_wins = [fw for fw in (wins_dict['charstats'], wins_dict['pools'], wins_dict['hotbar'], wins_dict['inventory'], wins_dict['skillbook']) if fw in active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])

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
                    self.mouse_pointer.image = item_down.props['image_inventory'][0]

            elif mb_event == 'up' and self.mouse_pointer.drag_item is not None:
                item_dragging = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                if self.mouse_pointer.drag_item[0] == wins_dict['realm'].maze.loot:
                    self.mouse_pointer.catcher[0] = item_dragging
                    self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                    wins_dict['realm'].maze.loot.remove(item_dragging)
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
                        or (self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]] is not None
                            and self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]].props['item_type']
                            not in self.mouse_pointer.drag_item[0].filters['item_types'])):
                    item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                        self.mouse_pointer.drag_item[1]] = \
                        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                            item_info[1]]

                if self.mouse_pointer.catcher[0] is not None:
                    self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                    self.mouse_pointer.image = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]].props['image_inventory'][0]
                else:
                    self.mouse_pointer.drag_item = None
                    self.mouse_pointer.image = None

                self.pc.char_sheet.itemlists_clean_tail()
            self.render_slots(wins_dict, active_wins)

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        skb_sckt_size = 48
        skb_sckt_left = 16
        skb_sckt_top = 160
        skb_sckt_per_row = 6
        # INVENTORY
        skb_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        skb_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.win_ui.resources.colors['gray_light'],
                             self.win_ui.resources.colors['gray_dark'],
                             self.win_ui.resources.colors['gray_mid'],
                             self.win_ui.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=skb_texture)
        # INVENTORY BACKGROUND
        skb_image = pydraw.square((skb_sckt_left - 1, skb_sckt_top - 1),
                                  (skb_sckt_per_row * skb_sckt_size + 2,
                                   self.skb_sckt_total // skb_sckt_per_row * skb_sckt_size + 2),
                                  (self.win_ui.resources.colors['gray_light'],
                                   self.win_ui.resources.colors['gray_dark'],
                                   self.win_ui.resources.colors['gray_mid'],
                                   self.win_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=skb_image, same_surface=True)
        skb_panel = self.win_ui.panel_add('skb_panel', (0, 0), (self.win_w, self.win_h), images=(skb_image,), page=None)

        # SKILL SOCKETS
        self.skb_sckt_img = pydraw.square((0, 0), (skb_sckt_size, skb_sckt_size),
                                          (self.win_ui.resources.colors['gray_light'],
                                      self.win_ui.resources.colors['gray_dark'],
                                      self.win_ui.resources.colors['gray_mid'],
                                      self.win_ui.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                          sq_image=None)
        for i in range(0, self.skb_sckt_total):
            s_x = skb_sckt_left + skb_sckt_size * (i % skb_sckt_per_row)
            s_y = skb_sckt_top + skb_sckt_size * (i // skb_sckt_per_row)
            skb_socket = self.win_ui.panel_add(i, (s_x, s_y), (skb_sckt_size, skb_sckt_size),
                                               images=(self.skb_sckt_img,), page=None, img_stretch=True,
                                               tags=(self.pc.char_sheet.skills, 'skill'))
            self.win_ui.interactives.append(skb_socket)
            self.skb_sockets_list.append(skb_socket)

        # window header
        header_texture = self.win_ui.random_texture((self.win_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w, 19),
                                   (self.win_ui.resources.colors['gray_light'],
                                    self.win_ui.resources.colors['gray_dark'],
                                    self.win_ui.resources.colors['gray_mid'],
                                    self.win_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.win_ui.text_add('win_header', (0, 0), (self.win_w, 19),
                                          caption='Skillbook',
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        help_text_element = self.win_ui.text_add('help', (12, 32), (self.win_w - 24, 128),
                                                  caption='This is your Book of Skills. $n Drag the skills you want to use $n to the HOTBAR.',
                                                  h_align='center', v_align='middle', cap_color='gray_mid',
                                                  cap_font='def_normal', cap_size=24)
        self.win_ui.decoratives.append(help_text_element)

        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(skb_panel)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.win_ui.tick(pygame_settings, mouse_pointer)
        if self.win_ui.updated or self.updated:
            self.render()

    def render_slots(self, wins_dict, active_wins):
        for win in ('inventory','skillbook', 'hotbar'):
            if wins_dict[win] in active_wins:
                wins_dict[win].render()

    def render(self, skb=True):
        # backpack update
        if self.pc is not None:
            if skb:
                for s_ind in range(0, len(self.skb_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.skills) or self.pc.char_sheet.skills[s_ind] is None:
                        self.skb_sockets_list[s_ind].images = (self.skb_sckt_img,)

                    else:
                        self.skb_sockets_list[s_ind].images = self.pc.char_sheet.skills[s_ind].props[
                            'image_inventory']
                    """elif (self.mouse_pointer.drag_item is not None and self.mouse_pointer.drag_item[
                                            0] == self.pc.char_sheet.skills
                                              and s_ind == self.mouse_pointer.drag_item[1]):
                                            self.skb_sockets_list[s_ind].images = (self.skb_sckt_img,)"""

        self.win_ui.draw(self.rendered_skb)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.rendered_skb, (self.offset_x, self.offset_y))

