# game title window
import pygame
import settings
from objects import ui
from library import pydraw, maths


class Context:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, log=True):
        self.db = db
        self.pygame_settings = pygame_settings
        self.mouse_pointer = mouse_pointer
        self.animations = animations
        self.context_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.context_rendered = None
        self.offset_x = 0
        self.offset_y = 0

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        mouse_x, mouse_y = self.mouse_pointer.xy
        return self.ui_click(self.context_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.context_ui.page:
            return
        # PAGE 0

        self.context_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def update_elements_weapon(self, item, mouse_xy, log=True):
        self.context_ui.decoratives.clear()
        self.context_ui.interactives.clear()

        win_width = 240
        itm_img_size = (48, 48)

        # color based on grade
        decor_color = self.context_ui.resources.grade_colors[item.props['grade']]
        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    self.context_ui.resources.grades[item.props['grade']] + ' ' + item.props['class']).capitalize(),
            'mainvalue': '87',
            'mv_caption': 'Damage'
        }
        itm_headlines = self.context_ui.context_headline_info(self.context_ui.resources, 'headlines',
                                                              (itm_img_size[0] + 16, 32),
                                                              (win_width - (itm_img_size[0] + 24), itm_img_size[1]),
                                                              images=None, text_dict=hl_text, cap_bgcolor='black',
                                                              page=None)
        body_text = {
            'modifiers': '5-12 Base attack',
            'desc': (item.props['desc'] + ' '),
            'sell_price': str('Sell price: %s' % item.props['price_sell']),
            'condition': str('Condition: %s' % item.props['condition_max'])
        }
        itm_bodylines = self.context_ui.context_body_info(self.context_ui.resources, 'body_text',
                                                          (8, 104),
                                                          (win_width - 16, itm_img_size[1]),
                                                          images=None, text_dict=body_text, cap_bgcolor='black',
                                                          page=None)
        itm_headlines.render_all()
        itm_bodylines.render_all()

        win_height = itm_bodylines.size[1] + 104 + 8
        self.context_rendered = pygame.Surface((win_width, win_height)).convert()
        self.context_rendered.set_colorkey(self.context_ui.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (win_width, win_height),
                                 (self.context_ui.resources.colors[decor_color],
                                  self.context_ui.resources.colors['gray_dark'],
                                  self.context_ui.resources.colors['black'],
                                  self.context_ui.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (win_width - 8, 24),
                                 (self.context_ui.resources.colors['gray_light'],
                                  self.context_ui.resources.colors['gray_dark'],
                                  self.context_ui.resources.colors['black'],
                                  self.context_ui.resources.colors[decor_color]),
                                 sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.context_ui.text_add('context_header', (4, 4), (win_width - 8, 24),
                                                caption=item.props['label'].upper(),
                                                h_align='center', v_align='middle', cap_color='fnt_celeb',
                                                cap_font='def_bold', images=(header_img,))

        bg_panel = self.context_ui.panel_add('inv_panel', (0, 0), (win_width, win_height), images=(bg_image,),
                                                   page=None)

        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.context_ui.resources.colors[decor_color],
                                   self.context_ui.resources.colors['gray_dark'],
                                   self.context_ui.resources.colors['black'],
                                   self.context_ui.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8,8))
        itm_icon_panel = self.context_ui.panel_add('inv_panel', (4, 32), (itm_img_w, itm_img_h), images=(item_icon,),
                                                page=None)

        self.context_ui.decoratives.append(context_header)
        self.context_ui.decoratives.append(itm_bodylines)
        self.context_ui.decoratives.append(itm_headlines)
        self.context_ui.decoratives.append(itm_icon_panel)
        self.context_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], win_width, win_height, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, win_width, win_height, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.render_ui(self.context_rendered)

    def tick(self, pygame_settings, mouse_pointer):
        self.context_ui.tick(pygame_settings, mouse_pointer)

    def render_ui(self, surface):
        for decorative in reversed(self.context_ui.decoratives):
            if decorative.page is not None and decorative.page != self.context_ui.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.context_ui.interactives):
            if interactive.page is not None and interactive.page != self.context_ui.page:
                continue
            interactive.draw(surface)

    def draw(self, surface):
        surface.blit(self.context_rendered, (self.offset_x, self.offset_y))
