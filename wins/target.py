# mob targeting window
import pygame
import settings
from components import ui, treasure
from library import pydraw, maths


class Target:
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

        self.win_rendered = None
        self.win_w = 320
        self.win_h = 64
        self.bar_color = resources.colors['bloody']
        self.bar_top = 36
        self.offset_x = pygame_settings.screen_res[0] // 2 - self.win_w // 2
        self.offset_y = 0

        self.mob_title = None
        self.mon_hp = None
        self.mob_object = None

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.create_elements()

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        mouse_x, mouse_y = self.mouse_pointer.xy
        return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
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
        self.mob_title.text_obj.caption = '%s, (%s)' % (monster.stats['label'].capitalize(), monster.stats['lvl'])
        self.mob_title.render_all()

        self.mon_hp = monster.hp
        self.win_ui.draw(self.win_rendered)
        self.progress_bar_update(monster.stats['hp_max'], self.mon_hp, self.bar_color)

    def drop_aim(self):
        if self.mob_object is not None:
            self.mob_object.aimed = False
            self.mob_object = None

    def progress_bar_update(self, maximum, current, fg_color):
        full_w = self.win_w - 32
        self.win_rendered.blit(self.tilesets.get_image('red_glass', (max(1, full_w * current // maximum), 12), (0,))[0], (16,self.bar_top))

    def create_elements(self):
        # INVENTORY
        tar_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        tar_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=tar_texture)
        tar_image = pydraw.square((14, self.bar_top - 2),
                                  (self.win_w - 28, 16),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['bg'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=True,
                                  sq_image=tar_image, same_surface=True)

        tar_panel = self.win_ui.panel_add('tar_panel', (0, 0), (self.win_w, self.win_h), images=(tar_image,),
                                          page=None)
        """header_texture = self.win_ui.random_texture((19, self.win_h), 'red_glass')
        header_img = pydraw.square((0, 0), (19, self.win_h),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['gray_darker']),
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

    def tick(self):
        if self.mob_object is not None:
            if self.mon_hp != self.mob_object.hp:
                self.mon_hp = self.mob_object.hp
                self.win_ui.draw(self.win_rendered)
                self.progress_bar_update(self.mob_object.stats['hp_max'], self.mon_hp, self.bar_color)

        self.win_ui.tick()

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
