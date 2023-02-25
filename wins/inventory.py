# char inventory window
import pygame
from library import textinput, pydraw, maths
from components import ui, skillfuncs, draganddrop, treasure


class Inventory:
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
        self.win_h = 510 + 192
        self.offset_x = 0
        self.offset_y = 64
        self.inv_sckt_total = 48
        self.inv_sockets_list = []
        self.eq_sockets_list = None
        self.inv_sockets_image = None

        self.gold_sum = None

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)

    def end(self):
        pass
        # self.pc.char_sheet.itemlist_cleanall_skills(self.wins_dict, self.pc)

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
            for j in (self.inv_sockets_list, self.eq_sockets_list):
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
                self.active_wins.remove(self.wins_dict['inventory'])
                self.active_wins.insert(0, self.wins_dict['inventory'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in (
                    self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'],
                    self.wins_dict['inventory'], self.wins_dict['skillbook'], self.wins_dict['tasks']
                ) if fw in self.active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])
        elif element.id == 'win_header' and m_bttn == 3 and mb_event == 'down':
            self.active_wins.remove(self)
            # self.pc.char_sheet.itemlist_cleanall_inventory(self.wins_dict, self.pc)
            # self.end()
            if in_realm:
                targ_win = self.wins_dict['pools']
                bttn_id = 'inv'
            else:
                targ_win = self.wins_dict['app_title']
                bttn_id = 'quick_inv'
            for el in targ_win.win_ui.interactives:
                if el.id == bttn_id:
                    el.sw_op = False
                    el.mouse_up(1)
            self.wins_dict['pools'].updated = in_realm

        if element.id == 'sell_panel' and m_bttn == 1 and mb_event == 'up' and self.mouse_pointer.drag_item is not None:
            item = self.mouse_pointer.drag_item[0][self.mouse_pointer.drag_item[1]]
            if 'quest_item' in item.props:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': "%s is not allowed to sell the item!" % self.pc.char_sheet.name,
                    'bttn_cancel': 'OK',
                }
                self.wins_dict['dialogue'].launch(self.pc)
            elif 'treasure_id' in item.props:
                price = treasure.calc_loot_stat(item.props, 'price_sell')
                price = price + price * self.pc.char_sheet.profs['prof_trade'] // 1000
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Trade confirmation',
                    'text': 'Sell %s for %s gp.? $n (You may get back recently sold items '
                            'in Buy Back tab of Trading Post window)' % (item.props['label'], price),
                    'bttn_cancel': 'CANCEL',
                    'bttn_ok': 'OK'
                }
                self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'item_sell', (self.mouse_pointer.drag_item[0],
                                                                                 self.mouse_pointer.drag_item[1], price))
                self.wins_dict['dialogue'].delayed_action['bttn_cancel'] = (self, 'item_to_cursor', (self.mouse_pointer.drag_item[0],
                                                                                            self.mouse_pointer.drag_item[1]))
                self.mouse_pointer.drag_item = None
                self.mouse_pointer.image = None
                self.wins_dict['dialogue'].launch(self.pc)
                self.wins_dict['realm'].pygame_settings.audio.sound('bag_drop')
            else:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': "It is impossible to sell %s's skills!" % self.pc.char_sheet.name,
                    'bttn_cancel': 'OK',
                }
                self.wins_dict['dialogue'].launch(self.pc)

        if element.id == 'bttn_sort' and m_bttn == 1 and mb_event == 'up':
            self.pc.char_sheet.inventory.sort(key=self.pc.char_sheet.sort_func)
            self.updated = True

        # PAGE 0
        if 'itm' not in element.tags:
            self.win_ui.interaction_callback(element, mb_event, m_bttn)
            # return True if interaction was made to prevent other windows from responding to this event
            return True
        """for cl in self.pc.hot_cooling_set:
            if cl[0] == element:
                self.win_ui.interaction_callback(element, mb_event, m_bttn)
                # return True if interaction was made to prevent other windows from responding to this event
                return True"""

        draganddrop.item_move(self, element, mb_event, m_bttn, in_realm, skillfuncs)

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.inv_sockets_list.clear()
        self.eq_sockets_list = None

        self.win_w = 320
        self.inv_sckt_total = len(self.pc.char_sheet.inventory)

        inv_sckt_size = 48
        inv_sckt_left = 16
        inv_sckt_top = 244
        inv_sckt_per_row = 6
        self.win_h = inv_sckt_top + inv_sckt_size * (self.inv_sckt_total // inv_sckt_per_row + ((self.inv_sckt_total % inv_sckt_per_row) != 0)) + 74

        # INVENTORY
        inv_texture = self.win_ui.random_texture((self.win_w // 2, self.win_h // 2), 'black_rock')
        inv_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=inv_texture, img_stretch=True)
        # INVENTORY BACKGROUND
        inv_image = pydraw.square((inv_sckt_left - 1, inv_sckt_top - 1),
                                  (inv_sckt_per_row * inv_sckt_size + 2,
                                   self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=inv_image, same_surface=True)
        inv_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(inv_image,),
                                          page=None)

        # INVENTORY SOCKETS
        self.inv_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                          (self.resources.colors['gray_light'],
                                           self.resources.colors['gray_dark'],
                                           self.resources.colors['gray_mid'],
                                           self.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=0, sq_ldir=2, sq_fill=False,
                                          sq_image=None)
        for i in range(0, self.inv_sckt_total):
            s_x = inv_sckt_left + inv_sckt_size * (i % inv_sckt_per_row)
            s_y = inv_sckt_top + inv_sckt_size * (i // inv_sckt_per_row)
            inv_socket = self.win_ui.panel_add(i, (s_x, s_y), (inv_sckt_size, inv_sckt_size),
                                               images=(self.inv_sckt_img,), page=None, img_stretch=True,
                                               tags=(self.pc.char_sheet.inventory, 'itm'), win=self)
            self.inv_sockets_list.append(inv_socket)

        eq_sckt_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                    (self.resources.colors['gray_light'],
                                     self.resources.colors['gray_dark'],
                                     self.resources.colors['gray_mid'],
                                     self.resources.colors['gray_darker']),
                                    sq_outsize=1, sq_bsize=2, sq_ldir=2, sq_fill=False,
                                    sq_image=None)
        # EQUIPPED ITEMS
        # panel ids must match char_sheet.equipped keys
        self.eq_sockets_list = (
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2, 48),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[0], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2, 108),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[1], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2 - 60, 108),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[2], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2 + 60, 108),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[3], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2 - 60, 168),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[4], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2 + 60, 168),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[5], 'itm'), win=self),
            self.win_ui.panel_add(0, (self.win_w // 2 - inv_sckt_size // 2 - 60, 48),
                                  (inv_sckt_size, inv_sckt_size), images=(eq_sckt_img,), page=None,
                                  img_stretch=True, tags=(self.pc.char_sheet.equipped[6], 'itm'), win=self),
        )

        inv_sell_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                          (self.resources.colors['gray_light'],
                                           self.resources.colors['gray_dark'],
                                           self.resources.colors['gray_mid'],
                                           self.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=2, sq_ldir=2, sq_fill=False, img_stretch=True,
                                          sq_image=self.tilesets.get_image('interface', (24, 24), (3,))[0])
        inv_sell_img = pydraw.square((0, 0), (inv_sckt_size, inv_sckt_size),
                                     (self.resources.colors['gray_light'],
                                      self.resources.colors['gray_dark'],
                                      self.resources.colors['gray_mid'],
                                      self.resources.colors['gray_darker']),
                                     sq_outsize=0, sq_bsize=1, sq_ldir=0, sq_fill=False, same_surface=True,
                                     sq_image=inv_sell_img)
        sell_panel = self.win_ui.panel_add('sell_panel',
                                           (inv_sckt_left + (inv_sckt_per_row - 1) * inv_sckt_size,
                                            inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 12),
                                           (48, 48), images=(inv_sell_img,), page=None, img_stretch=True)
        self.win_ui.interactives.append(sell_panel)

        bttn_sort = self.win_ui.button_add('bttn_sort', xy=(inv_sckt_left - 1, self.win_h - 24 - 16),
                                            caption='Sort', size=(48, 24), cap_font='def_bold', cap_size=24,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        self.win_ui.interactives.append(bttn_sort)

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
                                          caption='Inventory',
                                          h_align='center', v_align='middle', cap_color='sun',
                                          images=(header_img,))

        self.gold_sum = self.win_ui.text_add('inv_gold', (inv_sckt_left - 1 + 24,
                                                          inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 8),
                                             caption='* 600,000,000', cap_font='def_bold',
                                             h_align='left', v_align='bottom', size=(self.win_w // 2, 24),
                                             cap_color='bright_gold')

        coins_icon = self.win_ui.panel_add('coins_icon',
                                           (inv_sckt_left - 1,
                                                  inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                           (24, 24),
                                           images=(self.win_ui.tilesets.get_image(
                                                     *self.resources.sprites['gold_coins_icon'])),
                                           page=None, img_stretch=True)

        self.restore_cooling_sockets()

        self.win_ui.interactives.extend(self.inv_sockets_list)
        self.win_ui.interactives.extend(self.eq_sockets_list)
        self.win_ui.interactives.append(self.gold_sum)
        self.win_ui.interactives.append(win_header)
        self.win_ui.interactives.append(coins_icon)
        self.win_ui.interactives.append(inv_panel)

    def restore_cooling_sockets(self):
        for socket, skill in self.pc.hot_cooling_set:
            if socket.win is not self:
                continue
            for i in range(0, len(self.eq_sockets_list)):
                if socket.id == self.eq_sockets_list[i].id and socket.tags[0] == self.eq_sockets_list[i].tags[0]:
                    self.eq_sockets_list[i] = socket
                    break
            else:
                for i in range(0, len(self.inv_sockets_list)):
                    if socket.id == self.inv_sockets_list[i].id and socket.tags[0] == self.inv_sockets_list[i].tags[0]:
                        self.inv_sockets_list[i] = socket
                        break

    def item_sell(self, item_container, item_index, price):
        self.pc.moved_item_cooldown_check(item_container[item_index], None)
        self.wins_dict['trade'].trade_buyback.append(item_container[item_index])
        item_container[item_index].props['price_buy'] = item_container[item_index].props['price_sell']

        if price > 0:
            self.wins_dict['realm'].pygame_settings.audio.sound('coins_pickup')

        item_container[item_index] = None
        self.pc.char_sheet.gold_coins += price
        self.render_slots()

    def item_to_cursor(self, item_container, item_index):
        self.mouse_pointer.drag_item = [item_container, item_index]
        self.mouse_pointer.image = item_container[item_index].props['image_inventory'][0]

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render_slots(self):
        for win in ('inventory','skillbook', 'hotbar', 'trade', 'stash'):
            self.wins_dict[win].updated = True

    def render(self, inv=True, eq=True, gold=True):
        # backpack update
        if self.pc is not None:
            if gold:
                self.gold_sum.text_obj.caption = '%s gp.' % self.pc.char_sheet.gold_coins
                self.gold_sum.text_obj.render()
                self.gold_sum.render()
            if inv:
                for s_ind in range(0, len(self.inv_sockets_list)):
                    if s_ind >= len(self.pc.char_sheet.inventory) or self.pc.char_sheet.inventory[s_ind] is None:
                        self.inv_sockets_list[s_ind].images_update((self.inv_sckt_img,))
                    elif (self.mouse_pointer.drag_item is not None and self.mouse_pointer.drag_item[0] == self.pc.char_sheet.inventory
                        and s_ind == self.mouse_pointer.drag_item[1]):
                        self.inv_sockets_list[s_ind].images_update((self.inv_sckt_img,))
                    else:
                        self.inv_sockets_list[s_ind].images_update(self.pc.char_sheet.inventory[s_ind].props[
                            'image_inventory'])

                        if 'condition' in self.pc.char_sheet.inventory[s_ind].props:
                            cond = self.pc.char_sheet.inventory[s_ind].props['condition']
                            c_p_level = self.pc.char_sheet.inventory[s_ind].CONDITION_PENALTY_LEVEL
                            if cond <= c_p_level:
                                cond_y = cond * 150 // c_p_level
                                pygame.draw.rect(self.inv_sockets_list[s_ind].rendered_panel, (255,cond_y,0),
                                                 self.inv_sockets_list[s_ind].rendered_panel.get_rect(), width=1)
                        elif 'amount' in self.pc.char_sheet.inventory[s_ind].props:
                            self.pygame_settings.text_font.render_to(self.inv_sockets_list[s_ind].rendered_panel,
                                                     (5, 34), str(self.pc.char_sheet.inventory[s_ind].props['amount']),
                                                     fgcolor=self.resources.colors['fnt_celeb'])
                        elif 'charge' in self.pc.char_sheet.inventory[s_ind].props:
                            self.pygame_settings.text_font.render_to(self.inv_sockets_list[s_ind].rendered_panel,
                                                     (36, 5), str(self.pc.char_sheet.inventory[s_ind].props['charge']),
                                                     fgcolor=self.resources.colors['cyan'])
            if eq:
                for s_ind in range(0, len(self.eq_sockets_list)):
                    if len(self.pc.char_sheet.equipped[s_ind]) == 0 or self.pc.char_sheet.equipped[s_ind][0] is None:
                        self.eq_sockets_list[s_ind].images_update((self.inv_sckt_img,))
                    else:
                        self.eq_sockets_list[s_ind].images_update(self.pc.char_sheet.equipped[s_ind][0].props['image_inventory'])

                        if 'condition' in self.pc.char_sheet.equipped[s_ind][0].props:
                            cond = self.pc.char_sheet.equipped[s_ind][0].props['condition']
                            c_p_level = self.pc.char_sheet.equipped[s_ind][0].CONDITION_PENALTY_LEVEL
                            if cond <= c_p_level:
                                cond_y = cond * 150 // c_p_level
                                pygame.draw.rect(self.eq_sockets_list[s_ind].rendered_panel, (255, cond_y,0),
                                                 self.eq_sockets_list[s_ind].rendered_panel.get_rect(), width=1)
                        elif 'amount' in self.pc.char_sheet.equipped[s_ind][0].props:
                            self.pygame_settings.text_font.render_to(self.eq_sockets_list[s_ind].rendered_panel,
                                                     (5, 34), str(self.pc.char_sheet.equipped[s_ind][0].props['amount']),
                                                     fgcolor=self.resources.colors['fnt_celeb'])
                        elif 'charge' in self.pc.char_sheet.equipped[s_ind][0].props:
                            self.pygame_settings.text_font.render_to(self.eq_sockets_list[s_ind].rendered_panel,
                                                     (36, 5), str(self.pc.char_sheet.equipped[s_ind][0].props['charge']),
                                                     fgcolor=self.resources.colors['cyan'])

        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
