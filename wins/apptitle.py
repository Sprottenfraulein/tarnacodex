# game title window
import pygame
import settings
import random
from library import textinput
from components import maze, pc, charsheet, ui, skill, treasure


class AppTitle:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.win_w = 10
        self.win_h = 10
        self.offset_x = 0
        self.offset_y = 0
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.win_ui = ui.UI(pygame_settings, resources, tilesets, db)
        self.create_elements(log=True)

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        mouse_x, mouse_y = self.mouse_pointer.xy
        if event.type == pygame.KEYDOWN:
            if self.win_ui.key_focus is not None:
                if self.win_ui.key_focus.page is not None and self.win_ui.key_focus.page != self.win_ui.page:
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

                self.win_ui.key_focus.text_obj.actual_width, self.win_ui.key_focus.text_obj.max_height = self.win_ui.key_focus.text_obj.get_text_height()
                self.win_ui.key_focus.text_obj.render()
                self.win_ui.key_focus.render()
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
        return self.ui_click(self.win_ui.mouse_actions(mouse_x, mouse_y, event),
                             pygame_settings, resources, wins_dict, active_wins)

    def ui_click(self, inter_click, pygame_settings, resources, wins_dict, active_wins):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click
        if element.page is not None and element.page != self.win_ui.page:
            return
        # PAGE 0
        if element.id in ('input_name',) and m_bttn == 1 and mb_event == 'down':
            self.win_ui.key_focus = element
        elif element.id == 'new_char' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            self.win_ui.page = 1
            self.win_ui.key_focus = None
        elif element.id == 'exit' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            exit()
        elif element.id == 'test_start' and m_bttn == 1 and mb_event == 'up' and element.mode == 1:
            l = maze.Maze(self.db, self.animations, 80, 80, 1, ['cave', 'forest'],
                          self.win_ui.tilesets.get_maze_tiles('dung_default'),
                          monster_types=None, monster_type_amount=2, monster_amount_rate=1)
            for r in l.array:
                print(*r)
            location = 'town'
            pc_x_sq = 1
            pc_y_sq = 1
            for i in range(0, len(l.exits)):
                if l.exits[i].dest == location or i == len(l.exits) - 1:
                    pc_x_sq = random.randrange(l.exits[i].room.left, l.exits[i].room.right)
                    pc_y_sq = random.randrange(l.exits[i].room.top, l.exits[i].room.bottom)
                    break
            char_sheet = charsheet.CharSheet(self.db, 'char_id', chr_name='Xenia', chr_type='champion', chr_level=1)
            p = pc.PC(pc_x_sq, pc_y_sq, location, self.animations.get_animation('anthro_default'), char_sheet, state=0)

            p.char_sheet.hotbar[-2] = skill.Skill(1, self.db.cursor, self.win_ui.tilesets, resources, pygame_settings.audio)
            p.char_sheet.hotbar[-1] = skill.Skill(2, self.db.cursor, self.win_ui.tilesets, resources,
                                                  pygame_settings.audio)
            p.char_sheet.equipped[2][0] = treasure.Treasure(3, self.db.cursor, self.win_ui.tilesets, resources, pygame_settings.audio,
                                                            resources.fate_rnd)

            p.char_sheet.calc_stats()
            p.char_sheet.hp_get(100, percent=True)
            p.char_sheet.mp_get(100, percent=True)
            p.char_sheet.food_get(100, percent=True)
            wins_dict['realm'].maze = l
            wins_dict['realm'].pc = p
            wins_dict['realm'].launch(pygame_settings.audio, settings, wins_dict, active_wins)
            active_wins.append(wins_dict['realm'])
            active_wins.remove(self)

        # PAGE 1
        # TAGGED RADIO BUTTON SWITCH GROUP
        if 'charswitch' in element.tags:
            if m_bttn == 1 and mb_event == 'down' and element.mode == 0:
                for inter in self.win_ui.interactives:
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
            self.win_ui.page = 0
            self.win_ui.key_focus = None

        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        menu_btn_h = 40
        # MAIN MENU
        main_menu = (
            self.win_ui.button_add('new_char', caption='New Character', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
            self.win_ui.button_add('test_start', caption='Realm', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
            self.win_ui.button_add('exit', caption='Exit', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button']),
        )
        for i in range(0, len(main_menu)):
            main_menu[i].tags = ['lightup']
            main_menu[i].page = 0
            main_menu[i].rendered_rect.left = round(menu_btn_h)
            main_menu[i].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i

        main_menu[-1].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (
                    menu_btn_h * 1.2) * 7

        # CHARACTER CHOICE
        char_menu = (
            self.win_ui.button_add('char_champion', caption='Champion', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], switch=True),
            self.win_ui.button_add('char_kingslayer', caption='Kingslayer', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], switch=True),
            self.win_ui.button_add('char_cosmologist', caption='Cosmologist', size=(256, menu_btn_h), cap_color='fnt_muted',
                                   sounds=self.win_ui.snd_packs['button'], switch=True),
            self.win_ui.button_add('char_back', caption='< back', size=(256, menu_btn_h),
                                   cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button']),
        )
        for i in range(0, len(char_menu)):
            char_menu[i].tags = ['lightup', 'charswitch']
            char_menu[i].page = 1
            char_menu[i].rendered_rect.left = round(menu_btn_h)
            char_menu[i].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * i

        char_menu[-1].rendered_rect.centery = round(self.win_ui.pygame_settings.screen_res[1] / 2) + (menu_btn_h * 1.2) * 7
        char_menu[-1].tags = ['lightup']

        new_edit = self.win_ui.edit_add('input_name', (50, 100), sounds=self.win_ui.snd_packs['text_input'])
        new_edit.popup_win = self.win_ui.text_add('text', (50, 50), h_align='center', size=(320, 500),
                                                  cap_shadow=True)
        tag_string = self.win_ui.text_add('tag_string', (0, self.win_ui.pygame_settings.screen_res[1] - 16), caption=settings.tag_string,
                                          h_align='left', v_align='bottom',
                                          size=(self.win_ui.pygame_settings.screen_res[0] // 4, 16), cap_color='sun')

        self.win_ui.interactives.extend(main_menu)
        self.win_ui.interactives.extend(char_menu)
        self.win_ui.interactives.append(new_edit)
        self.win_ui.interactives.append(tag_string)

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        self.win_ui.tick(pygame_settings, mouse_pointer)

    def render_ui(self, surface):
        for decorative in reversed(self.win_ui.decoratives):
            if decorative.page is not None and decorative.page != self.win_ui.page:
                continue
            decorative.draw(surface)
        for interactive in reversed(self.win_ui.interactives):
            if interactive.page is not None and interactive.page != self.win_ui.page:
                continue
            interactive.draw(surface)

    def draw(self, surface):
        self.render_ui(surface)
