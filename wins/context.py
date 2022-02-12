# game title window
import pygame
import settings
from components import ui, treasure, skillfuncs
from library import pydraw, maths


class Context:
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
        self.offset_x = 0
        self.offset_y = 0

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        """mouse_x, mouse_y = self.mouse_pointer.xy
        return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                             self.pygame_settings, resources, self.wins_dict, self.active_wins)"""
        pass

    def ui_click(self, inter_click):
        pass

    def context_info_update(self, pc, element):
        # Here I need to write making changes to context_info_rich element
        for i in ('itm', 'skill', 'hot'):
            if i in element.tags:
                break
        else:
            return
        if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
            itm = element.tags[0][element.id]
            self.context_define(pc, itm, element)

    def context_define(self, pc, itm, element):
        if itm.props['item_type'] in ('wpn_melee', 'wpn_ranged'):
            self.wins_dict['context'].update_elements_weapon(pc, itm, element, self.mouse_pointer.xy)
        elif itm.props['item_type'] in ('skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc'):
            self.wins_dict['context'].update_elements_skill(pc, itm, element, self.mouse_pointer.xy)
        elif itm.props['item_type'] in ('sup_potion', 'exp_food'):
            self.wins_dict['context'].update_elements_supply(pc, itm, element, self.mouse_pointer.xy)
        elif itm.props['item_type'] in ('exp_lockpick','exp_tools'):
            self.wins_dict['context'].update_elements_lockpick(pc, itm, element, self.mouse_pointer.xy)
        elif itm.props['item_type'] in ('aug_gem',):
            self.wins_dict['context'].update_elements_charm(pc, itm, element, self.mouse_pointer.xy)
        element.popup_active = True
        self.active_wins.insert(0, self.wins_dict['context'])

    # interface creation
    def update_elements_weapon(self, pc, item, element, mouse_xy, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        self.win_w = 240
        itm_img_size = (48, 48)

        # color based on grade
        decor_color = self.resources.grade_colors[item.props['grade']]
        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    self.resources.grades_loot[item.props['grade']] + ' ' + item.props['class']).capitalize(),
            'mainvalue': '%s-%s' % pc.char_sheet.calc_attack_base(weapon=item.props),
            'mv_caption': 'Damage'
        }
        itm_headlines = self.win_ui.context_headline_info('headlines',
                                                          (itm_img_size[0] + 16, 32),
                                                          (self.win_w - (itm_img_size[0] + 24), itm_img_size[1]),
                                                          images=None, text_dict=hl_text, cap_bgcolor='black',
                                                          page=None)
        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'sell_price': str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell')),
            'condition': str('Condition: %s/%s' % (item.props['condition'] //10, treasure.calc_loot_stat(item.props, 'condition_max') //10))
        }
        body_text = {k: v for k, v in body_text.items() if v}
        itm_bodylines = self.win_ui.context_body_info('body_text',
                                                      (8, 104),
                                                      (self.win_w - 16, itm_img_size[1]),
                                                      images=None, text_dict=body_text, cap_bgcolor='black',
                                                      page=None)
        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + 104 + 8
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (self.win_w - 8, 24),
                                   (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (4, 4), (self.win_w - 8, 24),
                                              caption=treasure.loot_calc_name(item.props).upper(),
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))

        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(bg_image,),
                                         page=None)

        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.resources.colors[decor_color],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8,8))
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (4, 32), (itm_img_w, itm_img_h), images=(item_icon,),
                                               page=None)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.win_ui.draw(self.win_rendered)

    def update_elements_skill(self, pc, item, element, mouse_xy, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        win_width = 320
        itm_img_size = (48, 48)
        itm_img_top = 32

        # color based on grade
        decor_color = self.resources.grade_colors[item.props['grade']]
        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.resources.colors[decor_color],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8, 8))
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (4, itm_img_top), (itm_img_w, itm_img_h), images=(item_icon,),
                                               page=None)
        # calculating and rendering text
        bl_text = {
            'desc': item.props['desc'] % getattr(skillfuncs, item.props['function_name'])(None, None, pc, item.props, (element.tags[0], element.id) ,just_values=True)
        }
        itm_bodylines = self.win_ui.context_paragraphs('bodylines',
                                                       (itm_img_size[0] + 16, itm_img_top),
                                                       (win_width - (itm_img_size[0] + 24), itm_img_size[1]),
                                                       images=None, text_dict=bl_text, cap_bgcolor='black',
                                                       page=None)
        itm_bodylines.render_all()

        win_height = max(itm_bodylines.size[1], itm_img_top + itm_img_h) + 8
        self.win_rendered = pygame.Surface((win_width, win_height)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (win_width, win_height),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (win_width - 8, 24),
                                   (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (4, 4), (win_width - 8, 24),
                                              caption=item.props['label'].upper(),
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))

        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (win_width, win_height), images=(bg_image,),
                                         page=None)



        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], win_width, win_height, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, win_width, win_height, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.win_ui.draw(self.win_rendered)

    def update_elements_supply(self, pc, item, element, mouse_xy, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        self.win_w = 240
        itm_img_size = (48, 48)

        # color based on grade
        decor_color = self.resources.grade_colors[item.props['grade']]
        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    self.resources.grades_loot[item.props['grade']] + ' ' + item.props['class']).capitalize(),
            'mainvalue': '%s' % getattr(skillfuncs, item.props['use_skill'].props['function_name'])(None, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True),
            'mv_caption': 'Supply'
        }
        itm_headlines = self.win_ui.context_headline_info('headlines',
                                                          (itm_img_size[0] + 16, 32),
                                                          (self.win_w - (itm_img_size[0] + 24), itm_img_size[1]),
                                                          images=None, text_dict=hl_text, cap_bgcolor='black',
                                                          page=None)
        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] % getattr(skillfuncs, item.props['use_skill'].props['function_name'])(None, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True) + ' '),
            'sell_price': str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))
        }
        body_text = {k: v for k, v in body_text.items() if v}
        itm_bodylines = self.win_ui.context_body_info('body_text',
                                                      (8, 104),
                                                      (self.win_w - 16, itm_img_size[1]),
                                                      images=None, text_dict=body_text, cap_bgcolor='black',
                                                      page=None)
        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + 104 + 8
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (self.win_w - 8, 24),
                                   (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (4, 4), (self.win_w - 8, 24),
                                              caption=treasure.loot_calc_name(item.props).upper(),
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))

        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(bg_image,),
                                         page=None)

        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.resources.colors[decor_color],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8,8))
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (4, 32), (itm_img_w, itm_img_h), images=(item_icon,),
                                               page=None)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.win_ui.draw(self.win_rendered)

    def update_elements_lockpick(self, pc, item, element, mouse_xy, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        self.win_w = 240
        itm_img_size = (48, 48)

        # color based on grade
        decor_color = self.resources.grade_colors[item.props['grade']]
        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    self.resources.grades_loot[item.props['grade']] + ' ' + item.props['class']).capitalize(),
            'mainvalue': '%s' % ((treasure.calc_loot_stat(item.props, 'prof_picklock') + pc.char_sheet.profs['prof_picklock']) // 10) + '%',
            'mv_caption': 'Expendable'
        }
        itm_headlines = self.win_ui.context_headline_info('headlines',
                                                          (itm_img_size[0] + 16, 32),
                                                          (self.win_w - (itm_img_size[0] + 24), itm_img_size[1]),
                                                          images=None, text_dict=hl_text, cap_bgcolor='black',
                                                          page=None)
        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': item.props['desc'] % ((treasure.calc_loot_stat(item.props, 'prof_picklock') + pc.char_sheet.profs['prof_picklock']) // 10),
            'sell_price': str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))
        }
        body_text = {k: v for k, v in body_text.items() if v}
        itm_bodylines = self.win_ui.context_body_info('body_text',
                                                      (8, 104),
                                                      (self.win_w - 16, itm_img_size[1]),
                                                      images=None, text_dict=body_text, cap_bgcolor='black',
                                                      page=None)
        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + 104 + 8
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (self.win_w - 8, 24),
                                   (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (4, 4), (self.win_w - 8, 24),
                                              caption=treasure.loot_calc_name(item.props).upper(),
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))

        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(bg_image,),
                                         page=None)

        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.resources.colors[decor_color],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8,8))
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (4, 32), (itm_img_w, itm_img_h), images=(item_icon,),
                                               page=None)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.win_ui.draw(self.win_rendered)

    def update_elements_charm(self, pc, item, element, mouse_xy, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        self.win_w = 240
        itm_img_size = (48, 48)

        # color based on grade
        decor_color = self.resources.grade_colors[item.props['grade']]
        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    self.resources.grades_loot[item.props['grade']] + ' ' + item.props['class']).capitalize(),

        }
        itm_headlines = self.win_ui.context_headline_info('headlines',
                                                          (itm_img_size[0] + 16, 32),
                                                          (self.win_w - (itm_img_size[0] + 24), itm_img_size[1]),
                                                          images=None, text_dict=hl_text, cap_bgcolor='black',
                                                          page=None)
        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'sell_price': str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))
        }
        body_text = {k: v for k, v in body_text.items() if v}
        itm_bodylines = self.win_ui.context_body_info('body_text',
                                                      (8, 104),
                                                      (self.win_w - 16, itm_img_size[1]),
                                                      images=None, text_dict=body_text, cap_bgcolor='black',
                                                      page=None)
        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + 104 + 8
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])
        # background
        bg_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        header_img = pydraw.square((0, 0), (self.win_w - 8, 24),
                                   (self.resources.colors['gray_light'],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (4, 4), (self.win_w - 8, 24),
                                              caption=treasure.loot_calc_name(item.props).upper(),
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))

        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(bg_image,),
                                         page=None)

        # item icon
        item_image = pygame.transform.scale(item.props['image_inventory'][0], itm_img_size)
        itm_img_w, itm_img_h = itm_img_size[0] + 16, itm_img_size[1] + 16
        item_icon = pydraw.square((0, 0), (itm_img_w, itm_img_h),
                                  (self.resources.colors[decor_color],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=0, sq_ldir=4, sq_fill=False,
                                  sq_image=None)
        item_icon.blit(item_image, (8,8))
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (4, 32), (itm_img_w, itm_img_h), images=(item_icon,),
                                               page=None)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.win_ui.draw(self.win_rendered)

    def decorated_modifiers(self, mods):
        mod_list = []
        for mod, vals in mods.items():
            p_n = mod
            vb_str = str(vals['value_base'])
            if vals['value_type'] == 0:
                vb_str = '=' + vb_str
            elif vals['value_base'] >= 0 and p_n != 'att_base':
                vb_str = '+' + vb_str
            if 'value_spread' in vals:
                vs_str = str(vals['value_base'] + vals['value_spread'])
                if vals['value_base'] < 0 and (vals['value_spread'] + vals['value_base']) > 0:
                    vs_str = '+' + vs_str
                mod_num = '%s-%s %s' % (vb_str, vs_str, self.resources.stat_captions[p_n])
            else:
                mod_num = '%s %s' % (vb_str, self.resources.stat_captions[p_n])
            mod_list.append(mod_num)
        return ' $n '.join(mod_list)

    def decorated_de_buffs(self, de_buffs):
        deb_list = []
        for deb in de_buffs:
            deb_list.append(deb['label'])
            # deb_list.append(deb['desc'])
        return ' $n '.join(deb_list)

    def tick(self):
        self.win_ui.tick()

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
