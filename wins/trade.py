# trade window
import pygame
import math
from library import textinput, pydraw, maths, itemlist, calc2darray
from components import ui, treasure, dbrequests, chest


class Trade:
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
        self.text_font = pygame.freetype.Font(self.resources.fonts['def_bold'], 24)

        self.pc = None
        self.win_w = 512
        self.win_h = 510
        self.offset_x = 0
        self.offset_y = 0
        self.inv_sckt_total = 60
        self.inv_sockets_list = []
        self.inv_sockets_image = None

        self.trade_bank = []
        self.trade_list = []
        self.trade_buyback = []
        self.selected_index_list = {}
        self.filters_last = []
        self.cost_value = 0
        self.gold_sum = None
        self.delivery_cost = None
        self.total_cost = None
        self.dc_percents_per_floor = 5  # In percents of total goods cost

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)
        self.filter_list()
        self.render()
        self.active_wins.insert(0, self)

    def end(self):
        self.pc = None
        self.trade_list.clear()
        # self.trade_bank.clear()
        self.selected_index_list.clear()
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.inv_sockets_list.clear()
        self.active_wins.remove(self)

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
            for j in (self.inv_sockets_list,):
                for i in range(len(j) - 1, -1, -1):
                    if j[i].page is not None and self.win_ui.page not in j[i].page:
                        continue
                    if j[i].rendered_rect.collidepoint(
                            (mouse_x - self.offset_x, mouse_y - self.offset_y)):
                        if not j[i].mouse_over:
                            j[i].mouse_over = True
                            if not j[i].popup_active:
                                self.wins_dict['context'].context_info_update(self.pc, j[i], trade=True)
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
                self.active_wins.remove(self.wins_dict['trade'])
                self.active_wins.insert(0, self.wins_dict['trade'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in (
                self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'],
                self.wins_dict['inventory'], self.wins_dict['skillbook']) if fw in self.active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])

        if element.id == 'bttn_close' and m_bttn == 1 and mb_event == 'up':
            self.end()
        if element.id == 'bttn_order' and m_bttn == 1 and mb_event == 'up':
            if len(self.selected_index_list) == 0:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have not chosen any goods!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(self.pc)
            elif self.cost_value > self.pc.char_sheet.gold_coins:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have not enough gold!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(self.pc)
            else:
                self.win_ui.key_focus = None
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Trade confirmation',
                    'text': "You'll be charged %s gp. and the order will be shipped. $n Continue?" % self.cost_value,
                    'bttn_cancel': 'NO',
                    'bttn_ok': 'YES'
                }
                self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'order_set', ())
                self.wins_dict['dialogue'].launch(self.pc)

        # TAGGED RADIO BUTTON SWITCH GROUP
        if element.id == 'bttn_filter':
            if m_bttn == 1 and mb_event == 'down':
                for inter in self.win_ui.interactives:
                    if inter == element and element.mode == 0:
                        self.filter_list(element.tags)

                        if inter.text_obj.color != self.resources.colors['sun']:
                            inter.text_obj.color = self.resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()

                        self.updated = True
                    elif inter.id in ('bttn_filter', 'bttn_buyback'):
                        inter.mode = 0

                        if inter.text_obj.color != self.resources.colors['fnt_muted']:
                            inter.text_obj.color = self.resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()

                        inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True
        if element.id == 'bttn_buyback' and m_bttn == 1 and mb_event == 'down' and element.mode == 0:
            self.filter_list([])

            if element.text_obj.color != self.resources.colors['sun']:
                element.text_obj.color = self.resources.colors['sun']
                element.text_obj.render()
                element.render()
            self.updated = True
            for inter in self.win_ui.interactives:
                if inter.id == 'bttn_filter':
                    inter.mode = 0
                    if inter.text_obj.color != self.resources.colors['fnt_muted']:
                        inter.text_obj.color = self.resources.colors['fnt_muted']
                        inter.text_obj.render()
                        inter.render()
                    inter.render()
        elif element.id == 'bttn_buyback' and mb_event == 'up':
            return True

        # PAGE 0
        if 'itm' in element.tags and m_bttn == 1 and mb_event == 'down' and element.id < len(self.trade_list):
            key_obj = self.trade_list[element.id]
            """if key_obj in self.selected_index_list and key_obj not in self.trade_buyback:
                if self.selected_index_list[key_obj] < 99:
                    self.selected_index_list[key_obj] += 1
            else:
                self.selected_index_list[key_obj] = 1"""
            self.selected_index_list[key_obj] = 1
            self.updated = True
        if 'itm' in element.tags and m_bttn == 3 and mb_event == 'down' and element.id < len(self.trade_list):
            key_obj = self.trade_list[element.id]
            if key_obj in self.selected_index_list:
                if self.selected_index_list[key_obj] > 1:
                    self.selected_index_list[key_obj] -= 1
                else:
                    del self.selected_index_list[key_obj]
            self.updated = True

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def filter_list(self, item_types=None):
        self.trade_list.clear()
        if item_types is None:
            item_types = self.filters_last
        if len(item_types) == 0:
            self.trade_list.extend([itm for itm in self.trade_buyback[self.inv_sckt_total * -1:]])
        else:
            self.trade_list.extend([itm for itm in self.trade_bank if itm.props['item_type'] in item_types])
        self.filters_last = item_types

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.inv_sockets_list.clear()

        inv_sckt_size = 48
        inv_sckt_left = 16
        inv_sckt_top = 160
        inv_sckt_per_row = 10
        # INVENTORY
        inv_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        inv_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=inv_texture)
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
                                               images=(self.inv_sckt_img,), page=(0,), img_stretch=True,
                                               tags=(self.trade_list, 'itm'))
            self.inv_sockets_list.append(inv_socket)

        filter_menu = (
            self.win_ui.button_add(
                'bttn_filter', caption='All Items', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, mode=1, tags=(
                    'wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                    'orb_ammo', 'orb_source', 'use_wand', 'exp_tools', 'exp_lockpick', 'exp_food', 'light', 'aug_gem',
                    'sup_potion')
            ),
            self.win_ui.button_add(
                'bttn_filter', caption='Weapons', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'wpn_melee', 'wpn_ranged')),
            self.win_ui.button_add(
                'bttn_filter', caption='Armor', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'arm_head', 'arm_chest', 'acc_ring')),
            self.win_ui.button_add(
                'bttn_filter', caption='Magical', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'wpn_magic', 'orb_source', 'use_wand')),
            self.win_ui.button_add(
                'bttn_filter', caption='Potions', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'sup_potion',)),
            self.win_ui.button_add(
                'bttn_filter', caption='Tools', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'exp_tools', 'exp_lockpick')),
            self.win_ui.button_add(
                'bttn_filter', caption='Food', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'exp_food',)),
            self.win_ui.button_add(
                'bttn_filter', caption='Skills', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None, tags=(
                    'skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc')),

            self.win_ui.button_add(
                'bttn_buyback', caption='Buy Back', size=(80, 24), cap_font='def_bold', cap_size=24,
                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None),
        )
        fb_per_row = 6
        fb_width = 80
        fb_height = 24
        for i in range(0, len(filter_menu)):
            filter_menu[i].rendered_rect.topleft = (16 + fb_width * (i % fb_per_row),
                inv_sckt_top - fb_height * math.ceil(len(filter_menu) / fb_per_row) + fb_height * (i // fb_per_row))
        self.win_ui.interactives.extend(filter_menu)

        bttn_order = self.win_ui.button_add('bttn_order', xy=(self.win_w - 96 * 2 - 16 - 8, self.win_h - 32 - 16),
                                            caption='PURCHASE', size=(96, 32), cap_font='def_bold', cap_size=24,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        self.win_ui.interactives.append(bttn_order)
        bttn_close = self.win_ui.button_add('bttn_close', xy=(self.win_w - 96 - 16, self.win_h - 32 - 16),
                                            caption='CLOSE', size=(96, 32), cap_font='def_bold', cap_size=24,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        self.win_ui.interactives.append(bttn_close)

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
                                          caption='Trading Post',
                                          h_align='center', v_align='middle', cap_color='sun',
                                          images=(header_img,))

        self.gold_sum = self.win_ui.text_add('inv_gold', (inv_sckt_left - 1 + 24,
                                                          inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 8),
                                             caption='* 600,000,000', cap_font='def_bold',
                                             h_align='left', v_align='bottom', size=(self.win_w // 2, 24),
                                             cap_color='bright_gold')
        self.delivery_cost = self.win_ui.text_add('delivery_cost', (inv_sckt_left - 1,
                                                              inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 8 + 14),
                                               caption='* 600,000,000', cap_font='def_normal',
                                               h_align='left', v_align='bottom', size=(self.win_w // 2, 24),
                                               cap_color='fnt_celeb')
        self.total_cost = self.win_ui.text_add('total_cost', (inv_sckt_left - 1,
                                                              inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 8 + 28),
                                               caption='* 600,000,000', cap_font='def_bold',
                                               h_align='left', v_align='bottom', size=(self.win_w // 2, 24),
                                               cap_color='fnt_celeb')

        coins_icon = self.win_ui.panel_add('coins_icon',
                                           (inv_sckt_left - 1,
                                            inv_sckt_top + self.inv_sckt_total // inv_sckt_per_row * inv_sckt_size + 2),
                                           (24, 24),
                                           images=(self.win_ui.tilesets.get_image(
                                               *self.resources.sprites['gold_coins_icon'])),
                                           page=None, img_stretch=True)

        help_text_element = self.win_ui.text_add('help', (12, 28), (self.win_w - 24, 128),
                                                 caption='Welcome to the Trading Post! $n All goods you order will be delivered to the entrance of the current dungeon floor!',
                                                 h_align='center', v_align='middle', cap_color='fnt_celeb',
                                                 cap_font='def_normal', cap_size=24)
        self.win_ui.decoratives.append(help_text_element)

        self.win_ui.interactives.extend(self.inv_sockets_list)
        self.win_ui.decoratives.append(self.gold_sum)
        self.win_ui.decoratives.append(self.delivery_cost)
        self.win_ui.decoratives.append(self.total_cost)
        self.win_ui.interactives.append(win_header)
        self.win_ui.interactives.append(coins_icon)
        self.win_ui.decoratives.append(inv_panel)

        self.filters_last = filter_menu[0].tags

    def order_set(self):
        ordered_goods = []
        self.pc.char_sheet.gold_coins -= self.cost_value
        for itm in self.selected_index_list.keys():
            ordered_goods.append(itm)
            if itm in self.trade_bank:
                self.trade_bank.remove(itm)
            elif itm in self.trade_buyback:
                self.trade_buyback.remove(itm)

        self.selected_index_list.clear()
        self.filter_list()

        x_sq = self.pc.x_sq
        y_sq = self.pc.y_sq
        for ex in self.wins_dict['realm'].maze.exits:
            if ex.dest == 'up':
                x_sq, y_sq = ex.x_sq, ex.y_sq
        space_list = calc2darray.fill2d(self.wins_dict['realm'].maze.flag_array, {'mov': False, 'obj': 'True', 'floor': False},
                                        (x_sq, y_sq), (x_sq, y_sq), 2, 3, r_max=5)
        x_sq, y_sq = space_list[1]
        new_chest = chest.Chest(x_sq, y_sq, 0, None, self.wins_dict['realm'].maze.tile_set, off_x=-4, off_y=-4,
                                container=ordered_goods, disappear=True)
        self.wins_dict['realm'].maze.chests.append(new_chest)
        self.wins_dict['realm'].maze.flag_array[y_sq][x_sq].obj = new_chest
        self.wins_dict['realm'].maze.flag_array[y_sq][x_sq].mov = False
        # self.updated = True
        self.end()

    def goods_generate(self, goods_level_cap):
        self.trade_bank.clear()
        good_ids = dbrequests.treasure_get(self.db.cursor, goods_level_cap, 0, 1000, shop=1)
        for j in good_ids:
            for i in range(-2, 1):
                self.trade_bank.append(treasure.Treasure(j, max(1, goods_level_cap + i), self.db.cursor,
                                                         self.tilesets, self.resources, self.pygame_settings.audio,
                                                         self.resources.fate_rnd))

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render(self, inv=True, eq=True, gold=True, cost=True):
        # backpack update
        if self.pc is not None:
            if gold:
                self.gold_sum.text_obj.caption = '%s gp.' % self.pc.char_sheet.gold_coins
                self.gold_sum.text_obj.render()
                self.gold_sum.render()
            if cost:
                self.cost_value = 0
                for k, v in self.selected_index_list.items():
                    product_sum = k.props['price_buy'] * v
                    self.cost_value += product_sum

                delivery_fee = self.cost_value * (self.dc_percents_per_floor * (self.pc.location[1] + 1)) // 100
                self.delivery_cost.text_obj.caption = 'Delivery fee: %s gp.' % delivery_fee
                self.delivery_cost.render_all()

                self.cost_value += delivery_fee
                self.total_cost.text_obj.caption = 'Total cost: %s gp.' % (self.cost_value)
                if self.cost_value > self.pc.char_sheet.gold_coins:
                    self.total_cost.text_obj.color = self.resources.colors['fnt_attent']
                else:
                    self.total_cost.text_obj.color = self.resources.colors['fnt_celeb']
                self.total_cost.render_all()
            if inv:
                for s_ind in range(0, len(self.inv_sockets_list)):
                    if s_ind >= len(self.trade_list) or self.trade_list[s_ind] is None:
                        self.inv_sockets_list[s_ind].images_update((self.inv_sckt_img,))
                    else:
                        self.inv_sockets_list[s_ind].images_update(self.trade_list[s_ind].props['image_inventory'])

                        """self.text_font.render_to(self.inv_sockets_list[s_ind].rendered_panel,
                                                 (2, 36), str(self.trade_list[s_ind].props['price_buy']),
                                                 fgcolor=self.resources.colors['bright_gold'])"""
                        item_obj = self.trade_list[s_ind]
                        if item_obj in self.selected_index_list:
                            pygame.draw.rect(self.inv_sockets_list[s_ind].rendered_panel, self.resources.colors['sun'],
                                             self.inv_sockets_list[s_ind].rendered_panel.get_rect(), width=1)
                            self.text_font.render_to(self.inv_sockets_list[s_ind].rendered_panel,
                                                     (2, 2), str(self.selected_index_list[item_obj]),
                                                     fgcolor=self.resources.colors['sun'])

                        elif 'condition' in item_obj.props:
                            cond = item_obj.props['condition']
                            c_p_level = item_obj.CONDITION_PENALTY_LEVEL
                            if ('condition' in item_obj.props
                                    and item_obj.props['condition']
                                    <= item_obj.CONDITION_PENALTY_LEVEL):
                                cond_y = cond * 150 // c_p_level
                                pygame.draw.rect(self.inv_sockets_list[s_ind].rendered_panel, (255, cond_y, 0),
                                                 self.inv_sockets_list[s_ind].rendered_panel.get_rect(), width=1)

        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
