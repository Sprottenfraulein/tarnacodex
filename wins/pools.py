# pool info window
import pygame
import math
import settings
from components import ui
from library import pydraw, maths


class Pools:
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

        self.win_header = None
        self.pools_menu = None
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

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

        self.updated = False
        self.mouse_over = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements()
        self.updated = True

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        mouse_x, mouse_y = self.mouse_pointer.xy

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.wins_dict['pools'].toggle_all_wins(self.pc)
            if event.key == pygame.K_ESCAPE:
                self.wins_dict['options'].launch(self.pc)
                self.wins_dict['options'].render()

        if event.type == pygame.MOUSEMOTION:
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.win_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.win_h):
                if self.mouse_over:
                    self.mouse_over = False
                    self.updated = True
                return False
            else:
                if not self.mouse_over:
                    self.mouse_over = True
                    self.updated = True
                return True

        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click

        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['pools'])
                self.active_wins.insert(0, self.wins_dict['pools'])
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

        # PAGE 0
        if element.id == 'opts' and m_bttn == 1 and mb_event == 'up':
            if not self.wins_dict['options'] in self.active_wins:
                self.wins_dict['options'].launch(self.pc)
                self.wins_dict['options'].render()
        elif 'hud' in element.tags and m_bttn == 1 and element.mode == 0 and mb_event == 'down':
            if element.id == 'inv':
                if not self.wins_dict['inventory'] in self.active_wins:
                    self.wins_dict['inventory'].launch(self.pc)
                    self.wins_dict['inventory'].render()
                    self.active_wins.insert(0, self.wins_dict['inventory'])
            elif element.id == 'skb':
                if not self.wins_dict['skillbook'] in self.active_wins:
                    self.wins_dict['skillbook'].launch(self.pc)
                    self.wins_dict['skillbook'].render()
                    self.active_wins.insert(0, self.wins_dict['skillbook'])
            elif element.id == 'hot':
                if not self.wins_dict['hotbar'] in self.active_wins:
                    self.wins_dict['hotbar'].render()
                    self.active_wins.insert(0, self.wins_dict['hotbar'])
            elif element.id == 'miss':
                if not self.wins_dict['tasks'] in self.active_wins:
                    self.wins_dict['tasks'].launch(self.pc)
                    self.wins_dict['tasks'].render()
                    self.active_wins.insert(0, self.wins_dict['tasks'])
            elif element.id == 'char':
                if not self.wins_dict['charstats'] in self.active_wins:
                    self.wins_dict['charstats'].launch(self.pc)
                    self.wins_dict['charstats'].render()
                    self.active_wins.insert(0, self.wins_dict['charstats'])
            """elif element.id == 'opts':
                if not self.wins_dict['options'] in self.active_wins:
                    self.wins_dict['options'].launch(self.pc, self.wins_dict, self.active_wins)
                    self.wins_dict['options'].render()"""

        elif 'hud' in element.tags and m_bttn == 1 and element.mode == 1 and element.sw_op is False and mb_event == 'up':
            if element.id == 'inv':
                if self.wins_dict['inventory'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['inventory'])
                    # self.pc.char_sheet.itemlist_cleanall_inventory(self.wins_dict, self.pc)
                    self.wins_dict['inventory'].end()
            elif element.id == 'skb':
                if self.wins_dict['skillbook'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['skillbook'])
                    self.pc.char_sheet.itemlist_cleanall_skills(self.wins_dict, self.pc)
                    self.wins_dict['skillbook'].end()
            elif element.id == 'hot':
                if self.wins_dict['hotbar'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['hotbar'])
            elif element.id == 'miss':
                if self.wins_dict['tasks'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['tasks'])
                    self.wins_dict['tasks'].end()
            elif element.id == 'char':
                if self.wins_dict['charstats'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['charstats'])
                    self.wins_dict['charstats'].end()
            """elif element.id == 'opts':
                if self.wins_dict['options'] in self.active_wins:
                    self.wins_dict['options'].end()"""

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        self.updated = True
        return True

    def toggle_all_wins(self, pc):
        if (
                self.wins_dict['inventory'] in self.active_wins
                or self.wins_dict['skillbook'] in self.active_wins
                or self.wins_dict['charstats'] in self.active_wins
        ):
            self.close_all_wins(pc, hotbar=False)
        else:
            self.open_all_wins(pc)

    def open_all_wins(self, pc, inventory=True, skills=True, hotbar=True, charstats=True, options=True):
        if not self.wins_dict['inventory'] in self.active_wins and inventory:
            self.wins_dict['inventory'].launch(pc)
            self.wins_dict['inventory'].updated = True
            self.active_wins.insert(0, self.wins_dict['inventory'])
            self.pools_menu[0].mode = 1
            self.pools_menu[0].render()
        if not self.wins_dict['skillbook'] in self.active_wins and skills:
            self.wins_dict['skillbook'].launch(pc)
            self.wins_dict['skillbook'].updated = True
            self.active_wins.insert(0, self.wins_dict['skillbook'])
            self.pools_menu[1].mode = 1
            self.pools_menu[1].render()
        if not self.wins_dict['hotbar'] in self.active_wins and hotbar:
            self.wins_dict['hotbar'].updated = True
            self.active_wins.insert(0, self.wins_dict['hotbar'])
            self.pools_menu[2].mode = 1
            self.pools_menu[2].render()
        if not self.wins_dict['charstats'] in self.active_wins and charstats:
            self.wins_dict['charstats'].launch(pc)
            self.wins_dict['charstats'].updated = True
            self.active_wins.insert(0, self.wins_dict['charstats'])
            self.pools_menu[4].mode = 1
            self.pools_menu[4].render()

        self.pygame_settings.audio.sound(self.resources.sound_presets['button'][2])
        self.updated = True

    def close_all_wins(self, pc, inventory=True, skills=True, hotbar=True, charstats=True, options=True):
        if self.wins_dict['inventory'] in self.active_wins and inventory:
            self.active_wins.remove(self.wins_dict['inventory'])
            # self.pc.char_sheet.itemlist_cleanall_inventory(self.wins_dict, pc)
            self.wins_dict['inventory'].end()
            self.pools_menu[0].mode = 0
            self.pools_menu[0].render()

        if self.wins_dict['skillbook'] in self.active_wins and skills:
            self.active_wins.remove(self.wins_dict['skillbook'])
            self.pc.char_sheet.itemlist_cleanall_skills(self.wins_dict, pc)
            self.wins_dict['skillbook'].end()
            self.pools_menu[1].mode = 0
            self.pools_menu[1].render()

        if self.wins_dict['hotbar'] in self.active_wins and hotbar:
            self.active_wins.remove(self.wins_dict['hotbar'])
            self.pools_menu[2].mode = 0
            self.pools_menu[2].render()

        if self.wins_dict['tasks'] in self.active_wins and charstats:
            self.active_wins.remove(self.wins_dict['tasks'])
            self.wins_dict['tasks'].end()
            self.pools_menu[3].mode = 0
            self.pools_menu[3].render()

        if self.wins_dict['charstats'] in self.active_wins and charstats:
            self.active_wins.remove(self.wins_dict['charstats'])
            self.wins_dict['charstats'].end()
            self.pools_menu[4].mode = 0
            self.pools_menu[4].render()

        if self.wins_dict['options'] in self.active_wins and options:
            self.wins_dict['options'].end()
            self.pools_menu[5].mode = 0
            self.pools_menu[5].render()

        self.pygame_settings.audio.sound(self.resources.sound_presets['button'][3])
        self.updated = True

    def create_elements(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        # POOLS
        pl_texture = self.tilesets.get_image('pools', (154, 192), (0,))[0]
        pl_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['gray_mid'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                 sq_image=pl_texture)
        pl_panel = self.win_ui.panel_add('pl_panel', (0, 0), (self.win_w, self.win_h), images=(pl_image,),
                                         page=None)
        # window header
        header_texture = self.win_ui.random_texture((self.win_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w, 19),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        self.win_header = self.win_ui.text_add('win_header', (0, 0), (self.win_w, 19),
                                               caption='%s (%s lvl)' % (self.pc.char_sheet.name.capitalize(),
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
        pools_btn_h = 28
        bttns_per_col = 6
        settings_btn_h = 35
        # MAIN MENU
        bttn_texture = self.win_ui.random_texture((pools_btn_w, pools_btn_h), 'red_glass')

        bttn_icons = (
            self.tilesets.get_image('interface', (24, 24,), (20, 21)),
            self.tilesets.get_image('interface', (24, 24,), (22, 23)),
            self.tilesets.get_image('interface', (24, 24,), (24, 25)),
            self.tilesets.get_image('interface', (24, 24,), (30, 31)),
            self.tilesets.get_image('interface', (24, 24,), (26, 27)),
            self.tilesets.get_image('interface', (24, 24,), (28, 29))
        )
        bttn_img_list = []
        for i in range(0, 6):
            bttn_up_img = pydraw.square((0, 0), (pools_btn_w, pools_btn_h),
                                        (self.resources.colors['gray_light'],
                                         self.resources.colors['gray_dark'],
                                         self.resources.colors['gray_mid'],
                                         self.resources.colors['gray_darker']),
                                        sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                        sq_image=bttn_texture)
            bttn_up_img.blit(bttn_icons[i][0], (round(pools_btn_w / 2 - 12), round(pools_btn_h / 2 - 12)))
            bttn_down_img = pydraw.square((0, 0), (pools_btn_w, pools_btn_h),
                                          (self.resources.colors['gray_light'],
                                           self.resources.colors['gray_dark'],
                                           self.resources.colors['gray_mid'],
                                           self.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                          sq_image=bttn_texture)
            bttn_down_img.blit(bttn_icons[i][1], (round(pools_btn_w / 2 - 12), round(pools_btn_h / 2 - 12)))

            bttn_img_list.append((
                bttn_up_img, bttn_down_img
            ))

        self.pools_menu = (
            self.win_ui.button_add('inv', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[0], switch=True),
            self.win_ui.button_add('skb', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[1], switch=True),
            self.win_ui.button_add('hot', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[2], switch=True, mode=1),
            self.win_ui.button_add('miss', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[3], switch=True),
            self.win_ui.button_add('char', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[4], switch=True),
            self.win_ui.button_add('opts', size=(pools_btn_w, pools_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[5]),
        )
        for i in range(0, len(self.pools_menu)):
            self.pools_menu[i].tags = ['hud']

            self.pools_menu[i].rendered_rect.left = self.win_w - pools_btn_w - pools_btn_w * (i // bttns_per_col) - 3
            self.pools_menu[i].rendered_rect.top = 19 + (pools_btn_h * (i % bttns_per_col))

        self.win_ui.interactives.append(self.win_header)
        self.win_ui.interactives.extend(self.pools_menu)
        self.win_ui.interactives.append(pl_panel)

    def tick(self):
        self.win_ui.tick()
        if self.updated:
            self.render()

    def render(self):
        if self.pc_level != self.pc.char_sheet.level:
            self.win_header.text_obj.caption = '%s (lv.%s)' % (self.pc.char_sheet.name.capitalize(),
                                                                       self.pc.char_sheet.level)
            self.win_header.render_all()
            self.pc_level = self.pc.char_sheet.level
        self.win_ui.draw(self.win_rendered)
        hp_rate = max(0, self.pc.char_sheet.hp / self.pc.char_sheet.pools['HP'])
        mp_rate = max(0, self.pc.char_sheet.mp / self.pc.char_sheet.pools['MP'])
        food_rate = max(0, self.pc.char_sheet.food / self.pc.char_sheet.pools['FOOD'])
        exp_rate = max(0, (self.pc.char_sheet.experience - self.pc.char_sheet.exp_prev_lvl) / (
                    self.pc.char_sheet.exp_next_lvl - self.pc.char_sheet.exp_prev_lvl))
        self.win_rendered.blit(self.hp_pool_img.subsurface(
            (0, self.pool_img_h - round(hp_rate * self.pool_img_h), self.pool_img_w, round(self.pool_img_h * hp_rate))),
                                 (44, 31 + self.pool_img_h - round(self.pool_img_h * hp_rate)))
        self.win_rendered.blit(self.mp_pool_img.subsurface(
            (0, self.pool_img_h - round(mp_rate * self.pool_img_h), self.pool_img_w, round(self.pool_img_h * mp_rate))),
                                 (14, 79 + self.pool_img_h - round(self.pool_img_h * mp_rate)))
        self.win_rendered.blit(self.food_pool_img.subsurface((0, self.pool_img_h - round(food_rate * self.pool_img_h),
                                                              self.pool_img_w, round(self.pool_img_h * food_rate))),
                               (81, 83 + self.pool_img_h - round(self.pool_img_h * food_rate)))
        self.win_rendered.blit(
            self.exp_pool_img.subsurface((0, 0, round(self.pool_exp_w * exp_rate), self.pool_exp_h)), (17, 152))

        if self.mouse_over:
            hp_caption = '%s/%s' % (self.pc.char_sheet.hp, self.pc.char_sheet.pools['HP'])
            hp_cap_rect = self.pygame_settings.text_font.get_rect(hp_caption)
            self.pygame_settings.text_font.render_to(self.win_rendered, (
                44 + self.pool_img_w // 2 - hp_cap_rect.width // 2,
                31 + self.pool_img_h // 2 - hp_cap_rect.height // 2
            ), hp_caption, fgcolor=self.resources.colors['fnt_celeb'])

            mp_caption = '%s/%s' % (self.pc.char_sheet.mp, self.pc.char_sheet.pools['MP'])
            mp_cap_rect = self.pygame_settings.text_font.get_rect(mp_caption)
            self.pygame_settings.text_font.render_to(self.win_rendered, (
                12 + self.pool_img_w // 2 - mp_cap_rect.width // 2,
                82 + self.pool_img_h // 2 - mp_cap_rect.height // 2
            ), mp_caption, fgcolor=self.resources.colors['fnt_celeb'])

            food_caption = '%s/%s' % (self.pc.char_sheet.food // 10, self.pc.char_sheet.pools['FOOD'] // 10)
            food_cap_rect = self.pygame_settings.text_font.get_rect(food_caption)
            self.pygame_settings.text_font.render_to(self.win_rendered, (
                81 + self.pool_img_w // 2 - food_cap_rect.width // 2,
                82 + self.pool_img_h // 2 - food_cap_rect.height // 2
            ), food_caption, fgcolor=self.resources.colors['fnt_celeb'])

        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
