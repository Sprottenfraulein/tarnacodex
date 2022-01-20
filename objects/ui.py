# user interface object
import pygame
import random
from library import pydraw, typography, button, fieldedit, fieldtext, fieldrich, panel


class UI:
    def __init__(self, pygame_settings, resources, tilesets, db, log=True):
        self.resources = resources
        self.tilesets = tilesets
        self.pygame_settings = pygame_settings
        self.interactives = []
        self.decoratives = []
        self.key_focus = None
        self.page = 0
        self.updated = False

        # sound collections. REMOVE THIS , REMOVE SOUND FROM UI . GENERATE SOUNDS IN WINS
        self.snd_packs = {}
        for preset_name, preset_pack in self.resources.sound_presets.items():
            self.snd_packs[preset_name] = [pygame_settings.audio.bank_sounds[snd_name] for snd_name in preset_pack]

    def mouse_actions(self, mouse_x, mouse_y, event):
        # mouse events checking
        if event.type == pygame.MOUSEBUTTONDOWN:
            for interact in self.interactives:
                if interact.page is not None and interact.page != self.page:
                    continue
                # if interactive element is disabled then pass
                if interact.mode == -1:
                    continue
                try:
                    if interact.rendered_rect.collidepoint((mouse_x, mouse_y)):
                        return interact, event.button, 'down'
                except AttributeError:
                    pass
            # if clicked outside interactive elements, remove focus
        elif event.type == pygame.MOUSEBUTTONUP:
            inter_click = None
            for interact in self.interactives:
                if interact.page is not None and interact.page != self.page:
                    continue
                try:
                    if interact.rendered_rect.collidepoint((mouse_x, mouse_y)):
                        inter_click = (interact, event.button, 'up')
                    else:
                        interact.release(event.button)
                except AttributeError:
                    pass
            if inter_click is None:
                self.key_focus = None
            return inter_click

    def interaction_callback(self, element, event, bttn):
        if event == 'down':
            element.mouse_down(bttn)
        elif event == 'up':
            element.mouse_up(bttn)

    # UI ELEMENTS CREATION
    def button_add(self, bttn_id, xy=None, size=None, caption=None, images=None,
                   cap_font='def_bold', cap_size=None, cap_color=None, cap_shadow=False, sounds=None,
                   mode=0, switch=False, function=None, page=0, pop_show=30, pop_hide=1, pop_win=None):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if caption is None:
            caption = bttn_id
        if images is None:
            rnd_texture = self.random_texture(size, 'red_glass')
            images = (
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                              sq_image=rnd_texture),
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=False,
                              sq_image=rnd_texture),
            )
        if cap_size is None:
            cap_size = 48
        if cap_color is None:
            cap_color = self.resources.colors['black']
        else:
            cap_color = self.resources.colors[cap_color]

        text_xy = size[0] // 2, size[1] // 2
        text_bg_color = images[0].get_at(text_xy)
        text = typography.Typography(self.pygame_settings, caption, text_xy, cap_font, cap_size, cap_color,
                                     text_bg_color, 'center', 'middle', size[0], size[1], shadow=cap_shadow)

        new_button = button.Button(bttn_id, xy, size, text_obj=text, bttn_func=function, bttn_images=images,
                                   bttn_sounds=sounds, bttn_mode=mode, bttn_switch=switch,
                                   pop_show=pop_show, pop_hide=pop_hide, pop_win=pop_win, page=page)
        return new_button

    def edit_add(self, edit_id, xy=None, size=None, caption=None, max_len=12, h_align='left', images=None,
                 cap_font='def_bold', cap_size=None, cap_color=None, cap_shadow=False, cursor_symbol='|', sounds=None,
                 blink=30,
                 mode=0, pop_show=30, pop_hide=1, pop_win=None, page=0):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if caption is None:
            caption = edit_id
        if images is None:
            images = (
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=True, sq_image=None),
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=True, sq_image=None),
            )
        if cap_size is None:
            cap_size = 24
        if cap_color is None:
            cap_color = self.resources.colors['fnt_celeb']
        else:
            cap_color = self.resources.colors[cap_color]

        text_xy = 0, size[1] // 2
        if h_align == 'center':
            text_xy = size[0] // 2, size[1] // 2
        elif h_align == 'right':
            text_xy = size[0] - 1, size[1] // 2
        text_bg_color = images[0].get_at(text_xy)
        inp_text = typography.Typography(self.pygame_settings, caption, text_xy, cap_font, cap_size,
                                         cap_color, text_bg_color, h_align, 'middle', size[0], size[1],
                                         shadow=cap_shadow)
        cur_text = typography.Typography(self.pygame_settings, cursor_symbol, text_xy, cap_font, cap_size,
                                         cap_color, text_bg_color, 'left', 'middle', size[0], size[1],
                                         shadow=cap_shadow)
        new_edit = fieldedit.FieldEdit(edit_id, xy, size, text_obj=inp_text, cursor_obj=cur_text, fe_images=images,
                                       fe_maxlen=max_len, fe_blink=blink, fe_sounds=sounds, fe_mode=mode,
                                       pop_show=pop_show, pop_hide=pop_hide, pop_win=pop_win, page=page)
        return new_edit

    def text_add(self, edit_id, xy=None, size=None, caption=None, h_align='left', v_align='top', images=None,
                 cap_font='def_normal', cap_size=None, cap_color='sun', cap_shadow=False, cap_bgcolor='black',
                 pop_show=30, pop_hide=1, pop_win=None, page=None):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 48)
        if caption is None:
            caption = """Артур Эрнст Глазевальд родился в семье переплётчика Артура Глазевальда. Артур сам вначале стал 
            переплётчиком по профессии, уже позже стал торговать почтовыми марками. Коллекционированием почтовых марок 
            Артур увлёкся школьником в возрасте семи лет. Формированию его коллекции способствовал отец, который до 
            этого путешествовал по Скандинавии в течение 10 лет. Ещё больше филателистического материала поступило от 
            его дяди, живущего в США. После прохождения ученичества на переплетчика Глазевальд стал странствующим 
            мастером в 1878 году. До 1882 года он работал у продавца книг Левенталя (Löwenthal) в Касселе, в витрине 
            магазина которого были выставлены на продажу большие марочные листы"""
        if cap_size is None:
            cap_size = 24
        cap_color = self.resources.colors[cap_color]
        cap_bgcolor = self.resources.colors[cap_bgcolor]

        txt_x, txt_y = 0, 0
        if h_align == 'center':
            txt_x = size[0] // 2
        elif h_align == 'right':
            txt_x = size[0] - 1
        if v_align == 'middle':
            txt_y = size[1] // 2
        elif v_align == 'bottom':
            txt_y = size[1] - 1
        text_xy = txt_x, txt_y
        inp_text = typography.Typography(self.pygame_settings, caption, text_xy, cap_font, cap_size,
                                         cap_color, cap_bgcolor, h_align, v_align, size[0], size[1], shadow=cap_shadow)
        new_text = fieldtext.FieldText(edit_id, xy, size, text_obj=inp_text, ft_images=images, page=page)
        return new_text

    def panel_add(self, edit_id, xy=None, size=None, images=None,
                  pop_show=30, pop_hide=1, pop_win=None, page=None, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 48)

        new_panel = panel.Panel(edit_id, xy, size, pan_images=images, page=page, img_stretch=img_stretch)
        return new_panel

    def context_headline_info(self, resources, context_id, xy=None, size=None, images=None, text_dict=None,
                              cap_bgcolor='black', page=None, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if text_dict is None:
            text_dict = {
                'gradetype': 'gradetype',
                'mainvalue': '123456',
                'mv_caption': 'mv_caption'
            }
        if images is None:
            """images = (
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=0, sq_bsize=0, sq_ldir=0, sq_fill=False,
                              sq_image=None),
            )"""
        info_text = {
            'gradetype': typography.Typography(self.pygame_settings, text_dict['gradetype'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'], self.resources.colors['transparent'],
                                               'left', 'top', size[0], 24),
            'mainvalue': typography.Typography(self.pygame_settings, text_dict['mainvalue'], (0, 0), 'large', 18,
                                               self.resources.colors['fnt_celeb'], self.resources.colors['black'],
                                               'left', 'top', size[0], 48),
            'mv_caption': typography.Typography(self.pygame_settings, text_dict['mv_caption'], (0, 0), 'def_normal', 24,
                                                self.resources.colors['fnt_celeb'],
                                                self.resources.colors['transparent'],
                                                'left', 'top', size[0], 24)
        }
        for key, text in text_dict.items():
            info_text[key].caption = text
        new_rich = fieldrich.FieldRich(resources, context_id, xy, size, fr_images=images, text_dict=info_text, pop_show=60,
                                       pop_hide=30, pop_win=None, page=None, img_stretch=img_stretch)
        return new_rich

    def context_body_info(self, resources, context_id, xy=None, size=None, images=None, text_dict=None,
                          cap_bgcolor='black', page=None, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if text_dict is None:
            text_dict = {
                'modifiers': 'modifiers',
                'de_buffs': 'de_buffs',
                'affixes': 'affixes',
                'affix_de_buffs': 'affix_de_buffs',
                'desc': 'desc',
                'sell_price': 'sell_price',
                'condition': 'condition'
            }
        if images is None:
            images = (
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                              sq_image=None),
            )
        info_text = {
            'modifiers': typography.Typography(self.pygame_settings, text_dict['modifiers'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0),
            'de_buffs': typography.Typography(self.pygame_settings, text_dict['de_buffs'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0),
            'affixes': typography.Typography(self.pygame_settings, text_dict['affixes'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_header'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0),
            'affix_de_buffs': typography.Typography(self.pygame_settings, text_dict['affix_de_buffs'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0),
            'desc': typography.Typography(self.pygame_settings, text_dict['desc'], (0, 0), 'def_normal', 24,
                                          self.resources.colors['fnt_celeb'],
                                          self.resources.colors['transparent'],
                                          'left', 'top', size[0], 0),
            'sell_price': typography.Typography(self.pygame_settings, text_dict['sell_price'], (0, 0), 'def_normal', 24,
                                          self.resources.colors['bright_gold'],
                                          self.resources.colors['transparent'],
                                          'left', 'top', size[0], 0),
            'condition': typography.Typography(self.pygame_settings, text_dict['condition'], (0, 0), 'def_normal', 24,
                                                self.resources.colors['fnt_celeb'],
                                                self.resources.colors['transparent'],
                                                'left', 'top', size[0], 0),
        }
        for key, text in text_dict.items():
            if text == '':
                del info_text[key]

        new_rich = fieldrich.FieldRich(resources, context_id, xy, size, fr_images=images, text_dict=info_text, pop_show=60,
                                       pop_hide=30, pop_win=None, page=None, img_stretch=img_stretch)
        return new_rich

    def element_align(self, element, origin_xy, view_rect):
        """if origin_xy[0] - view_rect.left < element.rendered_rect.width:
            element.rendered_rect.left = origin_xy[0]
        if origin_xy[1] - view_rect.top < element.rendered_rect.height:
            element.rendered_rect.top = origin_xy[1]"""
        element.rendered_rect.left = origin_xy[0]
        element.rendered_rect.top = origin_xy[1]

    def random_texture(self, size, tileset_name):
        tileset = self.tilesets.sets_dict[tileset_name]
        ts_rect = tileset.get_rect()
        rnd_x = random.randrange(0, ts_rect.width - size[0])
        rnd_y = random.randrange(0, ts_rect.height - size[1])
        return tileset.subsurface((rnd_x, rnd_y, size[0], size[1]))

    def tick(self, pygame_settings, mouse_pointer):
        for element in self.interactives:
            if element.page is not None and element.page != self.page:
                continue
            try:
                element.tick()
            except AttributeError:
                pass

    def draw(self, surface):
        for decorative in reversed(self.decoratives):
            if decorative.page is not None and decorative.page != self.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.interactives):
            if interactive.page is not None and interactive.page != self.page:
                continue
            interactive.draw(surface)
        self.updated = False
