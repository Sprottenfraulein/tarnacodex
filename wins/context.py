# game title window
import pygame
import math
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

        self.win_w = 240
        self.win_h = 240
        self.itm_img_size = (48, 48)
        self.image_body_space_size = 12
        self.win_border_size = 8

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

    def end(self):
        if self in self.active_wins:
            self.active_wins.remove(self)

    def context_info_update(self, pc, element, trade=False):
        # Here I need to write making changes to context_info_rich element
        for i in ('itm', 'skill', 'hot'):
            if i in element.tags:
                if element.id < len(element.tags[0]) and element.tags[0][element.id] is not None:
                    itm = element.tags[0][element.id]
                    self.context_define(pc, itm, element, trade=trade)
                    return
        if 'de_buff' in element.tags:
            self.update_elements_de_buff(pc, element.tags[0], element, self.mouse_pointer.xy)
            element.popup_active = True
            self.active_wins.insert(0, self.wins_dict['context'])
            return


    def context_define(self, pc, itm, element, trade=False):
        if itm.props['item_type'] in ('wpn_melee', 'wpn_ranged', 'wpn_magic'):
            self.wins_dict['context'].update_elements_weapon(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('orb_ammo'):
            self.wins_dict['context'].update_elements_ammo(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('arm_head', 'arm_chest', 'orb_shield'):
            self.wins_dict['context'].update_elements_armor(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('acc_ring',):
            self.wins_dict['context'].update_elements_accessory(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('skill_melee', 'skill_ranged', 'skill_magic', 'skill_craft', 'skill_misc', ):
            self.wins_dict['context'].update_elements_skill(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('use_learn',):
            self.wins_dict['context'].update_elements_certificate(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('use_wand', ):
            self.wins_dict['context'].update_elements_wand(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('use_craft'):
            self.wins_dict['context'].update_elements_recipe(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('sup_potion', 'exp_food'):
            self.wins_dict['context'].update_elements_supply(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('exp_res',):
            self.wins_dict['context'].update_elements_resource(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] == 'exp_lockpick':
            self.wins_dict['context'].update_elements_lockpick(
                pc, itm, (
                    (treasure.calc_loot_stat(itm.props, 'prof_picklock') + pc.char_sheet.profs['prof_picklock']) // 10
                ), element, self.mouse_pointer.xy, trade=trade
            )
        elif itm.props['item_type'] == 'exp_tools':
            self.wins_dict['context'].update_elements_lockpick(
                pc, itm, (
                    (treasure.calc_loot_stat(itm.props, 'prof_disarm') + pc.char_sheet.profs['prof_disarm']) // 10
                ), element, self.mouse_pointer.xy, trade=trade
            )
        elif itm.props['item_type'] == 'light':
            self.wins_dict['context'].update_elements_light(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('aug_gem', 'misc_man'):
            self.wins_dict['context'].update_elements_charm(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        elif itm.props['item_type'] in ('exp_key',):
            self.wins_dict['context'].update_elements_key(pc, itm, element, self.mouse_pointer.xy, trade=trade)
        element.popup_active = True
        self.active_wins.insert(0, self.wins_dict['context'])

    # interface creation
    def update_elements_weapon(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s-%s' % pc.char_sheet.calc_attack_base(weapon=item.props),
            'mv_caption': 'Damage'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'condition': str('Condition: %s/%s' % (
            math.ceil(item.props['condition'] / 10), math.ceil(treasure.calc_loot_stat(item.props, 'condition_max') / 10)))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_ammo(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s-%s' % pc.char_sheet.calc_attack_base(),
            'mv_caption': 'Damage'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'amount': str('Amount: %s' % (item.props['amount']))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_armor(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s' % treasure.calc_loot_stat(item.props, 'def_physical'),
            'mv_caption': 'Defence'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'condition': str('Condition: %s/%s' % (
            math.ceil(item.props['condition'] / 10), math.ceil(treasure.calc_loot_stat(item.props, 'condition_max') / 10)))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_accessory(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s' % treasure.calc_loot_stat(item.props, list(item.props['mods'].keys())[0]),
            'mv_caption': self.resources.stat_captions[list(item.props['mods'].keys())[0]]
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
            'condition': str('Condition: %s/%s' % (
            math.ceil(item.props['condition'] / 10), math.ceil(treasure.calc_loot_stat(item.props, 'condition_max') / 10)))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_skill(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = 'azure'

        header_caption = item.props['label'].upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': 'Skill',
            'mainvalue': '%s' % (pc.char_sheet.level or '-'),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)
        itm_headlines.render_all()

        bl_text = {
            'desc': item.props['desc'] % getattr(skillfuncs, item.props['function_name'])(self.wins_dict, None, pc,
                                                                                          item,
                                                                                          (element.tags[0], element.id),
                                                                                          just_values=True)
        }
        itm_bodylines = self.body_text_add(bl_text, info_y)
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_certificate(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = 'azure'

        header_caption = item.props['label'].upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        types = {
            (1, 0, 0): 'Only for Champion',
            (0, 1, 0): 'Only for Kingslayer',
            (0, 0, 1): 'Only for Cosmologist',
            (1, 0, 1): 'Not for Kingslayer',
            (1, 1, 0): 'Not for Cosmologist',
            (0, 1, 1): 'Not for Champion',
            (1, 1, 1): 'For any character',
        }[(
            item.props['usable_champion'],
            item.props['usable_kingslayer'],
            item.props['usable_cosmologist'],
        )]
        hl_text = {
            'gradetype': types,
            'mainvalue': '%s' % (item.props['lvl'] or '-'),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)
        itm_headlines.render_all()

        # calculating and rendering text
        bl_text = {
            'desc': item.props['desc']
        }
        if trade:
            bl_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            bl_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(bl_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_wand(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = 'azure'

        header_caption = item.props['label'].upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        hl_text = {
            'gradetype': item.props['class'].capitalize(),
            'mainvalue': '%s' % (item.props['lvl'] or '-'),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)
        itm_headlines.render_all()

        # calculating and rendering text
        bl_text = {
            'desc': (item.props['desc'] % getattr(skillfuncs, item.props['use_skill'].props['function_name'])(self.wins_dict, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True) + ' ')
        }
        if 'charge' in item.props:
            bl_text['charges'] = 'Charge: %s/%s' % (
                item.props['charge'], treasure.calc_loot_stat(item.props, 'charge_max'))
        if 'condition' in item.props:
            bl_text['condition'] = 'Condition: %s/%s' % (
                item.props['condition'], treasure.calc_loot_stat(item.props, 'condition_max'))
        if trade:
            bl_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            bl_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(bl_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_recipe(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = 'azure'

        header_caption = item.props['label'].upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        hl_text = {
            'gradetype': 'Recipe',
            'mainvalue': '%s' % (item.props['lvl'] or '-'),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)
        itm_headlines.render_all()

        # calculating and rendering text
        bl_text = {
            'desc': (
                item.props['desc'] % getattr(
                    skillfuncs, item.props['use_skill'].props['function_name']
                )(
                    self.wins_dict, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True
                ) + ' '
            )
        }
        if trade:
            bl_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            bl_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(bl_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_supply(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s' % getattr(skillfuncs, item.props['use_skill'].props['function_name'])(self.wins_dict, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True),
            'mv_caption': 'Points'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] % getattr(skillfuncs, item.props['use_skill'].props['function_name'])(self.wins_dict, None, pc, item.props['use_skill'], (element.tags[0], element.id), just_values=True) + ' ')
        }
        if 'charge' in item.props:
            body_text['charges'] = 'Charge: %s/%s' % (
                item.props['charge'], treasure.calc_loot_stat(item.props, 'charge_max'))
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_resource(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': 'Ingredient',
            'mainvalue': '%s' % (item.props['lvl'] or '-'),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'desc': item.props['desc']
        }
        if 'charge' in item.props:
            body_text['charges'] = 'Charge: %s/%s' % (
                item.props['charge'], treasure.calc_loot_stat(item.props, 'charge_max'))
        if 'condition' in item.props:
            body_text['condition'] = 'Condition: %s/%s' % (
                item.props['condition'], treasure.calc_loot_stat(item.props, 'condition_max'))
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_lockpick(self, pc, item, main_value, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '%s' % main_value + '%',
            'mv_caption': 'Success rate'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': item.props['desc'] % ((treasure.calc_loot_stat(item.props, 'prof_picklock') + pc.char_sheet.profs[
                'prof_picklock']) // 10),
            'condition': str('Condition: %s/%s' % (
                math.ceil(item.props['condition'] / 10),
                math.ceil(treasure.calc_loot_stat(item.props, 'condition_max') / 10)))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_charm(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),

        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': (item.props['desc'] + ' '),
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_key(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': (
                    item.props['grade']['label'] + ' ' + item.props['class']).capitalize(),
            'mainvalue': '%s' % (item.props['lvl']),
            'mv_caption': 'Level'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join(
                [self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': item.props['desc'] % (item.props['lvl'])
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[
            1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_light(self, pc, item, element, mouse_xy, trade=False, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = item.props['grade']['color']

        header_caption = treasure.loot_calc_name(item.props).upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        hl_text = {
            'gradetype': '%s %s, lv.%s' % (item.props['grade']['label'].capitalize(),
                                item.props['class'].lower(), item.props['lvl'] or '-'),
            'mainvalue': '+%s' % (treasure.calc_loot_stat(item.props, 'prof_light') // 10) + '%',
            'mv_caption': 'Light distance'
        }
        itm_headlines = self.headlines_add(hl_text, info_y)

        body_text = {
            'modifiers': self.decorated_modifiers(item.props['mods']),
            'de_buffs': self.decorated_de_buffs(item.props['de_buffs']),
            'affixes': ' $n '.join([self.decorated_modifiers(affx['mods']) for affx in item.props['affixes']]),
            'affix_de_buffs': ' $n '.join([self.decorated_de_buffs(affx['de_buffs']) for affx in item.props['affixes'] if affx['de_buffs']]),
            'desc': item.props['desc'] % treasure.calc_loot_stat(item.props, 'prof_light'),
            'condition': 'Condition: %s/%s' % (
                math.ceil(item.props['condition'] / 10), math.ceil(treasure.calc_loot_stat(item.props, 'condition_max') / 10))
        }
        if trade:
            body_text['price'] = str('Buy price: %s' % treasure.calc_loot_stat(item.props, 'price_buy'))
        else:
            body_text['price'] = str('Sell price: %s' % treasure.calc_loot_stat(item.props, 'price_sell'))

        itm_bodylines = self.body_text_add(body_text, info_y)

        itm_headlines.render_all()
        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_icon_panel = self.item_icon_add(item, info_y)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_headlines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def update_elements_de_buff(self, pc, item, element, mouse_xy, log=True):
        self.win_ui_clear()

        self.win_w = 240

        # color based on grade
        decor_color = 'gray_light'

        header_caption = item['label'].upper()
        context_header, info_y = self.header_add(header_caption, decor_color)

        # calculating and rendering text
        bl_text = {
            'modifiers': self.decorated_modifiers(item['mods']),
            'desc': item['desc']
        }
        if item['duration'] > 0:
            bl_text['duration'] = '%s:%s' % (item.timer_dur // 3600, str(item.timer_dur % 3600 // 60).zfill(2))

        itm_bodylines = self.body_text_add(bl_text, info_y)

        itm_bodylines.render_all()

        self.win_h = itm_bodylines.size[1] + info_y + self.itm_img_size[1] + self.image_body_space_size + self.win_border_size

        self.win_surface()

        # background
        bg_panel = self.background_add(decor_color)

        # item icon
        itm_img_w, itm_img_h = self.itm_img_size[0], self.itm_img_size[1]
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (self.win_border_size, info_y), (itm_img_w, itm_img_h),
                                               images=element.images, page=None, img_stretch=True)

        self.win_ui.decoratives.append(context_header)
        self.win_ui.decoratives.append(itm_bodylines)
        self.win_ui.decoratives.append(itm_icon_panel)
        self.win_ui.decoratives.append(bg_panel)

        self.win_align(mouse_xy)

        self.win_ui.draw(self.win_rendered)

    def item_icon_add(self, item, y):
        item_icon = pygame.transform.scale(item.props['image_inventory'][0], self.itm_img_size)
        itm_img_w, itm_img_h = self.itm_img_size[0], self.itm_img_size[1]
        itm_icon_panel = self.win_ui.panel_add('inv_panel', (self.win_border_size, y), (itm_img_w, itm_img_h),
                                               images=(item_icon,), page=None)
        return itm_icon_panel

    def win_align(self, mouse_xy):
        self.offset_x, self.offset_y = maths.rect_to_center(mouse_xy[0], mouse_xy[1], self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])
        self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w, self.win_h, 0, 0,
                                                            self.pygame_settings.screen_res[0],
                                                            self.pygame_settings.screen_res[1])

    def background_add(self, decor_color):
        bg_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                 (self.resources.colors[decor_color],
                                  self.resources.colors['gray_dark'],
                                  self.resources.colors['black'],
                                  self.resources.colors['black']),
                                 sq_outsize=1, sq_bsize=2, sq_ldir=4, sq_fill=True, sq_image=None)
        bg_panel = self.win_ui.panel_add('inv_panel', (0, 0), (self.win_w, self.win_h), images=(bg_image,),
                                         page=None)
        return bg_panel

    def win_surface(self):
        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.win_rendered.set_colorkey(self.resources.colors['transparent'])

    def body_text_add(self, body_text, y):
        body_text = {k: v for k, v in body_text.items() if v}
        itm_bodylines = self.win_ui.context_body_info('body_text',
                                                      (self.win_border_size,
                                                       y + self.itm_img_size[1] + self.image_body_space_size),
                                                      (self.win_w - self.win_border_size * 2, self.itm_img_size[1]),
                                                      images=None, text_dict=body_text, cap_bgcolor='black',
                                                      page=None)
        return itm_bodylines

    def paragraph_add(self, itm_img_size, bl_text, y):
        itm_bodylines = self.win_ui.context_paragraphs('bodylines',
                                                       (itm_img_size[0] + 16, y),
                                                       (self.win_w - (itm_img_size[0] + 24), itm_img_size[1]),
                                                       images=None, text_dict=bl_text, cap_bgcolor='black',
                                                       page=None)
        return itm_bodylines

    def headlines_add(self, hl_text, y):
        itm_headlines = self.win_ui.context_headline_info('headlines',
            (self.itm_img_size[0] + self.win_border_size * 2, y - 1),
            (self.win_w - (self.itm_img_size[0] + self.image_body_space_size * 2),
            self.itm_img_size[1]), images=None, text_dict=hl_text, cap_bgcolor='black', par_div_height=0, page=None
        )
        return itm_headlines

    def header_add(self, header_caption, decor_color):
        header_height = math.ceil(len(header_caption) / 28)
        header_img = pydraw.square((0, 0), (self.win_w - self.win_border_size, header_height * 14 + 10),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['black'],
                                    self.resources.colors[decor_color]),
                                   sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=True)
        context_header = self.win_ui.text_add('context_header', (self.win_border_size // 2, self.win_border_size // 2),
                                              (self.win_w - self.win_border_size, header_height * 14 + 10),
                                              caption=header_caption,
                                              h_align='center', v_align='middle', cap_color='fnt_celeb',
                                              cap_font='def_bold', images=(header_img,))
        info_y = header_height * 14 + 14 + 8
        return context_header, info_y

    def win_ui_clear(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

    def decorated_modifiers(self, mods):
        mod_list = []
        for mod, vals in mods.items():
            p_n = mod
            percent = ''
            if vals['value_type'] in (2, 3):
                vb = round(vals['value_base'] / 10, 1)
                percent = '%'
            else:
                vb = vals['value_base']
            vb_str = str(vb)
            if vals['value_type'] == 0:
                vb_str = '=' + vb_str
            elif vals['value_base'] >= 0 and p_n != 'att_base':
                vb_str = '+' + vb_str
            if 'value_spread' in vals:
                if vals['value_type'] in (2, 3):
                    vs = round((vals['value_base'] + vals['value_spread']) / 10, 1)
                else:
                    vs = vals['value_base'] + vals['value_spread']
                vs_str = str(vs)
                if vals['value_base'] < 0 and (vals['value_spread'] + vals['value_base']) > 0:
                    vs_str = '+' + vs_str
                mod_num = '%s-%s%s %s' % (vb_str, vs_str, percent, self.resources.stat_captions[p_n])
            else:
                mod_num = '%s%s %s' % (vb_str, percent, self.resources.stat_captions[p_n])
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
