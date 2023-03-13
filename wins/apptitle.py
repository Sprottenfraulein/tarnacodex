# game title window
import pygame
import settings
import random
from library import textinput, pydraw, maths, calc2darray
from components import maze, pc, charsheet, ui, skill, treasure, dbrequests, gamesave, debuff


class AppTitle:
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

        self.win_w, self.win_h = pygame_settings.screen_res
        self.offset_x = 0
        self.offset_y = 0

        self.pc = None
        self.common_stash = None
        self.common_stash_gold = None

        self.chars = None
        self.chapters = None
        self.savegames = None
        self.save_ui_blocks_list = []
        self.char_desc_string = None
        self.char_title_string = None
        self.char_img_panel = None
        self.chapter_img_panel = None
        self.chapter_title_string = None
        self.chapter_desc_string = None
        self.curr_chapter_img_panel = None
        self.curr_chapter_title_string = None
        self.curr_chapter_desc_string = None
        self.curr_chapter_stage_string = None
        self.curr_chapter_continue_expence = None
        self.curr_char_panel = None
        self.curr_char_name_string = None
        self.curr_char_type_string = None
        self.field_charname_edit = None
        self.bttn_continue_chapter = None
        self.bttn_hardcore = None
        self.bttn_char_delete = None
        self.char_selection = 0
        self.chapter_selection = 0
        self.save_selection = None
        self.create_elements(log=True)

        # creating dedicated schedule
        self.schedule_man.new_schedule('realm_tasks')

        self.logo = pygame.image.load('./res/tilesets/logo.png').convert()
        self.logo.set_colorkey((0,0,0))
        self.logo_w, self.logo_h = self.logo.get_size()

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

        self.controls_enabled = True

        self.render()

    def event_check(self, event, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.win_ui.key_focus is not None:
                if self.win_ui.key_focus.page is not None and self.win_ui.page not in self.win_ui.key_focus.page:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.win_ui.key_focus.mode = 0

                    self.win_ui.key_focus.do_sound(2)

                    self.win_ui.key_focus = None
                    return
                self.win_ui.key_focus.text_obj.caption = textinput.do_edit(event.unicode,
                                                                           self.win_ui.key_focus.text_obj.caption,
                                                                           self.win_ui.key_focus.maxlen)

                self.win_ui.key_focus.do_sound(1)

                self.win_ui.key_focus.render_all()
                self.win_ui.updated = True
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item is not None:
                return
            for i in range(len(self.win_ui.interactives) - 1, -1, -1):
                if self.win_ui.interactives[i].rendered_rect.collidepoint(self.mouse_pointer.xy):
                    if not self.win_ui.interactives[i].mouse_over:
                        self.win_ui.interactives[i].mouse_over = True
                else:
                    if self.win_ui.interactives[i].mouse_over:
                        self.win_ui.interactives[i].mouse_over = False
                        if self.win_ui.interactives[i].popup_active:
                            self.win_ui.interactives[i].popup_active = False
                            self.win_ui.interactives.remove(self.win_ui.interactives[i].popup_win)
                            self.win_ui.dated = True

        if self.wins_dict['context'] in self.active_wins:
            self.active_wins.remove(self.wins_dict['context'])
        # return True if interaction was made to prevent other windows from responding to this event
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None or not self.controls_enabled:
            for inter in self.win_ui.interactives:
                inter.release(1)
                inter.release(3)
            self.win_ui.updated = True
            return
        element, m_bttn, mb_event = inter_click

        # PAGE 0
        if element.id in ('input_name',) and m_bttn == 1 and mb_event == 'down':
            self.win_ui.key_focus = element
        elif element.id == 'bttn_hardcore' and m_bttn == 1 and element.mode == 1 and mb_event == 'up' and element.sw_op == True:
            self.wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': 'You have chosen Hardcore mode. $n $n '
                        '* Your character death will be permanent. $n '
                        '* Auto-usage of supplies placed on Hotbar disabled.',
                'bttn_cancel': 'OK'
            }
            self.wins_dict['dialogue'].launch(pc)
        elif element.id == 'new_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            if len(self.savegames) < 10 or (len(self.savegames) == 10 and None in self.savegames):
                self.win_ui.page = 1
                self.char_name_rnd()
                self.bttn_hardcore.mode = 0
                self.bttn_hardcore.render()
        elif element.id == 'delete_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            if self.save_selection is not None:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'Are you sure you want to delete chosen character?',
                    'bttn_cancel': 'CANCEL',
                    'bttn_ok': 'OK'
                }
                self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'char_delete', [])
                self.wins_dict['dialogue'].launch(pc)
            else:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'Choose a character you want to delete!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
        elif element.id == 'exit' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            exit()

        # PAGE 1
        # TAGGED RADIO BUTTON SWITCH GROUP
        if self.win_ui.key_focus is not None and element.id != 'input_name':
            self.win_ui.key_focus = None
            self.field_charname_edit.mode = 0

        if 'charswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down' and element.mode == 0:
                for inter in self.win_ui.interactives:
                    if inter == element:
                        if inter.text_obj.color != self.resources.colors['sun']:
                            inter.text_obj.color = self.resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()
                            self.char_selection = inter.id
                            self.char_info_update()
                    elif 'charswitch' in inter.tags:
                        inter.mode = 0
                        if inter.text_obj.color != self.resources.colors['fnt_muted']:
                            inter.text_obj.color = self.resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True
        # TAGGED RADIO BUTTON SWITCH GROUP
        if 'chapterswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down' and element.mode == 0:
                for inter in self.win_ui.interactives:
                    if inter == element:
                        if inter.text_obj.color != self.resources.colors['sun']:
                            inter.text_obj.color = self.resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()
                            self.chapter_selection = inter.id
                            self.chapter_info_update()
                    elif 'chapterswitch' in inter.tags:
                        inter.mode = 0
                        if inter.text_obj.color != self.resources.colors['fnt_muted']:
                            inter.text_obj.color = self.resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True
        # TAGGED RADIO BUTTON SWITCH GROUP
        if 'saveswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down':
                for inter in self.win_ui.interactives:
                    if inter == element and element.mode == 0:
                        self.save_selection = inter.id
                        self.bttn_char_delete.page.add(0)
                    elif 'saveswitch' in inter.tags:
                        inter.mode = 0
                        inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True

        elif element.id == 'rnd_name' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.char_name_rnd()
            self.win_ui.key_focus = None

        elif element.id == 'back' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            if self.win_ui.page == 2:
                self.char_save(self.pc, None)
                self.clear_quick_view()
                self.create_savegames()
            self.win_ui.page = 0
            self.win_ui.key_focus = None

            self.save_selection = None
            self.bttn_char_delete.page.clear()
            for sb in self.save_ui_blocks_list:
                if sb is None:
                    continue
                sb[0].mode = 0

        elif element.id == 'new_char_begin' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None

            if self.chapters[self.chapter_selection]['lvl'] > 1:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'This chapter is for characters with level %s and higher!' % (self.chapters[self.chapter_selection]['lvl']),
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            else:

                self.char_create()

                self.controls_enabled = False

                self.pc.char_sheet.calc_stats()
                self.pc.char_sheet.hp_get(100, percent=True)
                self.pc.char_sheet.mp_get(100, percent=True)
                self.pc.char_sheet.food_get(100, percent=True)

                self.pc.location = [self.chapters[self.chapter_selection], 0]

                self.location_change(self.pc, 'up', launch=True, new_chapter=True)

        elif element.id == 'begin_chapter' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            if self.pc is None:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have to load a character first!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            elif self.pc.hardcore_char == 2:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Hardcore character attention',
                    'text': 'Unfortunately, your character has been slain! $n During the creation process you have chosen game mode featuring permanent character death. $n To play the game, create another character!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            elif self.pc.location is None:
                if self.chapter_level_check(self.pc, self.chapters[self.chapter_selection]):
                    self.chapter_begin()
                else:
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': '%s has to be level %s to start %s!' % (
                            self.pc.char_sheet.name.capitalize(),
                            self.chapters[self.chapter_selection]['lvl'],
                            self.chapters[self.chapter_selection]['label']
                        ),
                        'bttn_cancel': 'OK'
                    }
                    self.wins_dict['dialogue'].launch(pc)
            else:
                if not self.chapter_level_check(self.pc, self.chapters[self.chapter_selection]):
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': '%s has to be level %s to start %s!' % (
                            self.pc.char_sheet.name.capitalize(),
                            self.chapters[self.chapter_selection]['lvl'],
                            self.chapters[self.chapter_selection]['label']
                        ),
                        'bttn_cancel': 'OK'
                    }
                    self.wins_dict['dialogue'].launch(pc)
                else:
                    self.win_ui.key_focus = None
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': 'All existing chapter progress will be erased! $n Continue?',
                        'bttn_cancel': 'NO',
                        'bttn_ok': 'YES'
                    }
                    self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'chapter_begin', ())
                    self.wins_dict['dialogue'].launch(pc)

        elif element.id == 'continue_chapter' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            if self.pc is None:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have to load a character first!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            elif self.pc.hardcore_char == 2:
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Hardcore character attention',
                    'text': 'Unfortunately, your character has been slain! $n During the creation process '
                            'you have chosen game mode featuring permanent character death. $n '
                            'To play the game, create another character!',
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            elif (self.pc.char_sheet.gold_coins + self.wins_dict['stash'].common_stash_gold) < self.get_continue_expence(self.pc):
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'PAYMENT REQUIRED!',
                    'text': "To resume from the last visited stage, you have to pay Cosmologists' guild "
                            "for warping services. Unfortunately you have no %s "
                            "gold coins to cover the expences." % self.get_continue_expence(self.pc),
                    'bttn_cancel': 'OK'
                }
                self.wins_dict['dialogue'].launch(pc)
            else:
                expence = self.get_continue_expence(self.pc)
                self.wins_dict['dialogue'].dialogue_elements = {
                    'header': 'PAYMENT REQUIRED!',
                    'text': "To resume from the last visited stage, you have to pay Cosmologists' guild "
                            "for warping services. You are to be charged %s gold coins. $n Is this OK?" % expence,
                    'bttn_cancel': 'NO',
                    'bttn_ok': 'YES'
                }
                self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'chapter_continue', (expence,))
                self.wins_dict['dialogue'].launch(pc)

        elif element.id == 'load' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            self.char_load()

        # PAGE 2 quickview buttons
        if 'quick_view' in element.tags and m_bttn == 1 and element.mode == 0 and mb_event == 'down':
            if element.id == 'quick_inv':
                if not self.wins_dict['inventory'] in self.active_wins:
                    self.wins_dict['inventory'].updated = True
                    self.active_wins.insert(0, self.wins_dict['inventory'])
            elif element.id == 'quick_stash':
                if self.pc.hardcore_char == 2:
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': 'Common stash is unavailable because your Hardcore Character has been killed. $n '
                                'Please, create a new hardcore character to access the stash.',
                        'bttn_cancel': 'OK'
                    }
                    self.wins_dict['dialogue'].launch(pc)
                    return
                elif not self.wins_dict['stash'] in self.active_wins:
                    self.wins_dict['stash'].updated = True
                    self.active_wins.insert(0, self.wins_dict['stash'])
            elif element.id == 'quick_skb':
                if not self.wins_dict['skillbook'] in self.active_wins:
                    self.wins_dict['skillbook'].updated = True
                    self.active_wins.insert(0, self.wins_dict['skillbook'])
            elif element.id == 'quick_hot':
                if not self.wins_dict['hotbar'] in self.active_wins:
                    self.wins_dict['hotbar'].updated = True
                    self.active_wins.insert(0, self.wins_dict['hotbar'])
            elif element.id == 'quick_miss':
                if not self.wins_dict['tasks'] in self.active_wins:
                    self.wins_dict['tasks'].launch(self.pc)
                    self.active_wins.insert(0, self.wins_dict['tasks'])
            elif element.id == 'quick_char':
                if not self.wins_dict['charstats'] in self.active_wins:
                    self.wins_dict['charstats'].launch(self.pc)
                    self.active_wins.insert(0, self.wins_dict['charstats'])

        elif 'quick_view' in element.tags and m_bttn == 1 and element.mode == 1 and element.sw_op is False and mb_event == 'up':
            if element.id == 'quick_inv':
                if self.wins_dict['inventory'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['inventory'])
            elif element.id == 'quick_stash':
                if self.wins_dict['stash'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['stash'])
            elif element.id == 'quick_skb':
                if self.wins_dict['skillbook'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['skillbook'])
                    self.pc.char_sheet.itemlist_cleanall_skills(self.wins_dict, self.pc)
            elif element.id == 'quick_hot':
                if self.wins_dict['hotbar'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['hotbar'])
            elif element.id == 'quick_miss':
                if self.wins_dict['tasks'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['tasks'])
                    self.wins_dict['tasks'].end()
            elif element.id == 'quick_char':
                if self.wins_dict['charstats'] in self.active_wins:
                    self.active_wins.remove(self.wins_dict['charstats'])
                    self.wins_dict['charstats'].end()

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.chars = dbrequests.chars_get_all(self.db.cursor)
        self.chapters = dbrequests.chapters_get_all(self.db.cursor)

        self.win_ui.interactives.clear()
        self.win_ui.decoratives.clear()

        self.char_selection = 0
        self.chapter_selection = 0
        self.save_selection = None

        menu_btn_h = 40
        menu_btn_w = 256

        # SAVED GAMES
        self.create_savegames()

        # MAIN MENU
        main_menu = [
            self.win_ui.button_add('new_char', caption='New Character', size=(menu_btn_w, menu_btn_h), cap_font='large',
                                   cap_size=16,cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
            self.win_ui.button_add('exit', caption='Exit', size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                   cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
        ]
        self.bttn_char_delete = self.win_ui.button_add('delete_char', caption='Delete Character', size=(menu_btn_w, menu_btn_h),
                                                    cap_font='large', cap_size=16,cap_color='fnt_muted',
                                                    sounds=self.win_ui.snd_packs['button'])
        main_menu.insert(-1, self.bttn_char_delete)

        for i in range(0, len(main_menu)):
            main_menu[i].tags = ['lightup']
            main_menu[i].page = (0,)
            main_menu[i].rendered_rect.left = round(menu_btn_h)
            main_menu[i].rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i - 120

        self.bttn_char_delete.page = set()

        main_menu[-1].rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # CHARACTER CHOICE
        char_menu = []
        for i in range(0, min(5, len(self.chars))):
            new_bttn = self.win_ui.button_add(i, caption=self.chars[i]['label'].capitalize(),
                                              size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                              cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                              switch=True, mode=0)
            new_bttn.tags = ['lightup', 'charswitch']
            new_bttn.page = (1,)
            new_bttn.rendered_rect.left = round(menu_btn_h)
            new_bttn.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                        menu_btn_h * 1.2) * i - 120
            char_menu.append(new_bttn)

        char_menu[0].mode = 1
        char_menu[0].text_obj.color = self.win_ui.resources.colors['sun']
        char_menu[0].text_obj.render()
        char_menu[0].render()

        bttn_begin = self.win_ui.button_add('new_char_begin', caption='Start', size=(menu_btn_w, menu_btn_h),
                                            cap_font='large', cap_size = 16,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(1,))
        bttn_back = self.win_ui.button_add('back', caption='Main menu', size=(menu_btn_w, menu_btn_h),
                                           cap_font='large', cap_size=16,
                                           cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(1,2))

        bttn_back.rendered_rect.left = round(menu_btn_h)
        bttn_back.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7

        bttn_begin.rendered_rect.right = round(self.pygame_settings.screen_res[0] - menu_btn_h)
        bttn_begin.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # CHAR NAME INPUT FIELD
        self.field_charname_edit = self.win_ui.edit_add('input_name', (0, 0), sounds=self.win_ui.snd_packs['text_input'], cap_font='def_normal',
                                                        size=(round(menu_btn_w * 0.6), round(menu_btn_h * 0.7)), h_align='center', page=(1,))
        self.field_charname_edit.rendered_rect.centerx = round(menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        self.field_charname_edit.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7

        bttn_texture = self.win_ui.random_texture((round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)), 'red_glass')
        rnd_img = self.win_ui.tilesets.get_image('interface', (24,24), (1,))[0]
        bttn_img_up = pydraw.square((0, 0), (round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                                        (self.win_ui.resources.colors['gray_light'],
                                         self.win_ui.resources.colors['gray_dark'],
                                         self.win_ui.resources.colors['gray_mid'],
                                         self.win_ui.resources.colors['gray_darker']),
                                        sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                        sq_image=bttn_texture)
        bttn_img_down = pydraw.square((0, 0), (round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                                    (self.win_ui.resources.colors['gray_light'],
                                     self.win_ui.resources.colors['gray_dark'],
                                     self.win_ui.resources.colors['gray_mid'],
                                     self.win_ui.resources.colors['gray_darker']),
                                    sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                    sq_image=bttn_texture)
        bttn_img_up.blit(rnd_img, (2, 2))
        bttn_img_down.blit(rnd_img, (2, 2))
        rnd_name_bttn = self.win_ui.button_add('rnd_name', caption=None, size=(round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                               cap_font='def_bold', cap_size=24, cap_color='fnt_celeb',
                               sounds=self.win_ui.snd_packs['button'], images=(bttn_img_up, bttn_img_down), page=(1,))
        rnd_name_bttn.rendered_rect.left = self.field_charname_edit.rendered_rect.right
        rnd_name_bttn.rendered_rect.top = self.field_charname_edit.rendered_rect.top
        self.win_ui.interactives.append(rnd_name_bttn)

        # CHAPTERS CHOICE
        chapter_menu = []
        for i in range(0, min(5, len(self.chapters))):
            new_bttn = self.win_ui.button_add(i, caption=self.chapters[i]['label'],
                                              size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                              cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                              switch=True, mode=0)
            new_bttn.tags = ['lightup', 'chapterswitch']
            new_bttn.page = (1,2)
            new_bttn.rendered_rect.right = round(self.pygame_settings.screen_res[0] - menu_btn_h)
            new_bttn.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * i - 120
            chapter_menu.append(new_bttn)

        chapter_menu[0].mode = 1
        chapter_menu[0].text_obj.color = self.win_ui.resources.colors['sun']
        chapter_menu[0].text_obj.render()
        chapter_menu[0].render()

        char_string = \
            self.win_ui.text_add('char_string',
            (menu_btn_h, round(self.pygame_settings.screen_res[1] / 2 - menu_btn_h*1.5 - 120)),
            caption='Choose a character:',
            h_align='center', v_align='top', size=char_menu[0].size, cap_color='fnt_celeb',
            cap_font='large', cap_size=14, page=(1,))
        self.win_ui.decoratives.append(char_string)

        chapter_string = \
            self.win_ui.text_add('char_string',
            (self.pygame_settings.screen_res[0] - menu_btn_h - menu_btn_w,
            round(self.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5 - 120)),
            caption='Choose a chapter:',
            h_align='center', v_align='top', size=char_menu[0].size,
            cap_color='fnt_celeb',
            cap_font='large', cap_size=14, page=(1,2))
        self.win_ui.decoratives.append(chapter_string)

        char_imgs = self.win_ui.tilesets.get_image('char_portraits', (60,60), (0,))
        self.char_img_panel = self.win_ui.panel_add('char_img_panel', (
            menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            char_menu[0].rendered_rect.top
        ), (120, 120), images=char_imgs, page=(1,), img_stretch=True)
        self.win_ui.decoratives.append(self.char_img_panel)

        self.char_title_string = \
            self.win_ui.text_add('char_title',
                                 (0, chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption="%s's character traits:" % self.chars[self.char_selection]['label'].capitalize(),
                                 h_align='center', v_align='top', size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(1,))
        self.char_title_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.char_title_string)

        self.char_desc_string = \
            self.win_ui.text_add('char_desc', (menu_btn_h * 2 + menu_btn_w, round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chars[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ), cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(1,))
        self.win_ui.decoratives.append(self.char_desc_string)

        input_invite_string = \
            self.win_ui.text_add('input_invite',
                                 (0, round(self.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7 - 48),
                                 caption="Enter hero's name:",
                                 h_align='center', v_align='top',
                                 size=(280, 32),
                                 cap_color='fnt_celeb',
                                 cap_font='large', cap_size=14, page=(1,))
        input_invite_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(input_invite_string)

        hardcore_char_checkbox_string = \
            self.win_ui.text_add(
                'hc_checkbox_string',
                (self.pygame_settings.screen_res[0] - (menu_btn_h * 2 + menu_btn_w) -
                 (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64) + 32 + 8, 0),
                caption="Hardcore character", h_align='left', v_align='top', size=(280, 20), cap_color='fnt_celeb',
                cap_font='large', cap_size=14, page=(1,))
        hardcore_char_checkbox_string.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7
        self.win_ui.decoratives.append(hardcore_char_checkbox_string)

        hc_img = self.win_ui.tilesets.get_image('interface', (24, 24), (2,))[0]
        hc_bttn_img_up = pydraw.square((0, 0), (round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                                    (self.win_ui.resources.colors['gray_light'],
                                     self.win_ui.resources.colors['gray_dark'],
                                     self.win_ui.resources.colors['gray_darker'],
                                     self.win_ui.resources.colors['bg']),
                                    sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=True)
        hc_bttn_img_down = pydraw.square((0, 0), (round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                                      (self.win_ui.resources.colors['gray_light'],
                                       self.win_ui.resources.colors['gray_dark'],
                                       self.win_ui.resources.colors['gray_darker'],
                                       self.win_ui.resources.colors['bg']),
                                      sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=True)
        hc_bttn_img_down.blit(hc_img, (2, 2))
        self.bttn_hardcore = self.win_ui.button_add('bttn_hardcore', caption=None,
                                               size=(round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                                                    images=(hc_bttn_img_up, hc_bttn_img_down),
                                               sounds=self.win_ui.snd_packs['button'], switch=True, page=(1,))
        self.bttn_hardcore.rendered_rect.left = (self.pygame_settings.screen_res[0] - (menu_btn_h * 2 + menu_btn_w) -
                 (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64))
        self.bttn_hardcore.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7
        self.win_ui.interactives.append(self.bttn_hardcore)

        chapter_imgs = self.win_ui.tilesets.get_image('chapter_thumbs', (60, 60), (0,))
        self.chapter_img_panel = self.win_ui.panel_add('chapter_img_panel', (
            self.pygame_settings.screen_res[0] / 2 + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            chapter_menu[0].rendered_rect.top
        ), (120, 120), images=chapter_imgs, page=(1,2), img_stretch=True)
        self.win_ui.decoratives.append(self.chapter_img_panel)

        self.chapter_title_string = \
            self.win_ui.text_add('chapter_title',
                                 (0,chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption='%s briefing:' % self.chapters[0]['label'], h_align='center', v_align='top',
                                 size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(1, 2))
        self.chapter_title_string.rendered_rect.centerx = self.pygame_settings.screen_res[0] / 2 + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.chapter_title_string)

        self.chapter_desc_string = \
            self.win_ui.text_add('chapter_desc',
                                 (self.pygame_settings.screen_res[0] - (menu_btn_h * 2 + menu_btn_w) - (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64),
                                  round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chapters[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ),
                                 cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(1,2))
        self.win_ui.decoratives.append(self.chapter_desc_string)

        # PAGE 2
        self.curr_chapter_img_panel = self.win_ui.panel_add('chapter_img_panel', (
            menu_btn_h + menu_btn_w + (
                        self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            char_menu[0].rendered_rect.top
        ), (120, 120), images=chapter_imgs, page=(2,), img_stretch=True)
        self.win_ui.decoratives.append(self.curr_chapter_img_panel)

        self.curr_chapter_title_string = \
            self.win_ui.text_add('chapter_title',
                                 (0, chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption='%s briefing:' % self.chapters[0]['label'], h_align='center', v_align='top',
                                 size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(2,))
        self.curr_chapter_title_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.curr_chapter_title_string)

        self.curr_chapter_desc_string = \
            self.win_ui.text_add('chapter_desc',
                                 (menu_btn_h * 2 + menu_btn_w, round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chapters[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ),
                                 cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_chapter_desc_string)

        self.curr_chapter_stage_string = \
            self.win_ui.text_add('chapter_stage',
                                 (0, round(self.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7 - menu_btn_h * 2.2),
                                 caption='chapter $n stage', h_align='center', v_align='top',
                                 size=(menu_btn_w, 48),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(2,))
        self.curr_chapter_stage_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (
                    self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.curr_chapter_stage_string)

        self.curr_chapter_continue_expence = \
            self.win_ui.text_add('chapter_stage',
                                 (0, round(self.pygame_settings.screen_res[1] / 2) + (
                                         menu_btn_h * 1.2) * 7 - menu_btn_h * 1.1),
                                 caption='price', h_align='center', v_align='top',
                                 size=(menu_btn_w, 48),
                                 cap_color='bright_gold', cap_font='large', cap_size=12, page=(2,))
        self.curr_chapter_continue_expence.rendered_rect.centerx = menu_btn_h + menu_btn_w + (
                self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.curr_chapter_continue_expence)

        bttn_begin_chapter = self.win_ui.button_add('begin_chapter', caption='Start New Chapter', size=(menu_btn_w, menu_btn_h),
                                            cap_font='large', cap_size=16,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(2,))
        bttn_begin_chapter.rendered_rect.right = round(self.pygame_settings.screen_res[0] - menu_btn_h)
        bttn_begin_chapter.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7

        rnd_texture = self.win_ui.random_texture((menu_btn_w, menu_btn_h), 'black_rock')
        images = (
            pydraw.square((0, 0), (menu_btn_w, menu_btn_h),
                          (self.resources.colors['bright_gold'],
                           self.resources.colors['fnt_muted'],
                           self.resources.colors['gray_mid'],
                           self.resources.colors['black']),
                          sq_outsize=2, sq_bsize=2, sq_ldir=0, sq_fill=False,
                          sq_image=rnd_texture),
            pydraw.square((0, 0), (menu_btn_w, menu_btn_h),
                          (self.resources.colors['bright_gold'],
                           self.resources.colors['fnt_muted'],
                           self.resources.colors['gray_mid'],
                           self.resources.colors['black']),
                          sq_outsize=2, sq_bsize=2, sq_ldir=2, sq_fill=False,
                          sq_image=rnd_texture),
        )
        self.bttn_continue_chapter = self.win_ui.button_add('continue_chapter', caption='Resume Chapter',
                                                    size=(menu_btn_w, menu_btn_h), images=images,
                                                    cap_font='large', cap_size=16,
                                                    cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                                    page=(2,))
        self.bttn_continue_chapter.rendered_rect.centerx = round(menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        self.bttn_continue_chapter.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7

        curr_chapter_string = \
            self.win_ui.text_add('chapter_string',
                                 (menu_btn_h, round(self.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5 - 120)),
                                 caption='Current Chapter:',
                                 h_align='center', v_align='top', size=char_menu[0].size, cap_color='fnt_celeb',
                                 cap_font='large', cap_size=14, page=(2,))
        curr_chapter_string.rendered_rect.centerx = round(
            menu_btn_h + menu_btn_w + (self.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        self.win_ui.decoratives.append(curr_chapter_string)

        # QUICK VIEW character windows buttons
        quick_btn_w = 60
        quick_btn_h = 28
        bttns_per_row = 2
        bttn_texture = self.win_ui.random_texture((quick_btn_w, quick_btn_h), 'red_glass')
        bttn_icons = (
            self.win_ui.tilesets.get_image('interface', (24, 24,), (20, 21)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (22, 23)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (24, 25)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (30, 31)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (26, 27)),
            self.win_ui.tilesets.get_image('dung_chests', (24, 24,), (7, 6)),
        )
        bttn_img_list = []
        for i in range(0, 6):
            bttn_up_img = pydraw.square((0, 0), (quick_btn_w, quick_btn_h),
                                        (self.win_ui.resources.colors['gray_light'],
                                         self.win_ui.resources.colors['gray_dark'],
                                         self.win_ui.resources.colors['gray_mid'],
                                         self.win_ui.resources.colors['gray_darker']),
                                        sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                        sq_image=bttn_texture)
            bttn_up_img.blit(bttn_icons[i][0], (round(quick_btn_w / 2 - 12), round(quick_btn_h / 2 - 12)))
            bttn_down_img = pydraw.square((0, 0), (quick_btn_w, quick_btn_h),
                                          (self.win_ui.resources.colors['gray_light'],
                                           self.win_ui.resources.colors['gray_dark'],
                                           self.win_ui.resources.colors['gray_mid'],
                                           self.win_ui.resources.colors['gray_darker']),
                                          sq_outsize=1, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                          sq_image=bttn_texture)
            bttn_down_img.blit(bttn_icons[i][1], (round(quick_btn_w / 2 - 12), round(quick_btn_h / 2 - 12)))

            bttn_img_list.append((
                bttn_up_img, bttn_down_img
            ))
        char_quick_menu = (
            self.win_ui.button_add('quick_inv', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[0], switch=True),
            self.win_ui.button_add('quick_skb', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[1], switch=True),
            self.win_ui.button_add('quick_hot', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[2], switch=True),
            self.win_ui.button_add('quick_miss', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[3], switch=True),
            self.win_ui.button_add('quick_char', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[4], switch=True),
            self.win_ui.button_add('quick_stash', size=(quick_btn_w, quick_btn_h),
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[5], switch=True),
        )
        for i in range(0, len(char_quick_menu)):
            char_quick_menu[i].tags = ['quick_view']
            char_quick_menu[i].page = (2,)
            char_quick_menu[i].rendered_rect.left = menu_btn_h + menu_btn_w // 2 - quick_btn_w + (quick_btn_w * (i % bttns_per_row))
            char_quick_menu[i].rendered_rect.top = chapter_menu[0].rendered_rect.top + 120 + 8 + 64 + (quick_btn_h * (i // bttns_per_row))

        # loaded character info
        curr_char_string = \
            self.win_ui.text_add('char_string',
                                 (menu_btn_h, round(self.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5 - 120)),
                                 caption='Loaded Character:',
                                 h_align='center', v_align='top', size=char_menu[0].size, cap_color='fnt_celeb',
                                 cap_font='large', cap_size=14, page=(2,))
        self.win_ui.decoratives.append(curr_char_string)

        curr_char_img = self.win_ui.tilesets.get_image('char_portraits', (60, 60), (0,))
        self.curr_char_panel = self.win_ui.panel_add('curr_char_panel', (menu_btn_h + menu_btn_w // 2 - 60,
                                                    char_menu[0].rendered_rect.top),
                                                (120, 120), images=curr_char_img, img_stretch=True, page=(2,))
        self.win_ui.decoratives.append(self.curr_char_panel)

        self.curr_char_name_string = \
            self.win_ui.text_add('char_name',
                                 (menu_btn_h + 56, char_menu[0].rendered_rect.top + 120 + 8),
                                 caption='char_name',
                                 h_align='center', v_align='top', size=(140, 14), cap_color='fnt_celeb',
                                 cap_font='def_bold', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_char_name_string)

        self.curr_char_type_string = \
            self.win_ui.text_add('char_type',
                                 (menu_btn_h + 56, char_menu[0].rendered_rect.top + 120 + 8 + 14),
                                 caption='char_type',
                                 h_align='center', v_align='top', size=(140, 14), cap_color='fnt_celeb',
                                 cap_font='def_normal', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_char_type_string)

        # all pages
        tag_string = self.win_ui.text_add('tag_string', (0, self.pygame_settings.screen_res[1] - 16),
                                          caption=settings.tag_string, h_align='left', v_align='bottom',
                                          size=(self.pygame_settings.screen_res[0] // 4, 16), cap_color='sun')

        self.win_ui.interactives.extend(char_quick_menu)
        self.win_ui.interactives.append(self.bttn_continue_chapter)
        self.win_ui.interactives.append(bttn_begin_chapter)
        self.win_ui.interactives.append(bttn_begin)
        self.win_ui.interactives.append(bttn_back)
        self.win_ui.interactives.extend(main_menu)
        self.win_ui.interactives.extend(char_menu)
        self.win_ui.interactives.extend(chapter_menu)
        self.win_ui.interactives.append(self.field_charname_edit)
        self.win_ui.interactives.append(tag_string)

        self.char_name_rnd()

    def create_savegames(self):
        for save_block in self.save_ui_blocks_list:
            if save_block is None:
                continue
            self.win_ui.interactives.remove(save_block[0])
            for i in save_block[1:]:
                try:
                    self.win_ui.decoratives.remove(i)
                except ValueError:
                    pass

        self.save_ui_blocks_list.clear()

        self.savegames = dbrequests.savegames_get_all(self.db.cursor)

        menu_btn_h = 40
        menu_btn_w = 256

        saves_left = menu_btn_h + menu_btn_w + menu_btn_h
        saves_top = self.win_h / 2 - menu_btn_h // 2 - 120
        save_w = 160
        save_h = 210
        saves_per_row = 5
        saves_total = 10
        save_texture = self.win_ui.random_texture((save_w, save_h), 'black_rock')
        save_texture_hardcore = self.win_ui.random_texture((save_w, save_h), 'red_glass')

        bttn_img_up = pydraw.square((0, 0), (save_w, save_h),
                                    (self.win_ui.resources.colors['gray_light'],
                                     self.win_ui.resources.colors['gray_dark'],
                                     (0, 254, 0),
                                     self.win_ui.resources.colors['black']),
                                    sq_outsize=2, sq_bsize=2, sq_ldir=0, sq_fill=True)
        bttn_img_down = pydraw.square((0, 0), (save_w, save_h),
                                      (self.win_ui.resources.colors['gray_light'],
                                       self.win_ui.resources.colors['gray_dark'],
                                       (0, 254, 0),
                                       self.win_ui.resources.colors['sun']),
                                      sq_outsize=2, sq_bsize=2, sq_ldir=0, sq_fill=True)
        for i in range(0, min(saves_total, len(self.savegames))):
            save_x = saves_left + (save_w + 8) * (i % saves_per_row)
            save_y = saves_top + (save_h + 8) * (i // saves_per_row)

            if self.savegames[i]['hardcore_char'] == 2:
                char_img = self.win_ui.tilesets.get_image('char_portraits_archive',
                                                              (60, 60), (self.savegames[i]['char_image_index'],))
            else:
                char_img = self.win_ui.tilesets.get_image('char_portraits',
                                                              (60, 60), (self.savegames[i]['char_image_index'],))

            char_panel = self.win_ui.panel_add(i, (save_x + 20, save_y + 12), (120, 120), images=char_img,
                                               img_stretch=True, page=(0,))
            self.win_ui.decoratives.append(char_panel)

            if self.savegames[i]['hardcore_char'] != 0:
                save_font_color = 'sun'
            else:
                save_font_color = 'fnt_celeb'

            char_name_string = \
                self.win_ui.text_add('char_name',
                                     (save_x + 4, save_y + 8 + 120 + 8),
                                     caption='%s' % self.savegames[i]['char_name'],
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color=save_font_color,
                                     cap_font='def_bold', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(char_name_string)

            char_type_string = \
                self.win_ui.text_add('char_type',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14),
                                     caption='%s, lv.%s' % (
                                     self.savegames[i]['char_type'].capitalize(), self.savegames[i]['char_level']),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color=save_font_color,
                                     cap_font='def_normal', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(char_type_string)

            chapter_string = \
                self.win_ui.text_add('chapter_label',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14 + 14),
                                     caption=self.savegames[i]['chapter_label'] + ' %s:' % (
                                     self.savegames[i]['stage_index'] + 1,),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color=save_font_color,
                                     cap_font='def_normal', cap_size=24, page=(0,))
            if self.savegames[i]['chapter_label'] != '-':
                self.win_ui.decoratives.append(chapter_string)

            stage_string = \
                self.win_ui.text_add('stage_string',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14 + 14 + 14),
                                     caption='%s' % (self.savegames[i]['stage_label'],),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color=save_font_color,
                                     cap_font='def_normal', cap_size=24, page=(0,))
            if self.savegames[i]['chapter_label'] != '-':
                self.win_ui.decoratives.append(stage_string)

            if self.savegames[i]['hardcore_char'] != 0:
                save_panel = self.win_ui.panel_add(i, (save_x, save_y), (save_w, save_h), images=(save_texture_hardcore,),
                                                   page=(0,))
            else:
                save_panel = self.win_ui.panel_add(i, (save_x, save_y), (save_w, save_h), images=(save_texture,), page=(0,))
            self.win_ui.decoratives.append(save_panel)

            save_bttn = self.win_ui.button_add(i, xy=(save_x, save_y), size=(save_w, save_h),
                                               images=(bttn_img_up, bttn_img_down),
                                               sounds=self.win_ui.snd_packs['button'], switch=True, page=(0,))
            save_bttn.tags = ('saveswitch',)
            save_bttn.rendered_button.set_colorkey((0, 254, 0))
            self.win_ui.interactives.append(save_bttn)
            self.save_ui_blocks_list.append((save_bttn, char_panel, save_panel, stage_string,
                                             chapter_string, char_type_string, char_name_string))

            if self.pc is not None and self.savegames[i]['char_id'] == self.pc.char_sheet.id:
                self.save_selection = i

        if len(self.savegames) > 0:
            bttn_load = self.win_ui.button_add('load', caption='Load', size=(menu_btn_w, menu_btn_h),
                                               cap_font='large', cap_size=16,
                                               cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(0,))
            bttn_load.rendered_rect.right = round(self.pygame_settings.screen_res[0] - menu_btn_h)
            bttn_load.rendered_rect.centery = round(self.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7
            self.win_ui.interactives.append(bttn_load)

    def location_change(self, pc, entry, launch=False, new_chapter=False):
        debuff.DeBuff(dbrequests.de_buff_get_by_id_with_mods(self.db.cursor, 4, self.resources.fate_rnd),
                      self.pc.char_sheet.de_buffs)

        self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, self.wins_dict['overlay'],
                                                          'fade_out', (20, None))
        self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['app_title'],
                                                          'location_update', (pc, entry, launch))
        if not new_chapter:
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['overlay'], 'fade_in',
                                                         (20, None))
        else:
            text_list, image_list = dbrequests.chapter_demo_get(self.db.cursor, pc.location[0]['chapter_id'], 'intro')
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['demos'], 'demo_run',
                                                              (pc, text_list, image_list, False))
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['overlay'], 'fade_in',
                                                              (20, None))

    def location_update(self, pc, entry, launch=False):
        if not launch:
            self.maze_save(pc, self.wins_dict['realm'].maze)
        # dbrequests.chapter_progress_set(self.db, pc.char_sheet.id, self.wins_dict['realm'].maze.stage_index, 1, 1, 1, 1, 1, 1)

        self.wins_dict['realm'].maze = None
        l = maze.Maze(self.db, self.animations, self.win_ui.tilesets, self.pygame_settings.audio, pc, self.resources)

        for i in range(0, len(l.exits)):
            if l.exits[i].dest == entry:
                space_list = calc2darray.fill2d(l.flag_array, ('mov', 'obj', 'door', 'floor'),
                                                (l.exits[i].x_sq, l.exits[i].y_sq), (l.exits[i].x_sq, l.exits[i].y_sq),
                                                2, 5, r_max=5)
                pc.x_sq, pc.y_sq = space_list[-1]
                break
        pc.stage_entry = entry

        self.maze_save(pc, l)
        dbrequests.chapter_progress_set(self.db, pc.char_sheet.id, l.stage_index, 1, 1, 1, 1, 1, 1)
        # pc.tradepost_level = max(l.lvl, pc.tradepost_level)
        pc.tradepost_level = max(pc.char_sheet.level, pc.tradepost_level)
        self.char_save(pc, l)

        self.wins_dict['realm'].maze = l
        self.wins_dict['realm'].pc = pc

        if l.tradepost_update or launch:
            self.wins_dict['trade'].goods_generate(pc)
            self.wins_dict['trade'].updated = True
            l.tradepost_update = False
            self.wins_dict['realm'].spawn_realmtext('new_txt', "I would like to visit a Trading Post sometime soon.",
                                                    (0, 0), (0, -24), 'bright_gold', pc, None, 240, 'def_bold', 24)
            self.wins_dict['realm'].pygame_settings.audio.sound('news_bell')

        self.wins_dict['realm'].launch()
        if self.wins_dict['realm'] not in self.active_wins:
            self.active_wins.append(self.wins_dict['realm'])
        if self in self.active_wins:
            self.active_wins.remove(self)

        self.wins_dict['realm'].render_update()
        self.pc.char_sheet.missions_check(self.wins_dict, pc)

    def char_info_update(self):
        self.char_img_panel.images_update(self.win_ui.tilesets.get_image('char_portraits', (60,60), (self.char_selection,)))

        self.char_desc_string.text_obj.caption = self.chars[self.char_selection]['desc']
        self.char_desc_string.render_all()

        self.char_title_string.text_obj.caption = "%s's character traits:" % self.chars[self.char_selection]['label'].capitalize()
        self.char_title_string.render_all()

    def char_loaded_info_update(self):
        if self.pc.location is not None:
            self.curr_chapter_img_panel.images_update(
                self.win_ui.tilesets.get_image('chapter_thumbs', (60, 60), (self.pc.location[0]['chapter_image_index'],)))
            self.curr_chapter_title_string.text_obj.caption = '%s briefing:' % self.pc.location[0]['label']
            self.curr_chapter_title_string.render_all()
            self.curr_chapter_desc_string.text_obj.caption = self.pc.location[0]['desc']
            self.curr_chapter_desc_string.render_all()
            self.curr_chapter_stage_string.text_obj.caption = 'Stage %s: $n %s' % (
                self.pc.location[1] + 1, self.savegames[self.save_selection]['stage_label'])
            self.curr_chapter_continue_expence.text_obj.caption = '%s gold coins' % self.get_continue_expence(self.pc)
            self.curr_chapter_continue_expence.page = (2,)
            self.curr_chapter_continue_expence.render_all()
            self.curr_chapter_img_panel.page = (2,)
            self.curr_chapter_desc_string.page = (2,)
            self.curr_chapter_stage_string.page = (2,)
            self.bttn_continue_chapter.page = (2,)
            self.curr_chapter_stage_string.render_all()
        else:
            self.curr_chapter_img_panel.page = (-1,)
            self.curr_chapter_title_string.text_obj.caption = 'No chapter $n in progress!'
            self.curr_chapter_desc_string.page = (-1,)
            self.curr_chapter_stage_string.page = (-1,)
            self.bttn_continue_chapter.page = (-1,)
            self.curr_chapter_title_string.render_all()
            self.curr_chapter_continue_expence.page = (-1,)

        self.controls_enabled = True

        if self.pc.hardcore_char == 2:
            self.curr_char_panel.images_update(
                self.win_ui.tilesets.get_image('char_portraits_archive', (60, 60), (self.pc.char_portrait_index,)))
        else:
            self.curr_char_panel.images_update(
                self.win_ui.tilesets.get_image('char_portraits', (60, 60), (self.pc.char_portrait_index,)))

        self.curr_char_name_string.text_obj.caption = self.pc.char_sheet.name
        self.curr_char_name_string.render_all()
        self.curr_char_type_string.text_obj.caption = '%s, level %s' % (
            self.pc.char_sheet.type.capitalize(), self.pc.char_sheet.level)
        self.curr_char_type_string.render_all()

        if self.wins_dict['hotbar'].pc != self.pc:
            self.wins_dict['hotbar'].launch(self.pc)
        if self.wins_dict['inventory'].pc != self.pc:
            self.wins_dict['inventory'].launch(self.pc)
        if self.wins_dict['skillbook'].pc != self.pc:
            self.wins_dict['skillbook'].launch(self.pc)
        if self.wins_dict['stash'].pc != self.pc:
            self.wins_dict['stash'].launch(self.pc)
        if self.wins_dict['tasks'].pc != self.pc:
            self.wins_dict['tasks'].launch(self.pc)

        # self.location_change(pygame_settings, self.wins_dict, self.active_wins, p, 'up', launch=True)
        self.win_ui.page = 2
        self.win_ui.updated = True

    def chapter_level_check(self, pch, chapter):
        return chapter['lvl'] <= pch.char_sheet.level

    def chapter_info_update(self):
        self.chapter_img_panel.images_update(self.win_ui.tilesets.get_image('chapter_thumbs', (60, 60), (self.chapters[self.chapter_selection]['chapter_image_index'],)))

        self.chapter_desc_string.text_obj.caption = self.chapters[self.chapter_selection]['desc']
        self.chapter_desc_string.render_all()

        self.chapter_title_string.text_obj.caption = '%s briefing:' % self.chapters[self.chapter_selection]['label']
        self.chapter_title_string.render_all()

    def chapter_begin(self):
        self.controls_enabled = False

        self.pc.char_sheet.calc_stats()
        self.pc.char_sheet.hp_get(100, percent=True)
        self.pc.char_sheet.mp_get(100, percent=True)
        self.pc.char_sheet.food_get(100, percent=True)

        gamesave.chapter_wipe(self.db, self.pc)

        self.pc.location = [self.chapters[self.chapter_selection], 0]
        self.pc.stage_entry = 'up'

        self.clear_quick_view()

        self.location_change(self.pc, 'up', launch=True, new_chapter=True)

    def chapter_continue(self, expence):
        if self.pc.char_sheet.gold_coins >= expence:
            self.pc.char_sheet.gold_coins -= expence
        else:
            self.pc.char_sheet.gold_coins -= expence
            self.wins_dict['stash'].common_stash_gold += self.pc.char_sheet.gold_coins
            self.pc.char_sheet.gold_coins = 0
            self.wins_dict['stash'].updated = True
        self.win_ui.key_focus = None
        self.controls_enabled = False

        self.pygame_settings.audio.sound('cast_dispel')
        self.pygame_settings.audio.sound('coins_trade')

        self.pc.char_sheet.calc_stats()
        # self.pc.char_sheet.hp_get(100, percent=True)
        # self.pc.char_sheet.mp_get(100, percent=True)
        # self.pc.char_sheet.food_get(100, percent=True)

        self.clear_quick_view()

        self.location_change(self.pc, self.pc.stage_entry, launch=True)

    def get_continue_expence(self, pc):
        return round((100 + 10 * pc.location[1]) * (1 * (pc.char_sheet.level * (pc.char_sheet.level + 1) / 2)))

    def chapter_end(self, pc, chapter_dict):
        text_list, image_list = dbrequests.chapter_demo_get(self.db.cursor, chapter_dict['chapter_id'], 'ending')
        self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, self.wins_dict['overlay'], 'fade_out',
                                                     (20, None))
        self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['demos'], 'demo_run',
                                                     (pc, text_list, image_list, True))
        self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['overlay'], 'fade_in',
                                                     (20, None))

    def char_name_rnd(self):
        self.field_charname_edit.text_obj.caption = dbrequests.char_name_get_random(self.db.cursor)
        self.field_charname_edit.render_all()
        self.win_ui.updated = True

    def char_create(self):
        if self.field_charname_edit.text_obj.caption == '':
            self.char_name_rnd()

        valid_saves = [save for save in self.savegames if save is not None]
        if len(valid_saves) > 0:
            new_char_id = max([save['char_id'] for save in valid_saves]) + 1
        else:
            new_char_id = 0
        char_sheet = charsheet.CharSheet(self.db, new_char_id, chr_name=self.field_charname_edit.text_obj.caption,
                                         chr_type=self.chars[self.char_selection]['char_type'], chr_level=1)

        anim = 'anthro_champion'
        if char_sheet.type == 'kingslayer':
            anim = 'anthro_kingslayer'
        elif char_sheet.type == 'cosmologist':
            anim = 'anthro_cosmologist'

        p = pc.PC(0, 0, None, self.animations.get_animation(anim), char_sheet, self.bttn_hardcore.mode, state=0)
        p.char_portrait_index = self.char_selection

        initial_char_stats = dbrequests.char_params_get(self.db.cursor, 'characters', p.char_sheet.type)
        default_skills = dbrequests.skill_defaults_get(self.db.cursor, initial_char_stats['character_id'])

        p.char_sheet.hotbar[-2] = skill.Skill(default_skills[0], p.char_sheet.level, self.db.cursor,
                                              self.win_ui.tilesets, self.win_ui.resources, self.pygame_settings.audio)
        p.char_sheet.hotbar[-1] = skill.Skill(default_skills[1], p.char_sheet.level, self.db.cursor,
                                              self.win_ui.tilesets, self.win_ui.resources, self.pygame_settings.audio)
        for i in range(2, len(default_skills)):
            p.char_sheet.skills[i-2] = skill.Skill(default_skills[i], p.char_sheet.level, self.db.cursor,
                                                   self.win_ui.tilesets, self.win_ui.resources, self.pygame_settings.audio)

        default_treasure = dbrequests.treasure_defaults_get(self.db.cursor, initial_char_stats['character_id'])
        p.char_sheet.equipped[2][0] = treasure.Treasure(default_treasure[0], p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                                        self.win_ui.resources, self.pygame_settings.audio,
                                                        self.win_ui.resources.fate_rnd)
        for i in range(1, len(default_treasure)):
            if default_treasure[i] == 8:
                p.char_sheet.hotbar[0] = treasure.Treasure(default_treasure[i], p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                                    self.win_ui.resources, self.pygame_settings.audio,
                                                    self.win_ui.resources.fate_rnd)
                p.char_sheet.hotbar[0].props['charges'] = 9
            elif default_treasure[i] == 11:
                p.char_sheet.hotbar[1] = treasure.Treasure(default_treasure[i], p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                                    self.win_ui.resources, self.pygame_settings.audio,
                                                    self.win_ui.resources.fate_rnd)
                p.char_sheet.hotbar[1].props['charges'] = 9
            else:
                for j in range(0, p.char_sheet.inventory.items_max):
                    if p.char_sheet.inventory[j] is None:
                        p.char_sheet.inventory[j] = treasure.Treasure(default_treasure[i], p.char_sheet.level, self.db.cursor,
                                                                self.win_ui.tilesets, self.win_ui.resources,
                                                                self.pygame_settings.audio, self.win_ui.resources.fate_rnd)
                        break
        """p.char_sheet.inventory[0] = treasure.Treasure(9, p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                                        self.win_ui.resources, self.pygame_settings.audio,
                                                        self.win_ui.resources.fate_rnd)"""
        debuff.DeBuff(dbrequests.de_buff_get_by_id_with_mods(self.db.cursor, 3, self.resources.fate_rnd),
                      p.char_sheet.de_buffs)
        self.pc = p

    def char_save(self, pc, maze):
        gamesave.save_char(self.wins_dict, pc, maze, self.db, self.win_ui.tilesets)

    def maze_save(self, pc, maze):
        gamesave.save_maze(pc, maze, self.db, self.win_ui.tilesets, self.animations)

    def char_load(self):
        if self.save_selection is not None:
            char_sheet = charsheet.CharSheet(self.db, self.savegames[self.save_selection]['char_id'],
                                             chr_name=self.field_charname_edit.text_obj.caption,
                                             chr_type=self.savegames[self.save_selection]['char_type'], chr_level=1)

            anim = 'anthro_champion'
            if char_sheet.type == 'kingslayer':
                anim = 'anthro_kingslayer'
            elif char_sheet.type == 'cosmologist':
                anim = 'anthro_cosmologist'

            p = pc.PC(0, 0, None, self.animations.get_animation(anim), char_sheet, state=0)
            p.char_portrait_index = self.savegames[self.save_selection]['char_image_index']

            gamesave.load_char(self.wins_dict, p, self.db.cursor, self.win_ui.tilesets)
            self.pc = p

            self.entry_bonus()
            self.pc.day_stamp = maths.get_days()

            self.char_loaded_info_update()
        else:
            self.wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': 'Choose a saved character first!',
                'bttn_cancel': 'OK'
            }
            self.wins_dict['dialogue'].launch(pc)

    def char_delete(self):
        gamesave.char_wipe(self.db, self.savegames[self.save_selection]['char_id'])
        dbrequests.char_delete(self.db, self.savegames[self.save_selection]['char_id'])
        if self.save_ui_blocks_list[self.save_selection][0] in self.win_ui.interactives:
            self.win_ui.interactives.remove(self.save_ui_blocks_list[self.save_selection][0])
        for i in range(1, len(self.save_ui_blocks_list[self.save_selection])):
            if self.save_ui_blocks_list[self.save_selection][i] in self.win_ui.decoratives:
                self.win_ui.decoratives.remove(self.save_ui_blocks_list[self.save_selection][i])
        self.save_ui_blocks_list[self.save_selection] = None
        self.savegames[self.save_selection] = None
        self.win_ui.updated = True
        self.save_selection = None
        self.bttn_char_delete.page.remove(0)

    def clear_quick_view(self):
        self.wins_dict['stash'].end()
        for win in self.wins_dict.values():
            if win is not self and win in self.active_wins:
                self.active_wins.remove(win)
        """if self.pc is not None:
            self.pc.char_sheet.itemlist_cleanall_inventory(self.wins_dict, self.pc)"""
        for inter in self.win_ui.interactives:
            if 'quick_view' in inter.tags:
                inter.mode = 0
                inter.render()
        self.mouse_pointer.drag_item = None
        self.mouse_pointer.image = None
        self.mouse_pointer.catcher[0] = None

    def ending_check(self, pc):
        can_conclude = None
        if self.wins_dict['realm'].maze.chapter['quest_item_id'] is not None:
            quest_item_id = self.wins_dict['realm'].maze.chapter['quest_item_id']
            quest_item_list = pc.char_sheet.inventory_search_by_id(quest_item_id, amount=-1) + pc.char_sheet.equipped_search_by_id(quest_item_id)
            for qi in quest_item_list:
                if qi is not None and 'quest_item' in qi.props:
                    can_conclude = qi
        else:
            blackrock_list = pc.char_sheet.inventory_search(item_class='blackrock') + pc.char_sheet.equipped_search(item_class='blackrock')
            for br in blackrock_list:
                if br is not None and 'quest_item' in br.props:
                    can_conclude = br

        if can_conclude:
            self.wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': "Finish your Quest? $n $n (If you leave now, you will not be able to return to this world anymore without restarting the Chapter!)",
                'bttn_cancel': 'NO',
                'bttn_ok': 'YES'
            }
            self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self, 'chapter_conclude', (can_conclude, self.wins_dict, pc))
            self.wins_dict['dialogue'].launch(pc)
            self.pygame_settings.audio.sound('important_jingle')
        else:
            self.wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': 'You can not go outside until your quest is complete. Would you like to take a break and exit to the Character screen?',
                'bttn_cancel': 'NO',
                'bttn_ok': 'YES'
            }
            self.wins_dict['dialogue'].delayed_action['bttn_ok'] = (self.wins_dict['options'], 'overlay_save_and_exit', (self.wins_dict, pc,))
            self.wins_dict['dialogue'].launch(pc)

    def chapter_conclude(self, quest_item, wins_dict, pc):
        del quest_item.props['quest_item']
        # quest_item.props['price_sell'] = pc.char_sheet.level * 1000
        wins_dict['app_title'].chapter_end(pc, wins_dict['realm'].maze.chapter)
        pc.location = None
        pc.stage_entry = 'up'

    def entry_bonus(self):
        day_current = maths.get_days()
        if day_current - self.pc.day_stamp > 0:
            debuff.DeBuff(dbrequests.de_buff_get_by_id_with_mods(self.db.cursor, 3, self.resources.fate_rnd),
                          self.pc.char_sheet.de_buffs)

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated:
            self.render()

    def align(self, width, height):
        self.offset_x = (width - self.win_w) // 2
        self.offset_y = (height - self.win_h) // 2

    def render(self):
        self.win_rendered.fill((10, 10, 10))
        logo_x = (self.win_w - self.logo_w) // 2
        logo_y = 0
        self.win_rendered.blit(self.logo, (logo_x, logo_y))
        self.win_ui.draw(self.win_rendered)

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
