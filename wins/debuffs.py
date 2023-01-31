# player debuffs panel
import pygame
import settings
from components import ui, treasure, debufficons
from library import pydraw, maths


class Debuffs:
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
        self.win_w = 26 + 19
        self.win_h = 28
        self.icons_per_row = 10
        self.offset_x = 0
        self.offset_y = 0
        self.pc = None

        self.de_buff_panels = None

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        mouse_x, mouse_y = self.mouse_pointer.xy

        if event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.win_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.win_h):
                return False
            for j in (self.de_buff_panels,):
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
                self.active_wins.remove(self.wins_dict['debuffs'])
                self.active_wins.insert(0, self.wins_dict['debuffs'])
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

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    def update(self, pc):
        if self.create_elements(pc):
            if self not in self.active_wins:
                self.active_wins.insert(0, self)
        elif self in self.active_wins:
            self.active_wins.remove(self)

    def create_elements(self, pc):
        self.win_ui.interactives.clear()
        self.win_ui.decoratives.clear()
        self.pc = pc
        icon_w, icon_h = 32, 32
        total_de_buffs_list = list(pc.char_sheet.de_buffs.values())
        for eq_slot in pc.char_sheet.equipped:
            for eq_itm in eq_slot:
                if eq_itm is None:
                    continue
                if 'de_buffs' in eq_itm.props:
                    total_de_buffs_list += eq_itm.props['de_buffs']
                if 'affixes' in eq_itm.props:
                    for aff in eq_itm.props['affixes']:
                        if 'de_buffs' in aff:
                            total_de_buffs_list += aff['de_buffs']
        self.de_buff_panels = debufficons.create(total_de_buffs_list, self, (19, 2),
                                                 (icon_w, icon_h), self.icons_per_row)
        if not self.de_buff_panels:
            return False
        self.win_w = 19 + min(10, len(self.de_buff_panels)) * icon_w + 2
        self.win_h = (len(self.de_buff_panels) // self.icons_per_row + 1) * icon_h + 4

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        # self.win_rendered.set_colorkey(self.resources.colors['transparent'])

        buff_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        buff_image = pydraw.square(
            (0, 0), (self.win_w, self.win_h), (
                self.resources.colors['gray_light'],
                self.resources.colors['gray_dark'],
                self.resources.colors['gray_mid'],
                self.resources.colors['black']
            ), sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False, sq_image=buff_texture
        )
        buff_panel = self.win_ui.panel_add(
            'buff_panel', (0, 0), (self.win_w, self.win_h), images=(buff_image,), page=None, img_stretch=True
        )

        # window header
        header_texture = self.win_ui.random_texture((19, self.win_h), 'red_glass')
        header_img = pydraw.square((0, 0), (19, self.win_h),
                                   (self.win_ui.resources.colors['gray_light'],
                                    self.win_ui.resources.colors['gray_dark'],
                                    self.win_ui.resources.colors['gray_mid'],
                                    self.win_ui.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.win_ui.panel_add('win_header', (0, 0), (19, self.win_h), images=(header_img,), page=None)

        self.win_ui.interactives.extend(self.de_buff_panels)
        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(buff_panel)

        self.win_ui.draw(self.win_rendered)
        return True

    def tick(self):
        self.win_ui.tick()

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
