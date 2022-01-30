# pool info window
import pygame
import math
import settings
from components import ui
from library import pydraw, maths


class Pools:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.tilesets = tilesets
        self.pygame_settings = pygame_settings
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.pools_rendered = None
        self.win_header = None
        self.win_w = 210
        self.win_h = 192
        self.offset_x = 0
        self.offset_y = pygame_settings.screen_res[1] - self.win_h
        self.pc = None

        self.pc_level = 0

        self.hp_pool_img = None
        self.mp_pool_img = None
        self.food_pool_img = None
        self.exp_pool_img = None

        self.pool_img_w = 64
        self.pool_img_h = 64
        self.pool_exp_w = 120
        self.pool_exp_h = 24

        self.pools_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        mouse_x, mouse_y = self.mouse_pointer.xy
        return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.win_ui.page:
            return
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                active_wins.remove(wins_dict['pools'])
                active_wins.insert(0, wins_dict['pools'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in
                               (wins_dict['charstats'], wins_dict['pools'], wins_dict['hotbar'], wins_dict['inventory'], wins_dict['skillbook'])
                               if fw in active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, pygame_settings.screen_res[0],
                                                                    pygame_settings.screen_res[1])

        # PAGE 0
        if 'hud' in element.tags and m_bttn == 1 and element.mode == 0 and mb_event == 'down':
            if element.id == 'inv':
                if not wins_dict['inventory'] in active_wins:
                    wins_dict['inventory'].launch(self.pc)
                    wins_dict['inventory'].render()
                    active_wins.insert(0, wins_dict['inventory'])
            elif element.id == 'skb':
                if not wins_dict['skillbook'] in active_wins:
                    wins_dict['skillbook'].launch(self.pc)
                    wins_dict['skillbook'].render()
                    active_wins.insert(0, wins_dict['skillbook'])
            elif element.id == 'hot':
                if not wins_dict['hotbar'] in active_wins:
                    wins_dict['hotbar'].render()
                    active_wins.insert(0, wins_dict['hotbar'])
            elif element.id == 'char':
                if not wins_dict['charstats'] in active_wins:
                    wins_dict['charstats'].launch(self.pc)
                    wins_dict['charstats'].render()
                    active_wins.insert(0, wins_dict['charstats'])

        elif 'hud' in element.tags and m_bttn == 1 and element.mode == 1 and element.sw_op is False and mb_event == 'up':
            if element.id == 'inv':
                if wins_dict['inventory'] in active_wins:
                    active_wins.remove(wins_dict['inventory'])
                    self.pc.char_sheet.itemlist_cleanall_inventory()
                    wins_dict['inventory'].end()
            elif element.id == 'skb':
                if wins_dict['skillbook'] in active_wins:
                    active_wins.remove(wins_dict['skillbook'])
                    self.pc.char_sheet.itemlist_cleanall_skills()
                    wins_dict['skillbook'].end()
            elif element.id == 'hot':
                if wins_dict['hotbar'] in active_wins:
                    active_wins.remove(wins_dict['hotbar'])
            elif element.id == 'char':
                if wins_dict['charstats'] in active_wins:
                    active_wins.remove(wins_dict['charstats'])
                    wins_dict['charstats'].end()

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        self.updated = True
        return True

    def create_elements(self):
        # POOLS
        pl_texture = self.tilesets.get_image('pools', (154, 192), (0,))[0]
        pl_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.win_ui.resources.colors['gray_light'],
                                  self.win_ui.resources.colors['gray_dark'],
                                  self.win_ui.resources.colors['gray_mid'],
                                  self.win_ui.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                 sq_image=pl_texture)
        # INVENTORY BACKGROUND
        """pl_image = pydraw.square((pl_sckt_left - 1, pl_sckt_top - 1),
                                  (pl_sckt_per_row * pl_sckt_size + 2,
                                   self.pl_sckt_total // pl_sckt_per_row * pl_sckt_size + 2),
                                  (self.win_ui.resources.colors['gray_light'],
                                   self.win_ui.resources.colors['gray_dark'],
                                   self.win_ui.resources.colors['gray_mid'],
                                   self.win_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=pl_image, same_surface=True)"""
        pl_panel = self.win_ui.panel_add('pl_panel', (0, 0), (self.win_w, self.win_h), images=(pl_image,),
                                         page=None)
        # window header
        header_texture = self.win_ui.random_texture((self.win_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w, 19),
                                   (self.win_ui.resources.colors['gray_light'],
                                    self.win_ui.resources.colors['gray_dark'],
                                    self.win_ui.resources.colors['gray_mid'],
                                    self.win_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        self.win_header = self.win_ui.text_add('win_header', (0, 0), (self.win_w, 19),
                                               caption='%s the %s, %s' % (self.pc.char_sheet.name.capitalize(),
                                                                               self.pc.char_sheet.type.capitalize(),
                                                                               self.pc.char_sheet.level),
                                               h_align='center', v_align='middle', cap_color='sun', cap_font='def_bold',
                                               images=(header_img,))

        self.hp_pool_img = pygame.transform.scale(self.tilesets.sets_dict['interface'].subsurface((96, 0, 32, 32)),
                                                  (self.pool_img_w, self.pool_img_h))
        self.mp_pool_img = pygame.transform.scale(self.tilesets.sets_dict['interface'].subsurface((128, 0, 32, 32)),
                                                  (self.pool_img_w, self.pool_img_h))
        self.food_pool_img = pygame.transform.scale(self.tilesets.sets_dict['interface'].subsurface((160, 0, 32, 32)),
                                                    (self.pool_img_w, self.pool_img_h))
        self.exp_pool_img = pygame.transform.scale(self.tilesets.sets_dict['interface'].subsurface((120, 36, 60, 12)),
                                                   (self.pool_exp_w, self.pool_exp_h))

        # HUD BUTTONS
        pools_btn_w = 54
        pools_btn_h = 34
        bttns_per_col = 5
        settings_btn_h = 35
        # MAIN MENU
        bttn_texture = self.win_ui.random_texture((pools_btn_w, pools_btn_h), 'red_glass')

        bttn_icons = (
            self.tilesets.get_image('interface', (24, 24,), (20, 21)),
            self.tilesets.get_image('interface', (24, 24,), (22, 23)),
            self.tilesets.get_image('interface', (24, 24,), (24, 25)),
            self.tilesets.get_image('interface', (24, 24,), (26, 27)),
            self.tilesets.get_image('interface', (24, 24,), (28, 29))
        )
        bttn_img_list = []
        for i in range(0, 5):
            bttn_up_img = pydraw.square((0, 0), (pools_btn_w, pools_btn_h),
                                        (self.win_ui.resources.colors['gray_light'],
                                         self.win_ui.resources.colors['gray_dark'],
                                         self.win_ui.resources.colors['gray_mid'],
                                         self.win_ui.resources.colors['gray_darker']),
                                        sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                        sq_image=bttn_texture)
            bttn_up_img.blit(bttn_icons[i][0], (round(pools_btn_w / 2 - 12), round(pools_btn_h / 2 - 12)))
            bttn_down_img = pydraw.square((0, 0), (pools_btn_w, pools_btn_h),
                                          (self.win_ui.resources.colors['gray_light'],
                                           self.win_ui.resources.colors['gray_dark'],
                                           self.win_ui.resources.colors['gray_mid'],
                                           self.win_ui.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                          sq_image=bttn_texture)
            bttn_down_img.blit(bttn_icons[i][1], (round(pools_btn_w / 2 - 12), round(pools_btn_h / 2 - 12)))

            bttn_img_list.append((
                bttn_up_img, bttn_down_img
            ))

        pools_menu = (
            self.win_ui.button_add('inv', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[0], switch=True),
            self.win_ui.button_add('skb', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[1], switch=True),
            self.win_ui.button_add('hot', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[2], switch=True),
            self.win_ui.button_add('char', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[3], switch=True),
            self.win_ui.button_add('opts', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[4], switch=True),
        )
        for i in range(0, len(pools_menu)):
            pools_menu[i].tags = ['hud']
            # pools_menu[i].page = 0
            pools_menu[i].rendered_rect.left = self.win_w - pools_btn_w - pools_btn_w * (i // bttns_per_col) - 3
            pools_menu[i].rendered_rect.top = 19 + (pools_btn_h * (i % bttns_per_col))

        self.win_ui.interactives.append(self.win_header)
        self.win_ui.interactives.extend(pools_menu)
        self.win_ui.interactives.append(pl_panel)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.win_ui.tick(pygame_settings, mouse_pointer)
        if self.updated:
            self.render()

    def render(self):
        if self.pc_level != self.pc.char_sheet.level:
            self.win_header.text_obj.caption = '%s the %s, %s' % (self.pc.char_sheet.name.capitalize(),
                                                                       self.pc.char_sheet.type.capitalize(),
                                                                       self.pc.char_sheet.level)
            self.win_header.render_all()
            self.pc_level = self.pc.char_sheet.level
        self.win_ui.draw(self.pools_rendered)
        hp_rate = max(0, self.pc.char_sheet.hp / self.pc.char_sheet.pools['HP'])
        mp_rate = max(0, self.pc.char_sheet.mp / self.pc.char_sheet.pools['MP'])
        food_rate = max(0, self.pc.char_sheet.food / self.pc.char_sheet.pools['FOOD'])
        exp_rate = max(0, (self.pc.char_sheet.experience - self.pc.char_sheet.exp_prev_lvl) / (
                    self.pc.char_sheet.exp_next_lvl - self.pc.char_sheet.exp_prev_lvl))
        self.pools_rendered.blit(self.hp_pool_img.subsurface(
            (0, self.pool_img_h - round(hp_rate * self.pool_img_h), self.pool_img_w, round(self.pool_img_h * hp_rate))),
                                 (44, 31 + self.pool_img_h - round(self.pool_img_h * hp_rate)))
        self.pools_rendered.blit(self.mp_pool_img.subsurface(
            (0, self.pool_img_h - round(mp_rate * self.pool_img_h), self.pool_img_w, round(self.pool_img_h * mp_rate))),
                                 (14, 79 + self.pool_img_h - round(self.pool_img_h * mp_rate)))
        self.pools_rendered.blit(self.food_pool_img.subsurface((0, self.pool_img_h - round(food_rate * self.pool_img_h),
                                                                self.pool_img_w, round(self.pool_img_h * food_rate))),
                                 (81, 83 + self.pool_img_h - round(self.pool_img_h * food_rate)))
        self.pools_rendered.blit(
            self.exp_pool_img.subsurface((0, 0, round(self.pool_exp_w * exp_rate), self.pool_exp_h)), (17, 152))
        self.updated = False

    def draw(self, surface):
        surface.blit(self.pools_rendered, (self.offset_x, self.offset_y))