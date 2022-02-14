# char skillbook window
import pygame
from library import textinput, pydraw, maths, itemlist
from components import ui, skillfuncs


class SkillBook:
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
        self.win_w = 320
        self.win_h = 510
        self.offset_x = 8
        self.offset_y = 8
        self.skb_sckt_total = 36
        self.skb_sockets_list = []
        self.skb_sockets_image = None

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)

    def end(self):
        pass

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
                    if j[i].page is not None and self.win_ui.page not in j[i].page:
                        continue
                    if j[i].rendered_rect.collidepoint(
                            (mouse_x - self.offset_x, mouse_y - self.offset_y)):
                        if not j[i].mouse_over:
                            j[i].mouse_over = True
                            if not j[i].popup_active:
                                self.wins_dict['context'].context_info_update(self.pc, j[i])
                    else:
                        if j[i].mouse_over:
                            j[i].mouse_over = False
                            if j[i].popup_active:
                                j[i].popup_active = False
                                if self.wins_dict['context'] in self.active_wins:
                                    self.active_wins.remove(self.wins_dict['context'])
            return True

        # return True if interaction was made to prevent other windows from responding to this event
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click

        if self.wins_dict['realm'] in self.active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
            in_realm = True
        else:
            in_realm = False
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['skillbook'])
                self.active_wins.insert(0, self.wins_dict['skillbook'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in (self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'], self.wins_dict['inventory'], self.wins_dict['skillbook']) if fw in self.active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])

        # PAGE 0
        if 'skill' not in element.tags:
            self.win_ui.interaction_callback(element, mb_event, m_bttn)
            # return True if interaction was made to prevent other windows from responding to this event
            return True

        if m_bttn == 3 and in_realm:
            if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
                if 'skill_id' in element.tags[0][element.id].props:
                    getattr(skillfuncs, element.tags[0][element.id].props['function_name'])(
                        self.wins_dict, self.resources.fate_rnd, self.pc, element.tags[0][element.id],
                        (element.tags[0], element.id), True)
                elif 'treasure_id' in element.tags[0][element.id].props and element.tags[0][element.id].props[
                    'use_skill'] is not None:
                    getattr(skillfuncs, element.tags[0][element.id].props['use_skill'].props['function_name'])(
                        self.wins_dict, self.resources.fate_rnd, self.pc, element.tags[0][element.id].props['use_skill'],
                        (element.tags[0], element.id), True)
        elif m_bttn == 1:
            # removing popup if active
            if self.wins_dict['context'] in self.active_wins:
                self.active_wins.remove(self.wins_dict['context'])
            item_info = [element.tags[0], element.id]
            if mb_event == 'down' and self.mouse_pointer.drag_item is None:
                if item_info[1] < len(item_info[0]) and item_info[0][item_info[1]] is not None:
                    self.mouse_pointer.drag_item = item_info
                    # exchange between inventory socket and mouse

                    item_down = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                    self.mouse_pointer.image = item_down.props['image_inventory'][0]

            elif mb_event == 'up' and self.mouse_pointer.drag_item is not None:
                item_dragging = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
                if self.wins_dict['realm'].maze is not None and self.mouse_pointer.drag_item[0] == self.wins_dict['realm'].maze.loot:
                    self.mouse_pointer.catcher[0] = item_dragging
                    self.mouse_pointer.drag_item = [self.mouse_pointer.catcher, 0]
                    self.wins_dict['realm'].maze.loot.remove(item_dragging)

                if item_info[0][item_info[1]] is None:
                    item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                        self.mouse_pointer.drag_item[1]] = \
                        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                            item_info[1]]
                else:
                    item_info[0][item_info[1]], self.mouse_pointer.drag_item[0][
                        self.mouse_pointer.drag_item[1]] = \
                        self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]], item_info[0][
                            item_info[1]]

                self.pc.moved_item_cooldown_check(item_info[0][item_info[1]], element)

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
            self.render_slots()

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.skb_sockets_list.clear()

        skb_sckt_size = 48
        skb_sckt_left = 16
        skb_sckt_top = 160
        skb_sckt_per_row = 6
        # INVENTORY
        skb_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        skb_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                             self.resources.colors['gray_dark'],
                             self.resources.colors['gray_mid'],
                             self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=skb_texture)
        # INVENTORY BACKGROUND
        skb_image = pydraw.square((skb_sckt_left - 1, skb_sckt_top - 1),
                                  (skb_sckt_per_row * skb_sckt_size + 2,
                                   self.skb_sckt_total // skb_sckt_per_row * skb_sckt_size + 2),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=skb_image, same_surface=True)
        skb_panel = self.win_ui.panel_add('skb_panel', (0, 0), (self.win_w, self.win_h), images=(skb_image,), page=None)

        # SKILL SOCKETS
        self.skb_sckt_img = pydraw.square((0, 0), (skb_sckt_size, skb_sckt_size),
                                          (self.resources.colors['gray_light'],
                                      self.resources.colors['gray_dark'],
                                      self.resources.colors['gray_mid'],
                                      self.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                          sq_image=None)
        for i in range(0, self.skb_sckt_total):
            s_x = skb_sckt_left + skb_sckt_size * (i % skb_sckt_per_row)
            s_y = skb_sckt_top + skb_sckt_size * (i // skb_sckt_per_row)
            skb_socket = self.win_ui.panel_add(i, (s_x, s_y), (skb_sckt_size, skb_sckt_size),
                                               images=(self.skb_sckt_img,), page=None, img_stretch=True,
                                               tags=(self.pc.char_sheet.skills, 'skill'), win=self)
            self.skb_sockets_list.append(skb_socket)

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
                                          caption='Skillbook',
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        help_text_element = self.win_ui.text_add('help', (12, 64), (self.win_w - 24, 128),
                                                  caption='This is your Book of Skills. $n Drag the skills you want to use $n to the HOTBAR.',
                                                  h_align='center', v_align='middle', cap_color='gray_mid',
                                                  cap_font='def_normal', cap_size=24)
        self.win_ui.decoratives.append(help_text_element)

        self.restore_cooling_sockets()

        self.win_ui.interactives.extend(self.skb_sockets_list)
        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(skb_panel)

    def restore_cooling_sockets(self):
        for socket, skill in self.pc.hot_cooling_set:
            if socket is None or socket.win is not self:
                continue
            for i in range(0, len(self.skb_sockets_list)):
                if socket.id == self.skb_sockets_list[i].id and socket.tags[0] == self.skb_sockets_list[i].tags[0]:
                    self.skb_sockets_list[i] = socket
                    break

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render_slots(self):
        for win in ('inventory','skillbook', 'hotbar'):
            if self.wins_dict[win] in self.active_wins:
                self.wins_dict[win].render()

    def render(self, skb=True):
        # backpack update
        if self.pc is not None:
            if skb:
                for s_ind in range(0, len(self.skb_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.skills) or self.pc.char_sheet.skills[s_ind] is None:
                        self.skb_sockets_list[s_ind].images_update((self.skb_sckt_img,))

                    else:
                        self.skb_sockets_list[s_ind].images_update(self.pc.char_sheet.skills[s_ind].props[
                            'image_inventory'])

        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))

