# game title window
import pygame
import settings
from library import textinput
from objects import maze, pc, charsheet, ui


class AppTitle:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.title_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.create_elements(log=True)

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.title_ui.key_focus is not None:
                if self.title_ui.key_focus.page is not None and self.title_ui.key_focus.page != self.title_ui.page:
                    return
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.title_ui.key_focus.mode = 0

                    self.title_ui.key_focus.do_sound(2)

                    self.title_ui.key_focus = None
                    return
                self.title_ui.key_focus.text_obj.caption = textinput.do_edit(event.unicode,
                                                                             self.title_ui.key_focus.text_obj.caption,
                                                                             self.title_ui.key_focus.maxlen)

                self.title_ui.key_focus.do_sound(1)

                self.title_ui.key_focus.text_obj.actual_width, self.title_ui.key_focus.text_obj.max_height = self.title_ui.key_focus.text_obj.get_text_height()
                self.title_ui.key_focus.text_obj.render()
                self.title_ui.key_focus.render()
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item is not None:
                return
            for i in range(len(self.title_ui.interactives) - 1, -1, -1):
                if self.title_ui.interactives[i].rendered_rect.collidepoint(self.mouse_pointer.xy):
                    if not self.title_ui.interactives[i].mouse_over:
                        self.title_ui.interactives[i].mouse_over = True
                else:
                    if self.title_ui.interactives[i].mouse_over:
                        self.title_ui.interactives[i].mouse_over = False
                        if self.title_ui.interactives[i].popup_active:
                            self.title_ui.interactives[i].popup_active = False
                            self.title_ui.interactives.remove(self.title_ui.interactives[i].popup_win)
                            self.title_ui.dated = True

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.title_ui.mouse_actions(mouse_x, mouse_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.title_ui.page:
            return
        # PAGE 0
        if element.id in ('input_name',) and m_bttn == 1 and mb_event == 'down':
            self.title_ui.key_focus = element
        elif element.id == 'new_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.title_ui.page = 1
            self.title_ui.key_focus = None
        elif element.id == 'exit' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            exit()
        elif element.id == 'test_start' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            l = maze.Maze(self.db, self.animations, 80, 80, 1, ['town', 'cave', 'forest'], self.title_ui.tilesets.get_maze_tiles('dung_default'))
            for r in l.array:
                print(*r)
            location = 'town'
            pc_x_sq = 1
            pc_y_sq = 1
            for i in range(0, len(l.exits)):
                if l.exits[i].dest == location or i == len(l.exits) - 1:
                    pc_x_sq = l.exits[i].x_sq
                    pc_y_sq = l.exits[i].y_sq
            char_sheet = charsheet.CharSheet(self.db, 'char_id', chr_name='Xenia', chr_type='champion', chr_level=1)
            p = pc.PC(pc_x_sq, pc_y_sq, location, self.animations.get_animation('anthro_default'), char_sheet, state=0)
            p.char_sheet.calc_stats()
            wins_dict['realm'].maze = l
            wins_dict['realm'].pc = p
            wins_dict['realm'].launch(pygame_settings.audio, settings, wins_dict, active_wins)
            active_wins.append(wins_dict['realm'])
            active_wins.remove(self)

        # PAGE 1
        # TAGGED RADIO BUTTON SWITCH GROUP
        if 'charswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down' and element.mode == 0:
                for inter in self.title_ui.interactives:
                    if inter == element:
                        if inter.text_obj.color != resources.colors['sun']:
                            inter.text_obj.color = resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()
                        continue
                    elif 'charswitch' in inter.tags:
                        inter.mode = 0
                        if inter.text_obj.color != resources.colors['fnt_muted']:
                            inter.text_obj.color = resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()
            """elif m_bttn == 1 and mb_event == 'up' and element.mode == 1:
                if element.text_obj.color != resources.colors['fnt_muted']:
                    element.text_obj.color = resources.colors['fnt_muted']
                    element.text_obj.render()
                    element.render()"""

        elif element.id == 'char_back' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.title_ui.page = 0
            self.title_ui.key_focus = None

        self.title_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        menu_btn_h = 40
        # MAIN MENU
        main_menu = (
            self.title_ui.button_add('new_char', caption='New Character', size=(256, menu_btn_h), cap_color='fnt_muted',
                                              sounds=self.title_ui.snd_packs['button']),
            self.title_ui.button_add('test_start', caption='Realm', size=(256, menu_btn_h), cap_color='fnt_muted',
                                     sounds=self.title_ui.snd_packs['button']),
            self.title_ui.button_add('exit', caption='Exit', size=(256, menu_btn_h), cap_color='fnt_muted',
                                     sounds=self.title_ui.snd_packs['button']),
        )
        for i in range(0, len(main_menu)):
            main_menu[i].tags = ['lightup']
            main_menu[i].page = 0
            main_menu[i].rendered_rect.left = round(menu_btn_h)
            main_menu[i].rendered_rect.centery = round(self.title_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i

        main_menu[-1].rendered_rect.centery = round(self.title_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # CHARACTER CHOICE
        char_menu = (
            self.title_ui.button_add('char_champion', caption='Champion', size=(256, menu_btn_h), cap_color='fnt_muted',
                                     sounds=self.title_ui.snd_packs['button'], switch=True),
            self.title_ui.button_add('char_kingslayer', caption='Kingslayer', size=(256, menu_btn_h), cap_color='fnt_muted',
                                     sounds=self.title_ui.snd_packs['button'], switch=True),
            self.title_ui.button_add('char_cosmologist', caption='Cosmologist', size=(256, menu_btn_h), cap_color='fnt_muted',
                                     sounds=self.title_ui.snd_packs['button'], switch=True),
            self.title_ui.button_add('char_back', caption='< back', size=(256, menu_btn_h),
                                     cap_color='fnt_muted', sounds=self.title_ui.snd_packs['button']),
        )
        for i in range(0, len(char_menu)):
            char_menu[i].tags = ['lightup', 'charswitch']
            char_menu[i].page = 1
            char_menu[i].rendered_rect.left = round(menu_btn_h)
            char_menu[i].rendered_rect.centery = round(self.title_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i

        char_menu[-1].rendered_rect.centery = round(self.title_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7
        char_menu[-1].tags = ['lightup']

        new_edit = self.title_ui.edit_add('input_name', (50, 100), sounds=self.title_ui.snd_packs['text_input'])
        new_edit.popup_win = self.title_ui.text_add('text', (50, 50), h_align='center', size=(320, 500),
                                                    cap_shadow=True)
        tag_string = self.title_ui.text_add('tag_string', (0, self.title_ui.pygame_settings.screen_res[1]-16), caption=settings.tag_string,
                                            h_align='left', v_align='bottom',
                                            size=(self.title_ui.pygame_settings.screen_res[0] // 4, 16), cap_color='sun')

        self.title_ui.interactives.extend(main_menu)
        self.title_ui.interactives.extend(char_menu)
        self.title_ui.interactives.append(new_edit)
        self.title_ui.interactives.append(tag_string)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.title_ui.tick(pygame_settings, mouse_pointer)

    def render_ui(self, surface):
        for decorative in reversed(self.title_ui.decoratives):
            if decorative.page is not None and decorative.page != self.title_ui.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.title_ui.interactives):
            if interactive.page is not None and interactive.page != self.title_ui.page:
                continue
            interactive.draw(surface)

    def draw(self, surface):
        self.render_ui(surface)
