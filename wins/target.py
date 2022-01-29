# mob targeting window
import pygame
import settings
from components import ui, treasure
from library import pydraw, maths


class Target:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.pygame_settings = pygame_settings
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.target_rendered = None
        self.win_w = 320
        self.win_h = 64
        self.bar_color = resources.colors['bloody']
        self.offset_x = pygame_settings.screen_res[0] // 2 - self.win_w // 2
        self.offset_y = 0

        self.mob_title = None
        self.mon_hp = None
        self.mob_object = None

        self.target_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
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
        # PAGE 0

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def aim(self, monster, realm):
        self.offset_x = min(round((realm.view_offset_x_sq * -1 - 0.5) * realm.square_size * realm.square_scale - self.win_w // 2),
                            realm.view_size_scaled[0] - self.win_w)
        if self.mob_object is not None:
            self.mob_object.aimed = False
        self.mob_object = monster
        self.mob_object.aimed = True
        self.mob_title.text_obj.caption = monster.stats['label'].capitalize()
        self.mob_title.render_all()

        self.mon_hp = monster.hp
        self.render_ui(self.target_rendered)
        self.progress_bar_update(monster.stats['hp_max'], self.mon_hp, self.bar_color)

    def drop_aim(self):
        if self.mob_object is not None:
            self.mob_object.aimed = False
            self.mob_object = None

    def progress_bar_update(self, maximum, current, fg_color):
        full_w = self.win_w - 10 - 6
        self.target_rendered.fill(fg_color, (6, 34, full_w * current // maximum, 4))

    def create_elements(self):
        # INVENTORY
        tar_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        tar_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.win_ui.resources.colors['gray_light'],
                                   self.win_ui.resources.colors['gray_dark'],
                                   self.win_ui.resources.colors['gray_mid'],
                                   self.win_ui.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=tar_texture)
        tar_image = pydraw.square((4, 32),
                                  (self.win_w - 8, 8),
                                  (self.win_ui.resources.colors['gray_light'],
                                   self.win_ui.resources.colors['gray_dark'],
                                   self.win_ui.resources.colors['bg'],
                                   self.win_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=True,
                                  sq_image=tar_image, same_surface=True)

        tar_panel = self.win_ui.panel_add('tar_panel', (0, 0), (self.win_w, self.win_h), images=(tar_image,),
                                          page=None)
        """header_texture = self.win_ui.random_texture((19, self.win_h), 'red_glass')
        header_img = pydraw.square((0, 0), (19, self.win_h),
                                   (self.win_ui.resources.colors['gray_light'],
                                    self.win_ui.resources.colors['gray_dark'],
                                    self.win_ui.resources.colors['gray_mid'],
                                    self.win_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        tar_header = self.win_ui.panel_add('tar_header', (0, 0), (self.win_w, self.win_h), images=(header_img,),
                                             page=None)"""
        self.mob_title = self.win_ui.text_add('mob_title', (4, 8), (self.win_w - 8, 24),
                                              caption='mob_title', cap_font='def_bold',
                                              h_align='center', v_align='top', cap_color='sun',
                                              images=None)

        # self.win_ui.decoratives.append(tar_header)
        self.win_ui.decoratives.append(self.mob_title)
        self.win_ui.decoratives.append(tar_panel)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        if self.mob_object is not None:
            if self.mon_hp != self.mob_object.hp:
                self.mon_hp = self.mob_object.hp
                self.render_ui(self.target_rendered)
                self.progress_bar_update(self.mob_object.stats['hp_max'], self.mon_hp, self.bar_color)

        self.win_ui.tick(pygame_settings, mouse_pointer)

    def render_ui(self, surface):
        for decorative in reversed(self.win_ui.decoratives):
            if decorative.page is not None and decorative.page != self.win_ui.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.win_ui.interactives):
            if interactive.page is not None and interactive.page != self.win_ui.page:
                continue
            interactive.draw(surface)

    def draw(self, surface):
        surface.blit(self.target_rendered, (self.offset_x, self.offset_y))
