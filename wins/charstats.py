# char stats window
import pygame
from library import textinput, pydraw, maths
from components import ui


class CharStats:
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

        self.pc = None
        self.win_w = 511
        self.win_h = 510
        self.offset_x = (pygame_settings.screen_res[0] - self.win_w) // 2
        self.offset_y = 16

        self.win_rendered = pygame.Surface((self.win_w, self.win_h)).convert()
        self.stat_elements = {}

        self.updated = False

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)
        self.updated = True

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.stat_elements.clear()

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

                self.win_ui.key_focus.text_obj.actual_width, self.win_ui.key_focus.text_obj.max_height = self.win_ui.key_focus.text_obj.get_text_height()
                self.win_ui.key_focus.text_obj.render()
                self.win_ui.key_focus.render()
            elif event.key == pygame.K_SPACE:
                pass

        elif event.type == pygame.MOUSEMOTION:
            # preparing popup panel on N-th cycle
            if self.mouse_pointer.drag_item:
                return
            if (not self.offset_x <= mouse_x < self.offset_x + self.win_w
                    or not self.offset_y <= mouse_y < self.offset_y + self.win_h):
                return False

            return True

        # return True if interaction was made to prevent other windows from responding to this event
        return self.ui_click(self.win_ui.mouse_actions(mouse_x - self.offset_x, mouse_y - self.offset_y, event))

    def ui_click(self, inter_click):
        if inter_click is None:
            return
        element, m_bttn, mb_event = inter_click

        if self.wins_dict['realm'] in self.active_wins and self.pc is not None:
            self.pc.move_instr_x = self.pc.move_instr_y = 0
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['charstats'])
                self.active_wins.insert(0, self.wins_dict['charstats'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in (self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'], self.wins_dict['inventory'], self.wins_dict['skillbook']) if fw in self.active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])

        # PAGE 0


        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.stat_elements.clear()

        stats_top = 60
        # INVENTORY
        chs_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        chs_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                  (self.resources.colors['gray_light'],
                             self.resources.colors['gray_dark'],
                             self.resources.colors['gray_mid'],
                             self.resources.colors['black']),
                                  sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                  sq_image=chs_texture)
        # BACKGROUND
        chs_image = pydraw.square((12, stats_top + 144),
                                  (244, self.win_h - 172 - 12 - 32),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=chs_image, same_surface=True)

        chs_image = pydraw.square((264, stats_top + 144),
                                  (self.win_w - 256 - 8 - 12, self.win_h - 172 - 12 - 32),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['gray_mid'],
                                   self.resources.colors['black']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                  sq_image=chs_image, same_surface=True)
        chs_panel = self.win_ui.panel_add('chs_panel', (0, 0), (self.win_w, self.win_h), images=(chs_image,), page=None)

        # window header
        header_texture = self.win_ui.random_texture((self.win_w, 19), 'red_glass')
        header_img = pydraw.square((0, 0), (self.win_w, 19),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['gray_darker']),
                                   sq_outsize=1, sq_bsize=1, sq_ldir=0, sq_fill=False,
                                   sq_image=header_texture)
        win_header = self.win_ui.text_add('win_header', (0, 0), (self.win_w, 19),
                                          caption='Character Sheet',
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))

        char_title_text = self.win_ui.text_add('char_title', (12, 28), (self.win_w - 24, 38),
                                                  caption='~ %s the %s ~' % (self.pc.char_sheet.name.capitalize(),
                                                                          self.pc.char_sheet.type.capitalize()),
                                                  h_align='center', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='large', cap_size=18)
        self.win_ui.decoratives.append(char_title_text)

        char_img_size = (120, 120)
        if self.pc.char_sheet.type == 'champion':
            cp_index = 0
        elif self.pc.char_sheet.type == 'kingslayer':
            cp_index = 1
        else:
            cp_index = 2
        decor_color = 'fnt_celeb'

        # char icon
        char_image = pygame.transform.scale(self.win_ui.tilesets.get_image('char_portraits', (60,60), (cp_index,))[0], char_img_size)
        char_img_w, char_img_h = char_img_size[0] + 16, char_img_size[1] + 16
        char_icon = pydraw.square((0, 0), (char_img_w, char_img_h),
                                  (self.resources.colors['gray_light'],
                                   self.resources.colors['gray_dark'],
                                   self.resources.colors['black'],
                                   self.resources.colors['gray_light']),
                                  sq_outsize=0, sq_bsize=1, sq_ldir=5, sq_fill=False,
                                  sq_image=None)
        char_icon.blit(char_image, (8, 8))
        char_icon_panel = self.win_ui.panel_add('icon_panel', (12, stats_top), (char_img_w, char_img_h), images=(char_icon,),
                                               page=None)

        y = stats_top + 4
        for attr_name, attr_value in self.pc.char_sheet.attributes.items():
            attr_val_mods = self.pc.char_sheet.calc_all_mods(attr_name)
            av_color = 'fnt_celeb'
            if attr_val_mods > 0:
                av_color = 'sun'
            elif attr_val_mods < 0:
                av_color = 'fnt_attent'
            av_caption = str(attr_value + attr_val_mods)
            if attr_val_mods > 0:
                av_caption += ' (+%s)' % (attr_val_mods)
            elif attr_val_mods < 0:
                av_caption += ' (%s)' % (attr_val_mods)

            attr_label_element = self.win_ui.text_add(attr_name, (160, y), (80, 24),
                                                      caption=(self.resources.stat_captions[attr_name][
                                                               :3]).upper() + ':',
                                                      h_align='left', v_align='top', cap_color=av_color,
                                                      cap_font='large', cap_size=15)
            attr_value_element = self.win_ui.text_add(attr_name, (232, y), (96, 24),
                                              caption=av_caption,
                                              h_align='left', v_align='top', cap_color='fnt_celeb',
                                              cap_font='large', cap_size=15)
            self.stat_elements[attr_name] = attr_value_element
            self.win_ui.decoratives.append(attr_label_element)
            self.win_ui.decoratives.append(attr_value_element)
            y += 20

        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 10), (124, 16),
                                                  caption='HP:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 10), (159, 16),
                                                  caption=str(self.pc.char_sheet.pools['HP']),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['HP'] = pool_label_element

        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 24), (124, 16),
                                                  caption='MP:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 24), (159, 16),
                                                  caption=str(self.pc.char_sheet.pools['MP']),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['MP'] = pool_label_element

        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 38), (124, 16),
                                                  caption='FOOD:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 38), (159, 16),
                                                  caption=str(self.pc.char_sheet.pools['FOOD']),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['FOOD'] = pool_label_element

        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 66), (124, 16),
                                                  caption='LEVEL:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 66), (159, 16),
                                                  caption=str(self.pc.char_sheet.level),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['level'] = pool_label_element

        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 80), (124, 16),
                                                  caption='EXPERIENCE:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 94), (159, 16),
                                                  caption=str(self.pc.char_sheet.experience),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['experience'] = pool_label_element
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 108), (144, 16),
                                                  caption='EXP NEXT LEVEL:',
                                                  h_align='left', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        pool_label_element = self.win_ui.text_add('pool', (340, stats_top + 122), (159, 16),
                                                  caption=str(self.pc.char_sheet.exp_next_lvl),
                                                  h_align='right', v_align='top', cap_color='fnt_celeb',
                                                  cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(pool_label_element)
        self.stat_elements['exp_next_lvl'] = pool_label_element


        att_label_element = self.win_ui.text_add('attacks', (20, stats_top + 152), (164, 16),
                                                 caption='Attacks:',
                                                 h_align='left', v_align='top', cap_color='fnt_celeb',
                                                 cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(att_label_element)
        def_label_element = self.win_ui.text_add('defences', (20, stats_top + 280), (164, 16),
                                                 caption='Defences:',
                                                 h_align='left', v_align='top', cap_color='fnt_celeb',
                                                 cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(def_label_element)
        prof_label_element = self.win_ui.text_add('profs', (272, stats_top + 152), (164, 16),
                                                 caption='Properties:',
                                                 h_align='left', v_align='top', cap_color='fnt_celeb',
                                                 cap_font='def_bold', cap_size=24)
        self.win_ui.decoratives.append(prof_label_element)

        y = stats_top + 168
        for att_name, att_value in self.pc.char_sheet.attacks.items():
            av_color = 'fnt_celeb'
            if isinstance(att_value, int):
                av_caption = str(att_value)
            else:
                av_caption = '%s-%s' % (att_value[0], att_value[1])

            att_label_element = self.win_ui.text_add(att_name, (20, y), (96, 16),
                                                      caption=(self.resources.stat_captions[att_name].split()[0]) + ':',
                                                      h_align='left', v_align='top', cap_color='fnt_celeb',
                                                      cap_font='def_normal', cap_size=24)
            att_value_element = self.win_ui.text_add(att_name, (116, y), (64, 16),
                                                      caption=av_caption,
                                                      h_align='left', v_align='top', cap_color=av_color,
                                                      cap_font='def_normal', cap_size=24)
            self.stat_elements[att_name] = att_value_element
            self.win_ui.decoratives.append(att_label_element)
            self.win_ui.decoratives.append(att_value_element)
            y += 14

        y = stats_top + 298
        for def_name, def_value in self.pc.char_sheet.defences.items():
            dv_color = 'fnt_celeb'

            def_value_percent = def_value / 10
            if def_value_percent.is_integer():
                dv_caption = str(round(def_value_percent))
            else:
                dv_caption = str(round(def_value / 10, 1))

            def_label_element = self.win_ui.text_add(def_name, (20, y), (96, 16),
                                                     caption=(self.resources.stat_captions[def_name].split()[
                                                         0]) + ':',
                                                     h_align='left', v_align='top', cap_color='fnt_celeb',
                                                     cap_font='def_normal', cap_size=24)
            def_value_element = self.win_ui.text_add(def_name, (116, y), (64, 16),
                                                     caption=dv_caption,
                                                     h_align='left', v_align='top', cap_color=dv_color,
                                                     cap_font='def_normal', cap_size=24)
            self.stat_elements[def_name] = def_value_element
            self.win_ui.decoratives.append(def_label_element)
            self.win_ui.decoratives.append(def_value_element)
            y += 14

        y = stats_top + 168
        for prof_name, prof_value in self.pc.char_sheet.profs.items():
            pv_color = 'fnt_celeb'

            prof_value_percent = prof_value / 10
            if prof_value_percent.is_integer():
                pv_caption = str(round(prof_value_percent))
            else:
                pv_caption = str(round(prof_value / 10, 1))

            prof_label_element = self.win_ui.text_add(prof_name, (272, y), (144, 16),
                                                     caption=self.resources.stat_captions[prof_name] + ':',
                                                     h_align='left', v_align='top', cap_color='fnt_celeb',
                                                     cap_font='def_normal', cap_size=24)
            prof_value_element = self.win_ui.text_add(prof_name, (416, y), (48, 16),
                                                     caption=pv_caption,
                                                     h_align='left', v_align='top', cap_color=pv_color,
                                                     cap_font='def_normal', cap_size=24)
            self.stat_elements[prof_name] = prof_value_element
            self.win_ui.decoratives.append(prof_label_element)
            self.win_ui.decoratives.append(prof_value_element)
            y += 14

        self.win_ui.decoratives.append(char_icon_panel)
        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(chs_panel)

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render(self, chs=True):
        # update
        for attr_name, attr_value in self.pc.char_sheet.attributes.items():
            attr_val_mods = self.pc.char_sheet.calc_all_mods(attr_name)
            av_color = self.resources.colors['fnt_celeb']
            if attr_val_mods > 0:
                av_color = self.resources.colors['sun']
            elif attr_val_mods < 0:
                av_color = self.resources.colors['fnt_attent']
            av_caption = str(attr_value + attr_val_mods)
            if attr_val_mods > 0:
                av_caption += ' (+%s)' % (attr_val_mods)
            elif attr_val_mods < 0:
                av_caption += ' (%s)' % (attr_val_mods)
            if (self.stat_elements[attr_name].text_obj.caption != av_caption or
                    self.stat_elements[attr_name].text_obj.color != av_color):
                self.stat_elements[attr_name].text_obj.caption = av_caption
                self.stat_elements[attr_name].text_obj.color = av_color
                self.stat_elements[attr_name].render_all()

            if self.stat_elements['level'].text_obj.caption != str(self.pc.char_sheet.level):
                self.stat_elements['level'].text_obj.caption = str(self.pc.char_sheet.level)
                self.stat_elements['level'].render_all()
            if self.stat_elements['HP'].text_obj.caption != str(self.pc.char_sheet.pools['HP']):
                self.stat_elements['HP'].text_obj.caption = str(self.pc.char_sheet.pools['HP'])
                self.stat_elements['HP'].render_all()
            if self.stat_elements['MP'].text_obj.caption != str(self.pc.char_sheet.pools['MP']):
                self.stat_elements['MP'].text_obj.caption = str(self.pc.char_sheet.pools['MP'])
                self.stat_elements['MP'].render_all()
            if self.stat_elements['FOOD'].text_obj.caption != str(self.pc.char_sheet.pools['FOOD']):
                self.stat_elements['FOOD'].text_obj.caption = str(self.pc.char_sheet.pools['FOOD'])
                self.stat_elements['FOOD'].render_all()
            if self.stat_elements['experience'].text_obj.caption != str(self.pc.char_sheet.experience):
                self.stat_elements['experience'].text_obj.caption = str(self.pc.char_sheet.experience)
                self.stat_elements['experience'].render_all()
            if self.stat_elements['exp_next_lvl'].text_obj.caption != str(self.pc.char_sheet.exp_next_lvl):
                self.stat_elements['exp_next_lvl'].text_obj.caption = str(self.pc.char_sheet.exp_next_lvl)
                self.stat_elements['exp_next_lvl'].render_all()

            for att_name, att_value in self.pc.char_sheet.attacks.items():
                av_color = self.resources.colors['fnt_celeb']
                if isinstance(att_value, int):
                    av_caption = str(round(att_value / 10, 1)) + '%'
                else:
                    av_caption = '%s-%s' % (att_value[0], att_value[1])
                if (self.stat_elements[att_name].text_obj.caption != av_caption or
                        self.stat_elements[att_name].text_obj.color != av_color):
                    self.stat_elements[att_name].text_obj.caption = av_caption
                    self.stat_elements[att_name].text_obj.color = av_color
                    self.stat_elements[att_name].render_all()

            for def_name, def_value in self.pc.char_sheet.defences.items():
                dv_color = self.resources.colors['fnt_celeb']

                if def_name in ('def_melee', 'def_ranged'):
                    def_value_percent = def_value / 10
                    if def_value_percent.is_integer():
                        dv_caption = str(round(def_value_percent)) + '%'
                    else:
                        dv_caption = str(round(def_value / 10, 1)) + '%'
                else:
                    dv_caption = str(def_value) + ''
                if (self.stat_elements[def_name].text_obj.caption != dv_caption or
                        self.stat_elements[def_name].text_obj.color != dv_color):
                    self.stat_elements[def_name].text_obj.caption = dv_caption
                    self.stat_elements[def_name].text_obj.color = dv_color
                    self.stat_elements[def_name].render_all()

            for prof_name, prof_value in self.pc.char_sheet.profs.items():
                pv_color = self.resources.colors['fnt_celeb']

                prof_value_percent = prof_value / 10
                if prof_value_percent == 0:
                    pv_caption = '.'
                elif prof_value_percent.is_integer():
                    pv_caption = '+' * (prof_value_percent > 0) + str(round(prof_value_percent)) + '%'
                else:
                    pv_caption = '+' * (prof_value_percent > 0) + str(round(prof_value / 10, 1)) + '%'
                if (self.stat_elements[prof_name].text_obj.caption != pv_caption or
                        self.stat_elements[prof_name].text_obj.color != pv_color):
                    self.stat_elements[prof_name].text_obj.caption = pv_caption
                    self.stat_elements[prof_name].text_obj.color = pv_color
                    self.stat_elements[prof_name].render_all()

        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))

