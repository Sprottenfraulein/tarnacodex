# game title window
import pygame
import settings
import random
from library import textinput, pydraw
from components import maze, pc, charsheet, ui, skill, treasure, dbrequests, gamesave


class AppTitle:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.win_w, self.win_h = pygame_settings.screen_res
        self.offset_x = 0
        self.offset_y = 0
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations

        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db)

        self.pc = None

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
        self.curr_char_panel = None
        self.curr_char_name_string = None
        self.curr_char_type_string = None
        self.field_charname_edit = None
        self.char_selection = 0
        self.chapter_selection = 0
        self.save_selection = None
        self.create_elements(log=True)
        self.char_name_rnd()

        # creating dedicated schedule
        self.schedule_man.new_schedule('realm_tasks')

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()

        self.render()

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
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

        # return True if interaction was made to prevent other windows from responding to this event
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN:
            return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event),
                                 pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            for inter in self.win_ui.interactives:
                inter.release(1)
                inter.release(3)
            self.win_ui.updated = True
            return
        element, m_bttn, mb_event = inter_click
        # PAGE 0
        if element.id in ('input_name',) and m_bttn == 1 and mb_event == 'down':
            self.win_ui.key_focus = element
        elif element.id == 'new_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            if len(self.savegames) < 6 or (len(self.savegames) == 6 and None in self.savegames):
                self.win_ui.page = 1
        elif element.id == 'delete_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            if self.save_selection is not None:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'Are you sure you want to DELETE the character?',
                    'bttn_cancel': 'CANCEL',
                    'bttn_ok': 'OK'
                }
                wins_dict['dialogue'].delayed_action = (self, 'char_delete', [])
                wins_dict['dialogue'].launch(pc, wins_dict, active_wins)
            else:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'Choose a CHARACTER you want TO DELETE!',
                    'bttn_cancel': 'OK'
                }
                wins_dict['dialogue'].launch(pc, wins_dict, active_wins)
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
                        if inter.text_obj.color != resources.colors['sun']:
                            inter.text_obj.color = resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()
                            self.char_selection = inter.id
                            self.char_info_update()
                    elif 'charswitch' in inter.tags:
                        inter.mode = 0
                        if inter.text_obj.color != resources.colors['fnt_muted']:
                            inter.text_obj.color = resources.colors['fnt_muted']
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
                        if inter.text_obj.color != resources.colors['sun']:
                            inter.text_obj.color = resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()
                            self.chapter_selection = inter.id
                            self.chapter_info_update()
                    elif 'chapterswitch' in inter.tags:
                        inter.mode = 0
                        if inter.text_obj.color != resources.colors['fnt_muted']:
                            inter.text_obj.color = resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True
        # TAGGED RADIO BUTTON SWITCH GROUP
        if 'saveswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down' and element.mode == 0:
                for inter in self.win_ui.interactives:
                    if inter == element:
                        self.save_selection = inter.id
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
            self.win_ui.page = 0
            self.win_ui.key_focus = None
            self.clear_quick_view(wins_dict, active_wins)

        elif element.id == 'new_char_begin' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None

            self.char_create()

            self.pc.char_sheet.calc_stats()
            self.pc.char_sheet.hp_get(100, percent=True)
            self.pc.char_sheet.mp_get(100, percent=True)
            self.pc.char_sheet.food_get(100, percent=True)

            self.pc.location = [self.chapters[self.chapter_selection], 0]

            wins_dict['hotbar'].launch(self.pc)

            self.location_change(pygame_settings, wins_dict, active_wins, self.pc, 'up', launch=True)

        elif element.id == 'begin_chapter' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            if self.pc is None:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have to load a character first!',
                    'bttn_cancel': 'OK'
                }
                wins_dict['dialogue'].launch(pc, wins_dict, active_wins)
            else:
                self.win_ui.key_focus = None
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'All existing chapter progress will be erased! $n Continue?',
                    'bttn_cancel': 'NO',
                    'bttn_ok': 'YES'
                }
                wins_dict['dialogue'].delayed_action = (self, 'chapter_begin', (pygame_settings, wins_dict, active_wins))
                wins_dict['dialogue'].launch(pc, wins_dict, active_wins)

        elif element.id == 'continue_chapter' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            if self.pc is None:
                wins_dict['dialogue'].dialogue_elements = {
                    'header': 'Attention',
                    'text': 'You have to load a character first!',
                    'bttn_cancel': 'OK'
                }
                wins_dict['dialogue'].launch(pc, wins_dict, active_wins)
            else:
                self.win_ui.key_focus = None

                self.pc.char_sheet.calc_stats()
                self.pc.char_sheet.hp_get(100, percent=True)
                self.pc.char_sheet.mp_get(100, percent=True)
                self.pc.char_sheet.food_get(100, percent=True)

                self.clear_quick_view(wins_dict, active_wins)

                self.location_change(pygame_settings, wins_dict, active_wins, self.pc, 'up', launch=True)

        elif element.id == 'load' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.key_focus = None
            self.char_load(pygame_settings, wins_dict, active_wins)

        # PAGE 2 quickview buttons
        if 'quick_view' in element.tags and m_bttn == 1 and element.mode == 0 and mb_event == 'down':
            if element.id == 'quick_inv':
                if not wins_dict['inventory'] in active_wins:
                    wins_dict['inventory'].launch(self.pc)
                    wins_dict['inventory'].render()
                    active_wins.insert(0, wins_dict['inventory'])
            elif element.id == 'quick_skb':
                if not wins_dict['skillbook'] in active_wins:
                    wins_dict['skillbook'].launch(self.pc)
                    wins_dict['skillbook'].render()
                    active_wins.insert(0, wins_dict['skillbook'])
            elif element.id == 'quick_hot':
                if not wins_dict['hotbar'] in active_wins:
                    wins_dict['hotbar'].render()
                    active_wins.insert(0, wins_dict['hotbar'])
            elif element.id == 'quick_char':
                if not wins_dict['charstats'] in active_wins:
                    wins_dict['charstats'].launch(self.pc)
                    wins_dict['charstats'].render()
                    active_wins.insert(0, wins_dict['charstats'])

        elif 'quick_view' in element.tags and m_bttn == 1 and element.mode == 1 and element.sw_op is False and mb_event == 'up':
            if element.id == 'quick_inv':
                if wins_dict['inventory'] in active_wins:
                    active_wins.remove(wins_dict['inventory'])
                    self.pc.char_sheet.itemlist_cleanall_inventory()
                    wins_dict['inventory'].end()
            elif element.id == 'quick_skb':
                if wins_dict['skillbook'] in active_wins:
                    active_wins.remove(wins_dict['skillbook'])
                    self.pc.char_sheet.itemlist_cleanall_skills()
                    wins_dict['skillbook'].end()
            elif element.id == 'quick_hot':
                if wins_dict['hotbar'] in active_wins:
                    active_wins.remove(wins_dict['hotbar'])
            elif element.id == 'quick_char':
                if wins_dict['charstats'] in active_wins:
                    active_wins.remove(wins_dict['charstats'])
                    wins_dict['charstats'].end()

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.chars = dbrequests.chars_get_all(self.db.cursor)
        self.chapters = dbrequests.chapters_get_all(self.db.cursor)
        self.savegames = dbrequests.savegames_get_all(self.db.cursor)

        menu_btn_h = 40
        menu_btn_w = 256

        # MAIN MENU
        main_menu = [
            self.win_ui.button_add('new_char', caption='New Character', size=(menu_btn_w, menu_btn_h), cap_font='large',
                                   cap_size=16,cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
            self.win_ui.button_add('exit', caption='Exit', size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                   cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
        ]
        if len(self.savegames) > 0:
            main_menu.insert(-1, self.win_ui.button_add('delete_char', caption='Delete Character', size=(menu_btn_w, menu_btn_h),
                                                    cap_font='large', cap_size=16,cap_color='fnt_muted',
                                                    sounds=self.win_ui.snd_packs['button']))

        for i in range(0, len(main_menu)):
            main_menu[i].tags = ['lightup']
            main_menu[i].page = (0,)
            main_menu[i].rendered_rect.left = round(menu_btn_h)
            main_menu[i].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i

        main_menu[-1].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # SAVED GAMES
        saves_left = menu_btn_h + menu_btn_w + menu_btn_h
        saves_top = self.win_h / 2 - menu_btn_h // 2
        save_w = 160
        save_h = 210
        saves_per_row = 5
        saves_total = 5
        save_texture = self.win_ui.random_texture((save_w, save_h), 'black_rock')
        bttn_img_up = pydraw.square((0, 0), (save_w, save_h),
                                    (self.win_ui.resources.colors['gray_light'],
                                     self.win_ui.resources.colors['gray_dark'],
                                     (0,254,0),
                                     self.win_ui.resources.colors['black']),
                                    sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=True)
        bttn_img_down = pydraw.square((0, 0), (save_w, save_h),
                                    (self.win_ui.resources.colors['gray_light'],
                                     self.win_ui.resources.colors['gray_dark'],
                                     (0,254,0),
                                     self.win_ui.resources.colors['sun']),
                                    sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=True)
        for i in range(0, min(saves_total, len(self.savegames))):
            save_x = saves_left + (save_w + 8) * (i % saves_per_row)
            save_y = saves_top + (save_h + 8) * (i // saves_per_row)

            char_img = self.win_ui.tilesets.get_image('char_portraits', (60,60), (self.savegames[i]['char_image_index'],))
            char_panel = self.win_ui.panel_add(i, (save_x + 20, save_y + 12), (120, 120), images=char_img, img_stretch=True, page=(0,))
            self.win_ui.decoratives.append(char_panel)

            char_name_string = \
                self.win_ui.text_add('char_name',
                                     (save_x + 4, save_y + 8 + 120 + 8),
                                     caption='%s' % self.savegames[i]['char_name'],
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color='fnt_celeb',
                                     cap_font='def_bold', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(char_name_string)

            char_type_string = \
                self.win_ui.text_add('char_type',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14),
                                     caption='%s, level %s' % (self.savegames[i]['char_type'].capitalize(), self.savegames[i]['char_level']),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color='fnt_celeb',
                                     cap_font='def_normal', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(char_type_string)

            chapter_string = \
                self.win_ui.text_add('chapter_label',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14 + 14),
                                     caption=self.savegames[i]['chapter_label'] + ' %s:' % (self.savegames[i]['stage_index'] + 1,),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color='fnt_celeb',
                                     cap_font='def_normal', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(chapter_string)

            stage_string = \
                self.win_ui.text_add('stage_string',
                                     (save_x + 4, save_y + 8 + 120 + 8 + 14 + 14 + 14),
                                     caption='%s' % (self.savegames[i]['stage_label'], ),
                                     h_align='center', v_align='top', size=(save_w - 8, 14), cap_color='fnt_celeb',
                                     cap_font='def_normal', cap_size=24, page=(0,))
            self.win_ui.decoratives.append(stage_string)

            save_panel = self.win_ui.panel_add(i, (save_x, save_y), (save_w, save_h), images=(save_texture,), page=(0,))
            self.win_ui.decoratives.append(save_panel)

            save_bttn = self.win_ui.button_add(i, xy=(save_x, save_y),size=(save_w, save_h),
                                               images=(bttn_img_up, bttn_img_down),
                                               sounds=self.win_ui.snd_packs['button'], switch=True, page=(0,))
            save_bttn.tags = ('saveswitch',)
            save_bttn.rendered_button.set_colorkey((0, 254, 0))
            self.win_ui.interactives.append(save_bttn)
            self.save_ui_blocks_list.append((save_bttn, char_panel, save_panel, stage_string,
                                             chapter_string, char_type_string, char_name_string))

        if len(self.savegames) > 0:
            bttn_load = self.win_ui.button_add('load', caption='Load', size=(menu_btn_w, menu_btn_h),
                                                cap_font='large', cap_size=16,
                                                cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(0,))
            bttn_load.rendered_rect.right = round(self.win_ui.pygame_settings.screen_res[0] - menu_btn_h)
            bttn_load.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7
            self.win_ui.interactives.append(bttn_load)

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
            new_bttn.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                        menu_btn_h * 1.2) * i
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
        bttn_back.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7

        bttn_begin.rendered_rect.right = round(self.win_ui.pygame_settings.screen_res[0] - menu_btn_h)
        bttn_begin.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # CHAR NAME INPUT FIELD
        self.field_charname_edit = self.win_ui.edit_add('input_name', (0, 0), sounds=self.win_ui.snd_packs['text_input'], cap_font='def_normal',
                                                        size=(round(menu_btn_w * 0.6), round(menu_btn_h * 0.7)), h_align='center', page=(1,))
        self.field_charname_edit.rendered_rect.centerx = round(menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        self.field_charname_edit.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
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
        rnd_name_bttn = self.win_ui.button_add('rnd_name', caption='/@', size=(round(menu_btn_h * 0.7), round(menu_btn_h * 0.7)),
                               cap_font='def_bold', cap_size=24, cap_color='fnt_celeb',
                               sounds=self.win_ui.snd_packs['button'], images=(bttn_img_up, bttn_img_down), page=(1,))
        rnd_name_bttn.rendered_rect.left = self.field_charname_edit.rendered_rect.right
        rnd_name_bttn.rendered_rect.top = self.field_charname_edit.rendered_rect.top
        self.win_ui.interactives.append(rnd_name_bttn)

        # CHAPTERS CHOICE
        chapter_menu = []
        for i in range(0, min(5, len(self.chapters))):
            new_bttn = self.win_ui.button_add(i, caption=self.chapters[i]['label'].capitalize(),
                                              size=(menu_btn_w, menu_btn_h), cap_font='large', cap_size=16,
                                              cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                              switch=True, mode=0)
            new_bttn.tags = ['lightup', 'chapterswitch']
            new_bttn.page = (1,2)
            new_bttn.rendered_rect.right = round(self.win_ui.pygame_settings.screen_res[0] - menu_btn_h)
            new_bttn.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * i
            chapter_menu.append(new_bttn)

        chapter_menu[0].mode = 1
        chapter_menu[0].text_obj.color = self.win_ui.resources.colors['sun']
        chapter_menu[0].text_obj.render()
        chapter_menu[0].render()

        char_string = \
            self.win_ui.text_add('char_string',
            (menu_btn_h, round(self.win_ui.pygame_settings.screen_res[1] / 2 - menu_btn_h*1.5)),
            caption='Choose a character:',
            h_align='center', v_align='top', size=char_menu[0].size, cap_color='fnt_celeb',
            cap_font='large', cap_size=14, page=(1,))
        self.win_ui.decoratives.append(char_string)

        chapter_string = \
            self.win_ui.text_add('char_string',
            (self.win_ui.pygame_settings.screen_res[0] - menu_btn_h - menu_btn_w,
            round(self.win_ui.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5)),
            caption='Choose a chapter:',
            h_align='center', v_align='top', size=char_menu[0].size,
            cap_color='fnt_celeb',
            cap_font='large', cap_size=14, page=(1,2))
        self.win_ui.decoratives.append(chapter_string)

        char_imgs = self.win_ui.tilesets.get_image('char_portraits', (60,60), (0,))
        self.char_img_panel = self.win_ui.panel_add('char_img_panel', (
            menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            char_menu[0].rendered_rect.top
        ), (120, 120), images=char_imgs, page=(1,), img_stretch=True)
        self.win_ui.decoratives.append(self.char_img_panel)

        self.char_title_string = \
            self.win_ui.text_add('char_title',
                                 (0, chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption="%s's story:" % self.chars[self.char_selection]['label'].capitalize(),
                                 h_align='center', v_align='top', size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(1,))
        self.char_title_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.char_title_string)

        self.char_desc_string = \
            self.win_ui.text_add('char_desc', (menu_btn_h * 2 + menu_btn_w, round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chars[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ), cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(1,))
        self.win_ui.decoratives.append(self.char_desc_string)

        input_invite_string = \
            self.win_ui.text_add('input_invite',
                                 (0, round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7 - 48),
                                 caption="Enter hero's name:",
                                 h_align='center', v_align='top',
                                 size=(280, 32),
                                 cap_color='fnt_celeb',
                                 cap_font='large', cap_size=14, page=(1,))
        input_invite_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(input_invite_string)

        chapter_imgs = self.win_ui.tilesets.get_image('red_glass', (60, 60), (0,))
        self.chapter_img_panel = self.win_ui.panel_add('chapter_img_panel', (
            self.win_ui.pygame_settings.screen_res[0] / 2 + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            chapter_menu[0].rendered_rect.top
        ), (120, 120), images=chapter_imgs, page=(1,2), img_stretch=True)
        self.win_ui.decoratives.append(self.chapter_img_panel)

        self.chapter_title_string = \
            self.win_ui.text_add('chapter_title',
                                 (0,chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption=self.chapters[0]['label'], h_align='center', v_align='top',
                                 size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(1, 2))
        self.chapter_title_string.rendered_rect.centerx = self.win_ui.pygame_settings.screen_res[0] / 2 + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.chapter_title_string)

        self.chapter_desc_string = \
            self.win_ui.text_add('chapter_desc',
                                 (self.win_ui.pygame_settings.screen_res[0] - (menu_btn_h * 2 + menu_btn_w) - (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64),
                                  round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chapters[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ),
                                 cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(1,2))
        self.win_ui.decoratives.append(self.chapter_desc_string)

        # PAGE 2
        self.curr_chapter_img_panel = self.win_ui.panel_add('chapter_img_panel', (
            menu_btn_h + menu_btn_w + (
                        self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2 - 60,
            char_menu[0].rendered_rect.top
        ), (120, 120), images=chapter_imgs, page=(2,), img_stretch=True)
        self.win_ui.decoratives.append(self.curr_chapter_img_panel)

        self.curr_chapter_title_string = \
            self.win_ui.text_add('chapter_title',
                                 (0, chapter_menu[0].rendered_rect.top + 120 + 8),
                                 caption=self.chapters[0]['label'], h_align='center', v_align='top',
                                 size=(menu_btn_w, 32),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(2,))
        self.curr_chapter_title_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.curr_chapter_title_string)

        self.curr_chapter_desc_string = \
            self.win_ui.text_add('chapter_desc',
                                 (menu_btn_h * 2 + menu_btn_w, round(char_menu[0].rendered_rect.top + 120 + 48)),
                                 caption=self.chapters[0]['desc'], h_align='left', v_align='top',
                                 size=(
                                     self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w - 64, 120
                                 ),
                                 cap_color='fnt_celeb', cap_font='def_normal', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_chapter_desc_string)

        self.curr_chapter_stage_string = \
            self.win_ui.text_add('chapter_stage',
                                 (0, round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7 - menu_btn_h * 1.9),
                                 caption='chapter $n stage', h_align='center', v_align='top',
                                 size=(menu_btn_w, 48),
                                 cap_color='fnt_celeb', cap_font='large', cap_size=14, page=(2,))
        self.curr_chapter_stage_string.rendered_rect.centerx = menu_btn_h + menu_btn_w + (
                    self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2
        self.win_ui.decoratives.append(self.curr_chapter_stage_string)

        bttn_begin_chapter = self.win_ui.button_add('begin_chapter', caption='Start New Chapter', size=(menu_btn_w, menu_btn_h),
                                            cap_font='large', cap_size=16,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=(2,))
        bttn_begin_chapter.rendered_rect.right = round(self.win_ui.pygame_settings.screen_res[0] - menu_btn_h)
        bttn_begin_chapter.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7

        bttn_continue_chapter = self.win_ui.button_add('continue_chapter', caption='Resume Chapter',
                                                    size=(menu_btn_w, menu_btn_h),
                                                    cap_font='large', cap_size=16,
                                                    cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                                                    page=(2,))
        bttn_continue_chapter.rendered_rect.centerx = round(menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        bttn_continue_chapter.rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                menu_btn_h * 1.2) * 7

        curr_chapter_string = \
            self.win_ui.text_add('chapter_string',
                                 (menu_btn_h, round(self.win_ui.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5)),
                                 caption='Current Chapter:',
                                 h_align='center', v_align='top', size=char_menu[0].size, cap_color='fnt_celeb',
                                 cap_font='large', cap_size=14, page=(2,))
        curr_chapter_string.rendered_rect.centerx = round(
            menu_btn_h + menu_btn_w + (self.win_ui.pygame_settings.screen_res[0] / 2 - menu_btn_h - menu_btn_w) / 2)
        self.win_ui.decoratives.append(curr_chapter_string)

        # character windows buttons
        quick_btn_w = 60
        quick_btn_h = 34
        bttns_per_row = 2
        bttn_texture = self.win_ui.random_texture((quick_btn_w, quick_btn_h), 'red_glass')
        bttn_icons = (
            self.win_ui.tilesets.get_image('interface', (24, 24,), (20, 21)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (22, 23)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (24, 25)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (26, 27)),
            self.win_ui.tilesets.get_image('interface', (24, 24,), (28, 29))
        )
        bttn_img_list = []
        for i in range(0, 5):
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
            self.win_ui.button_add('quick_inv', size=(quick_btn_w, quick_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[0], switch=True),
            self.win_ui.button_add('quick_skb', size=(quick_btn_w, quick_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[1], switch=True),
            self.win_ui.button_add('quick_hot', size=(quick_btn_w, quick_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[2], switch=True),
            self.win_ui.button_add('quick_char', size=(quick_btn_w, quick_btn_h), cap_size=24, cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[3], switch=True),
            # self.win_ui.button_add('opts', size=(quick_btn_w, quick_btn_h), cap_size=24, cap_color='fnt_muted',
            #                        sounds=self.win_ui.snd_packs['button'], images=bttn_img_list[4], switch=True),
        )
        for i in range(0, len(char_quick_menu)):
            char_quick_menu[i].tags = ['quick_view']
            char_quick_menu[i].page = (2,)
            char_quick_menu[i].rendered_rect.left = menu_btn_h + menu_btn_w // 2 - 60 + (quick_btn_w * (i % bttns_per_row))
            char_quick_menu[i].rendered_rect.top = chapter_menu[0].rendered_rect.top + 120 + 8 + 64 + (quick_btn_h * (i // bttns_per_row))

        # loaded character info
        curr_char_string = \
            self.win_ui.text_add('char_string',
                                 (menu_btn_h, round(self.win_ui.pygame_settings.screen_res[1] / 2 - menu_btn_h * 1.5)),
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
                                 h_align='center', v_align='top', size=(save_w - 16, 14), cap_color='fnt_celeb',
                                 cap_font='def_bold', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_char_name_string)

        self.curr_char_type_string = \
            self.win_ui.text_add('char_type',
                                 (menu_btn_h + 56, char_menu[0].rendered_rect.top + 120 + 8 + 14),
                                 caption='char_type',
                                 h_align='center', v_align='top', size=(save_w - 16, 14), cap_color='fnt_celeb',
                                 cap_font='def_normal', cap_size=24, page=(2,))
        self.win_ui.decoratives.append(self.curr_char_type_string)

        # all pages
        tag_string = self.win_ui.text_add('tag_string', (0, self.win_ui.pygame_settings.screen_res[1] - 16),
                                          caption=settings.tag_string, h_align='left', v_align='bottom',
                                          size=(self.win_ui.pygame_settings.screen_res[0] // 4, 16), cap_color='sun')

        self.win_ui.interactives.extend(char_quick_menu)
        self.win_ui.interactives.append(bttn_continue_chapter)
        self.win_ui.interactives.append(bttn_begin_chapter)
        self.win_ui.interactives.append(bttn_begin)
        self.win_ui.interactives.append(bttn_back)
        self.win_ui.interactives.extend(main_menu)
        self.win_ui.interactives.extend(char_menu)
        self.win_ui.interactives.extend(chapter_menu)
        self.win_ui.interactives.append(self.field_charname_edit)
        self.win_ui.interactives.append(tag_string)

    def location_change(self, pygame_settings, wins_dict, active_wins, pc, entry, launch=False):
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, 20, None))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, wins_dict['app_title'], 'location_update',
                                                     (pygame_settings, wins_dict, active_wins, pc,
                                                     entry, launch))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

    def location_update(self, pygame_settings, wins_dict, active_wins, pc, entry, launch=False):

        if not launch:
            gamesave.save_maze(pc, wins_dict['realm'].maze, self.db, self.win_ui.tilesets, self.animations, pygame_settings.audio)
        # dbrequests.chapter_progress_set(self.db, pc.char_sheet.id, wins_dict['realm'].maze.stage_index, 1, 1, 1, 1, 1, 1)

        wins_dict['realm'].maze = None
        l = maze.Maze(self.db, self.animations, self.win_ui.tilesets, pygame_settings.audio, pc)

        for i in range(0, len(l.exits)):
            if l.exits[i].dest == entry:
                pc.x_sq = l.exits[i].x_sq
                pc.y_sq = l.exits[i].y_sq + 1
                break

        gamesave.save_maze(pc, l, self.db, self.win_ui.tilesets, self.animations, pygame_settings.audio)
        dbrequests.chapter_progress_set(self.db, pc.char_sheet.id, l.stage_index, 1, 1, 1, 1, 1, 1)

        gamesave.save_char(pc, l, self.db, self.win_ui.tilesets, pygame_settings.audio)

        wins_dict['realm'].maze = l
        wins_dict['realm'].pc = pc

        if launch:
            wins_dict['realm'].launch(pygame_settings.audio, settings, wins_dict, active_wins)

            active_wins.append(wins_dict['realm'])
            active_wins.remove(self)
        else:
            wins_dict['realm'].stage_update(wins_dict)

        wins_dict['realm'].render_update()
        wins_dict['pools'].render()

    def char_info_update(self):
        self.char_img_panel.images_update(self.win_ui.tilesets.get_image('char_portraits', (60,60), (self.char_selection,)))

        self.char_desc_string.text_obj.caption = self.chars[self.char_selection]['desc']
        self.char_desc_string.render_all()

        self.char_title_string.text_obj.caption = "%s's story:" % self.chars[self.char_selection]['label'].capitalize()
        self.char_title_string.render_all()

    def chapter_info_update(self):
        self.chapter_img_panel.images_update(self.win_ui.tilesets.get_image('red_glass', (60,60), (self.chapters[self.chapter_selection]['chapter_image_index'],)))

        self.chapter_desc_string.text_obj.caption = self.chars[self.chapter_selection]['desc']
        self.chapter_desc_string.render_all()

        self.chapter_title_string.text_obj.caption = self.chars[self.chapter_selection]['label'].capitalize()
        self.chapter_title_string.render_all()

    def chapter_begin(self, pygame_settings, wins_dict, active_wins):
        self.pc.char_sheet.calc_stats()
        self.pc.char_sheet.hp_get(100, percent=True)
        self.pc.char_sheet.mp_get(100, percent=True)
        self.pc.char_sheet.food_get(100, percent=True)

        gamesave.chapter_wipe(self.db, self.pc)

        self.pc.location = [self.chapters[self.chapter_selection], 0]

        self.clear_quick_view(wins_dict, active_wins)

        self.location_change(pygame_settings, wins_dict, active_wins, self.pc, 'up', launch=True)

    def chapter_end(self, wins_dict, active_wins, chapter_dict):
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, 20, None))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, wins_dict['demos'], 'ending_run',
                                                     (wins_dict, active_wins, self.win_ui.resources, pc, chapter_dict))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

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
        p = pc.PC(0, 0, None, self.animations.get_animation('anthro_default'), char_sheet, state=0)
        p.char_portrait_index = self.char_selection
        p.char_sheet.hotbar[-2] = skill.Skill(1, p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                              self.win_ui.resources, self.win_ui.pygame_settings.audio)
        p.char_sheet.hotbar[-1] = skill.Skill(2, p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                              self.win_ui.resources, self.win_ui.pygame_settings.audio)
        p.char_sheet.equipped[2][0] = treasure.Treasure(3, p.char_sheet.level, self.db.cursor, self.win_ui.tilesets,
                                                        self.win_ui.resources, self.win_ui.pygame_settings.audio,
                                                        self.win_ui.resources.fate_rnd)
        self.pc = p

    def char_load(self, pygame_settings, wins_dict, active_wins):
        if self.save_selection is not None:
            char_sheet = charsheet.CharSheet(self.db, self.savegames[self.save_selection]['char_id'],
                                             chr_name=self.field_charname_edit.text_obj.caption,
                                             chr_type=self.chars[self.char_selection]['char_type'], chr_level=1)
            p = pc.PC(0, 0, None, self.animations.get_animation('anthro_default'), char_sheet, state=0)
            p.char_portrait_index = self.savegames[self.save_selection]['char_image_index']

            gamesave.load_char(p, self.db.cursor, self.win_ui.tilesets, pygame_settings.audio)

            self.pc = p

            self.curr_chapter_img_panel.images_update(
                self.win_ui.tilesets.get_image('red_glass', (60, 60), (self.pc.location[0]['chapter_image_index'],)))
            self.curr_chapter_title_string.text_obj.caption = self.pc.location[0]['label'].capitalize()
            self.curr_chapter_title_string.render_all()
            self.curr_chapter_desc_string.text_obj.caption = self.pc.location[0]['desc']
            self.curr_chapter_desc_string.render_all()
            self.curr_chapter_stage_string.text_obj.caption = 'Level %s: $n %s' % (
            self.pc.location[1] + 1, self.savegames[self.chapter_selection]['stage_label'])
            self.curr_chapter_stage_string.render_all()
            self.curr_char_panel.images_update(
                self.win_ui.tilesets.get_image('char_portraits', (60, 60), (self.pc.char_portrait_index,)))
            self.curr_char_name_string.text_obj.caption = self.pc.char_sheet.name
            self.curr_char_name_string.render_all()
            self.curr_char_type_string.text_obj.caption = '%s, level %s' % (
            self.pc.char_sheet.type.capitalize(), self.pc.char_sheet.level)
            self.curr_char_type_string.render_all()

            # self.location_change(pygame_settings, wins_dict, active_wins, p, 'up', launch=True)
            self.win_ui.page = 2

            wins_dict['hotbar'].launch(self.pc)

            self.win_ui.updated = True
        else:
            wins_dict['dialogue'].dialogue_elements = {
                'header': 'Attention',
                'text': 'Choose a saved character first!',
                'bttn_cancel': 'OK'
            }
            wins_dict['dialogue'].launch(pc, wins_dict, active_wins)

    def char_delete(self):
        gamesave.char_wipe(self.db, self.savegames[self.save_selection]['char_id'])
        dbrequests.char_delete(self.db, self.savegames[self.save_selection]['char_id'])
        self.win_ui.interactives.remove(self.save_ui_blocks_list[self.save_selection][0])
        for i in range(1, len(self.save_ui_blocks_list[self.save_selection])):
            self.win_ui.decoratives.remove(self.save_ui_blocks_list[self.save_selection][i])
        self.save_ui_blocks_list[self.save_selection] = None
        self.savegames[self.save_selection] = None
        self.win_ui.updated = True
        self.save_selection = None

    def clear_quick_view(self, wins_dict, active_wins):
        for win in wins_dict.values():
            if win is not self and win in active_wins:
                active_wins.remove(win)
                win.end()
        for inter in self.win_ui.interactives:
            if 'quick_view' in inter.tags:
                inter.mode = 0
                inter.render()
        if self.pc is not None:
            self.pc.char_sheet.itemlist_cleanall_inventory()
            self.pc.char_sheet.itemlist_cleanall_skills()

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.win_ui.tick(pygame_settings, mouse_pointer)
        if self.win_ui.updated:
            self.render()

    def align(self, width, height):
        self.offset_x = (width - self.win_w) // 2
        self.offset_y = (height - self.win_h) // 2

    def render(self):
        self.win_rendered.fill((10, 10, 10))
        self.win_ui.draw(self.win_rendered)

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
