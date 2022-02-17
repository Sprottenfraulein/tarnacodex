# user interface object
import pygame
import random
from library import pydraw, typography, button, fieldedit, fieldtext, fieldrich, panel


class UI:
    def __init__(self, pygame_settings, resources, tilesets, db, mouse_pointer, log=True):
        self.resources = resources
        self.tilesets = tilesets
        self.pygame_settings = pygame_settings
        self.db = db
        self.mouse_pointer = mouse_pointer

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
                if interact.page is not None and self.page not in interact.page:
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
                if interact.page is not None and self.page not in interact.page:
                    continue
                try:
                    if inter_click is None and interact.rendered_rect.collidepoint((mouse_x, mouse_y)):
                        inter_click = (interact, event.button, 'up')
                    """else:
                        interact.release(event.button)"""
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
                   mode=0, switch=False, function=None, tags=None, page=None):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
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

        if caption is None:
            text = None
        else:
            text_xy = size[0] // 2, size[1] // 2
            text_bg_color = images[0].get_at(text_xy)
            text = typography.Typography(self.pygame_settings, caption, text_xy, cap_font, cap_size, cap_color,
                                         text_bg_color, 'center', 'middle', size[0], size[1], shadow=cap_shadow)

        new_button = button.Button(bttn_id, xy, size, text_obj=text, bttn_func=function, bttn_images=images,
                                   bttn_sounds=sounds, bttn_mode=mode, bttn_switch=switch, tags=tags,
                                   page=page)
        return new_button

    def edit_add(self, edit_id, xy=None, size=None, caption=None, max_len=12, h_align='left', images=None,
                 cap_font='def_bold', cap_size=None, cap_color=None, cap_shadow=False, cursor_symbol='|', sounds=None,
                 blink=30, mode=0, page=None):
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
                               self.resources.colors['gray_darker'],
                               self.resources.colors['black']),
                              sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=True, sq_image=None),
                pydraw.square((0, 0), size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_darker'],
                               self.resources.colors['sun']),
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
        cur_text = typography.Typography(self.pygame_settings, cursor_symbol, (0, text_xy[1]), cap_font, cap_size,
                                         cap_color, text_bg_color, 'left', 'middle', size[0], size[1],
                                         shadow=cap_shadow)
        new_edit = fieldedit.FieldEdit(self, edit_id, xy, size, text_obj=inp_text, cursor_obj=cur_text, fe_images=images,
                                       fe_maxlen=max_len, fe_blink=blink, fe_align=h_align,fe_sounds=sounds, fe_mode=mode, page=page)
        return new_edit

    def text_add(self, edit_id, xy=None, size=None, caption=None, h_align='left', v_align='top', images=None,
                 cap_font='def_normal', cap_size=None, cap_color='sun', cap_shadow=False, cap_bgcolor='black',
                 page=None):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 48)
        if caption is None:
            caption = """123"""
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

    def panel_add(self, edit_id, xy=None, size=None, images=None, page=None, img_stretch=False, tags=None, win=None):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 48)

        new_panel = panel.Panel(edit_id, xy, size, pan_images=images, page=page, img_stretch=img_stretch, tags=tags,
                                win=win)
        return new_panel

    def context_headline_info(self, context_id, xy=None, size=None, images=None, text_dict=None,
                              cap_bgcolor='black', page=None, par_div_height=4, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if text_dict is None:
            text_dict = {

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
        if 'gradetype' in text_dict:
            text_dict['gradetype'] = typography.Typography(self.pygame_settings, text_dict['gradetype'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'], self.resources.colors['transparent'],
                                               'left', 'top', size[0], 24)
        if 'mainvalue' in text_dict:
            text_dict['mainvalue'] = typography.Typography(self.pygame_settings, text_dict['mainvalue'], (0, 0), 'large', 18,
                                           self.resources.colors['fnt_celeb'], self.resources.colors['black'],
                                           'left', 'top', size[0], 48)
        if 'mv_caption' in text_dict:
            text_dict['mv_caption'] = typography.Typography(self.pygame_settings, text_dict['mv_caption'], (0, 0), 'def_normal', 24,
                                            self.resources.colors['fnt_celeb'],
                                            self.resources.colors['transparent'],
                                            'left', 'top', size[0], 24)

        new_rich = fieldrich.FieldRich(self.resources, context_id, xy, size, fr_images=images, text_dict=text_dict,
                                        par_div_height=par_div_height, page=None, img_stretch=img_stretch)
        return new_rich

    def context_body_info(self, context_id, xy=None, size=None, images=None, text_dict=None,
                          cap_bgcolor='black', page=None, par_div_height=4, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if text_dict is None:
            text_dict = {

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
        if 'modifiers' in text_dict:
            text_dict['modifiers'] = typography.Typography(self.pygame_settings, text_dict['modifiers'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0)
        if 'de_buffs' in text_dict:
            text_dict['de_buffs'] = typography.Typography(self.pygame_settings, text_dict['de_buffs'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0)
        if 'affixes' in text_dict:
            text_dict['affixes'] = typography.Typography(self.pygame_settings, text_dict['affixes'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_header'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0)
        if 'affix_de_buffs' in text_dict:
            text_dict['affix_de_buffs'] = typography.Typography(self.pygame_settings, text_dict['affix_de_buffs'], (0, 0), 'def_normal', 24,
                                               self.resources.colors['fnt_celeb'],
                                               self.resources.colors['transparent'],
                                               'left', 'top', size[0], 0)
        if 'desc' in text_dict:
            text_dict['desc'] = typography.Typography(self.pygame_settings, text_dict['desc'], (0, 0), 'def_normal', 24,
                                          self.resources.colors['fnt_celeb'],
                                          self.resources.colors['transparent'],
                                          'left', 'top', size[0], 0)
        if 'price' in text_dict:
            text_dict['price'] = typography.Typography(self.pygame_settings, text_dict['price'], (0, 0), 'def_normal', 24,
                                          self.resources.colors['bright_gold'],
                                          self.resources.colors['transparent'],
                                          'left', 'top', size[0], 0)
        if 'condition' in text_dict:
            text_dict['condition'] = typography.Typography(self.pygame_settings, text_dict['condition'], (0, 0), 'def_normal', 24,
                                                self.resources.colors['fnt_celeb'],
                                                self.resources.colors['transparent'],
                                                'left', 'top', size[0], 0)

        new_rich = fieldrich.FieldRich(self.resources, context_id, xy, size, fr_images=images, text_dict=text_dict,
                                       par_div_height=par_div_height, page=None, img_stretch=img_stretch)
        return new_rich

    def context_paragraphs(self, context_id, xy=None, size=None, images=None, text_dict=None,
                          cap_bgcolor='black', page=None, par_div_height=4, img_stretch=False):
        # setting defaults if attributes not presented:
        if xy is None:
            xy = (0, 0)
        if size is None:
            size = (96, 32)
        if text_dict is None:
            text_dict = {
                'desc': 'desc',
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
            'desc': typography.Typography(self.pygame_settings, text_dict['desc'], (0, 0), 'def_normal', 24,
                                          self.resources.colors['fnt_celeb'],
                                          self.resources.colors['transparent'],
                                          'left', 'top', size[0], 0)
        }
        for key, text in text_dict.items():
            if text == '':
                del info_text[key]

        new_rich = fieldrich.FieldRich(self.resources, context_id, xy, size, fr_images=images, text_dict=info_text,
                                       par_div_height=par_div_height, img_stretch=img_stretch)
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
        rnd_x = random.randrange(0, ts_rect.width - size[0] + 1)
        rnd_y = random.randrange(0, ts_rect.height - size[1] + 1)
        return tileset.subsurface((rnd_x, rnd_y, size[0], size[1]))

    def tick(self):
        for element in self.interactives:
            if element.page is not None and self.page not in element.page:
                continue
            if hasattr(element, 'tick'):
                element.tick()

    def draw(self, surface):
        for decorative in reversed(self.decoratives):
            if decorative.page is not None and self.page not in decorative.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.interactives):
            if interactive.page is not None and self.page not in interactive.page:
                continue
            interactive.draw(surface)
        self.updated = False
