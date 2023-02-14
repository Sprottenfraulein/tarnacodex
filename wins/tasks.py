# char stats window
import pygame
import random
from library import textinput, pydraw, maths, calc2darray, pickrandom
from components import ui, textinserts, dbrequests, chest, treasure


class Tasks:
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
        self.task_selected = None
        self.task_desc = None
        self.task_reqs = []
        self.bttn_complete = None

        self.updated = False

        self.TASK_EXP_REWARD_BASE = 100

    def launch(self, pc):
        self.pc = pc
        self.create_elements(log=True)
        self.updated = True

    def end(self):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()
        self.task_reqs.clear()
        self.task_selected = None
        self.bttn_complete.enabled = False

    def restart(self):
        self.end()
        self.launch(self.pc)

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
            in_realm = True
        else:
            in_realm = False
        # dragging window
        if element.id == 'win_header' and m_bttn == 1:
            if mb_event == 'down':
                self.mouse_pointer.drag_ui = (self, self.mouse_pointer.xy[0] - self.offset_x,
                                              self.mouse_pointer.xy[1] - self.offset_y)
                self.active_wins.remove(self.wins_dict['tasks'])
                self.active_wins.insert(0, self.wins_dict['tasks'])
            if mb_event == 'up':
                self.mouse_pointer.drag_ui = None
                framed_wins = [fw for fw in (
                    self.wins_dict['charstats'], self.wins_dict['pools'], self.wins_dict['hotbar'],
                    self.wins_dict['inventory'], self.wins_dict['skillbook'], self.wins_dict['tasks']
                ) if fw in self.active_wins]
                self.offset_x, self.offset_y = maths.rect_sticky_edges(
                    (self.offset_x, self.offset_y, self.win_w, self.win_h),
                    [(ow.offset_x, ow.offset_y, ow.win_w, ow.win_h) for ow in framed_wins])
                self.offset_x, self.offset_y = maths.rect_in_bounds(self.offset_x, self.offset_y, self.win_w,
                                                                    self.win_h,
                                                                    0, 0, self.pygame_settings.screen_res[0],
                                                                    self.pygame_settings.screen_res[1])
        elif element.id == 'win_header' and m_bttn == 3 and mb_event == 'down':
            self.active_wins.remove(self)
            self.end()
            if in_realm:
                targ_win = self.wins_dict['pools']
                bttn_id = 'miss'
            else:
                targ_win = self.wins_dict['app_title']
                bttn_id = 'quick_miss'
            for el in targ_win.win_ui.interactives:
                if el.id == bttn_id:
                    el.mouse_up(1)
            self.wins_dict['pools'].updated = in_realm

        if element.id == 'bttn_task':
            if m_bttn == 1 and mb_event == 'down':
                for inter in self.win_ui.interactives:
                    if inter == element and element.mode == 0:
                        self.task_desc_update(element.tags[0])

                        if inter.text_obj.color != self.resources.colors['sun']:
                            inter.text_obj.color = self.resources.colors['sun']
                            inter.text_obj.render()
                            inter.render()

                        self.updated = True
                    elif inter != element and inter.id == 'bttn_task':
                        inter.mode = 0
                        if inter.text_obj.color != self.resources.colors['fnt_muted']:
                            inter.text_obj.color = self.resources.colors['fnt_muted']
                            inter.text_obj.render()
                            inter.render()
                        inter.render()
            if m_bttn == 1 and mb_event == 'up':
                # Preventing button interaction callback from calling a mouse up in button object.
                return True

        if element.id == 'bttn_complete' and self.bttn_complete.enabled:
            if m_bttn == 1 and mb_event == 'up':
                if not in_realm:
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': 'You must have the boots on the ground to submit a task.',
                        'bttn_cancel': 'OK'
                    }
                    self.wins_dict['dialogue'].launch(self.pc)
                elif self.pc.char_sheet.mission_task_check(self.task_selected):
                    self.reward(self.task_selected)
                else:
                    self.wins_dict['dialogue'].dialogue_elements = {
                        'header': 'Attention',
                        'text': 'Requirements are not met! The task may not be completed yet.',
                        'bttn_cancel': 'OK'
                    }
                    self.wins_dict['dialogue'].launch(self.pc)

        self.win_ui.updated = True
        self.win_ui.interaction_callback(element, mb_event, m_bttn)
        # return True if interaction was made to prevent other windows from responding to this event
        return True

    # interface creation
    def create_elements(self, log=True):
        self.win_ui.decoratives.clear()
        self.win_ui.interactives.clear()

        frames_top = 70
        # INVENTORY
        miss_texture = self.win_ui.random_texture((self.win_w, self.win_h), 'black_rock')
        miss_image = pydraw.square((0, 0), (self.win_w, self.win_h),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['black']),
                                   sq_outsize=1, sq_bsize=2, sq_ldir=0, sq_fill=False,
                                   sq_image=miss_texture)

        # BACKGROUND
        miss_image = pydraw.square((12, frames_top),
                                   (224, self.win_h - frames_top - 12 - 60),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['black']),
                                   sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                   sq_image=miss_image, same_surface=True)

        miss_image = pydraw.square((244, frames_top),
                                   (self.win_w - 236 - 8 - 12, self.win_h - frames_top - 12 - 60),
                                   (self.resources.colors['gray_light'],
                                    self.resources.colors['gray_dark'],
                                    self.resources.colors['gray_mid'],
                                    self.resources.colors['black']),
                                   sq_outsize=0, sq_bsize=1, sq_ldir=2, sq_fill=False,
                                   sq_image=miss_image, same_surface=True)

        miss_panel = self.win_ui.panel_add('miss_panel', (0, 0), (self.win_w, self.win_h), images=(miss_image,))

        list_header = self.win_ui.text_add(
            'str_task_list', (12, 42), caption='Active tasks:', h_align='center', v_align='top',
            size=(224, 28), cap_color='fnt_celeb', cap_font='large', cap_size=14
        )
        self.win_ui.decoratives.append(list_header)
        desc_header = self.win_ui.text_add(
            'str_task_desc', (244, 42), caption='Task description:', h_align='center', v_align='top',
            size=(self.win_w - 236 - 8 - 12, 28), cap_color='fnt_celeb', cap_font='large', cap_size=14
        )
        self.win_ui.decoratives.append(desc_header)

        self.task_desc = self.win_ui.text_add(
            'task_desc', (246, frames_top + 2),
            caption='Click a task button on the left panel to watch its description.',
            h_align='left', v_align='top', size=(self.win_w - 236 - 8 - 8, 48),
            cap_color='fnt_celeb', cap_font='def_normal', cap_size=24
        )
        self.win_ui.decoratives.append(self.task_desc)

        bttn_h = 24
        tasks_list = []
        miss_index = 0
        for miss_id, miss_props in self.pc.char_sheet.missions.items():
            if 'complete' in miss_props and miss_props['once'] == 1:
                continue
            if 'complete' in miss_props and miss_props['once'] == 0 and miss_props['complete'] >= miss_props['lvl']:
                continue
            new_bttn = self.win_ui.button_add(
                'bttn_task', caption='%s, lv.%s' % (miss_props['label'], miss_props['lvl']), size=(220, bttn_h),
                cap_font='def_bold', cap_size=24, cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'],
                page=None, tags=(miss_props,), switch=True)
            new_bttn.rendered_rect.topleft = (12 + 2, frames_top + 2 + bttn_h * miss_index)
            tasks_list.append(new_bttn)
            miss_index += 1
        self.win_ui.interactives.extend(tasks_list)

        self.bttn_complete = self.win_ui.button_add('bttn_complete', caption='Submit task', xy=(244, self.win_h - 60),
                                               size=(self.win_w - 236 - 8 - 12, 40),
                                            cap_font='large', cap_size=16,
                                            cap_color='fnt_muted', sounds=self.win_ui.snd_packs['button'], page=None)
        self.bttn_complete.enabled = False
        self.win_ui.interactives.append(self.bttn_complete)

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
                                          caption='Tasks',
                                          h_align='center', v_align='middle', cap_color='sun', images=(header_img,))
        self.win_ui.interactives.append(win_header)
        self.win_ui.decoratives.append(miss_panel)

    def task_desc_update(self, task_props):
        # Clear existing desc elements
        if self.task_reqs is not None:
            for itm in self.task_reqs:
                if itm in self.win_ui.decoratives:
                    self.win_ui.decoratives.remove(itm)
                if itm in self.win_ui.interactives:
                    self.win_ui.decoratives.remove(itm)
            self.task_reqs.clear()

        # Creating new elements and changing text description.
        self.task_desc.text_obj.caption = (
                '%s $n $n Completion requirements $n '
                '(All items must be level %s or higher):'
                % (textinserts.insert(self.wins_dict['realm'], self.pc, (task_props['desc'])),
                   task_props['lvl'])
        )
        self.task_desc.render_all()

        task_list = dbrequests.mission_tasks_get(self.db.cursor, [task[0] for task in task_props['tasks']])

        for i in range(0, len(task_list)):
            # Search task list for amount
            for tsk_id, tsk_amount in task_props['tasks']:
                if tsk_id == task_list[i]['treasure_id']:
                    amount = tsk_amount
                    break
            else:
                amount = 0
            # Creating elements
            req_image = self.win_ui.tilesets.get_image(
                task_list[i]['tileset'], (task_list[i]['width'], task_list[i]['height']), (task_list[i]['index'],)
            )[0]
            req_panel = self.win_ui.panel_add(
                'req_panel', (246, self.task_desc.rendered_rect.bottom + 32 + 56 * i), (48, 48), images=(req_image,),
                img_stretch=True
            )
            self.win_ui.decoratives.insert(0, req_panel)
            self.task_reqs.append(req_panel)
            req_text = self.win_ui.text_add(
                'req_text', (298, self.task_desc.rendered_rect.bottom + 32 + 56 * i + 18),
                caption='%s x%s' % (task_list[i]['label'], amount),
                h_align='left', size=(self.win_w - 236 - 8 - 8 - 52, 24),
                cap_color='fnt_celeb', cap_font='def_normal', cap_size=24
            )
            self.win_ui.decoratives.insert(0, req_text)
            self.task_reqs.append(req_text)

        self.task_selected = task_props
        self.bttn_complete.enabled = True
        self.updated = True

    def reward(self, mission):
        self.wins_dict['inventory'].updated = True
        self.pc.char_sheet.experience_get(
            self.wins_dict, self.pc, mission['lvl'],
            self.TASK_EXP_REWARD_BASE * mission['reward_exp'] // 100 * mission['lvl']
        )
        x_sq = self.pc.x_sq
        y_sq = self.pc.y_sq
        for ex in self.wins_dict['realm'].maze.exits:
            if ex.dest == 'up':
                x_sq, y_sq = ex.x_sq, ex.y_sq
        space_list = calc2darray.fill2d(
            self.wins_dict['realm'].maze.flag_array, {'mov': False, 'obj': 'True', 'floor': False},
            (x_sq, y_sq), (round(self.pc.x_sq), round(self.pc.y_sq)), 2, 5, r_max=5
        )
        x_sq, y_sq = space_list[1]
        alignment = random.choice((0, 1))
        new_chest = chest.Chest(
            x_sq, y_sq, alignment, None, self.wins_dict['realm'].maze.tile_set, off_x=-4, off_y=-4,
            lvl=mission['lvl'], items_number=mission['reward_treasure_amount'], gp_number=mission['reward_gold_piles'],
            treasure_group=mission['reward_treasure_group'], item_type=None, char_type=(self.pc.char_sheet.type,),
            container=self.reward_treasure_get(mission), disappear=True, allow_mimic=False
        )
        self.wins_dict['realm'].maze.chests.append(new_chest)
        self.wins_dict['realm'].maze.chests.append(new_chest)
        self.wins_dict['realm'].maze.flag_array[y_sq][x_sq].obj = new_chest
        self.wins_dict['realm'].maze.flag_array[y_sq][x_sq].mov = False
        self.wins_dict['realm'].obj_jump_add(new_chest)
        self.wins_dict['realm'].sound_inrealm('item_throw', x_sq, y_sq)

        self.pc.char_sheet.missions[mission['mission_id']]['complete'] = self.pc.char_sheet.level
        self.task_selected = None
        self.bttn_complete.enabled = False

        # Run demo if exists.
        text_list, image_list = dbrequests.chapter_demo_get(self.db.cursor, self.pc.location[0]['chapter_id'], mission['demo_tag'])
        if (len(text_list) + len(image_list)) > 0:
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['demos'], 'demo_run',
                                                              (self.pc, text_list, image_list, False))
            self.wins_dict['app_title'].schedule_man.task_add('realm_tasks', 2, self.wins_dict['overlay'], 'fade_in',
                                                              (20, None))

        if not self.wins_dict['realm'].maze.flag_array[y_sq][x_sq].vis:
            self.wins_dict['realm'].schedule_man.task_add('realm_tasks', 1, self, 'shipment_reminder', ())
        self.restart()

    def shipment_reminder(self):
        self.wins_dict['dialogue'].dialogue_elements = {
            'header': 'Attention',
            'text': 'Your package awaits you near the upstairs of the current floor!',
            'bttn_cancel': 'OK'
        }
        self.wins_dict['dialogue'].launch(self.pc)

    def reward_treasure_get(self, mission):
        treasure_list = [self.reward_manuscript_get(mission)]
        for tr_id, amount in mission['non_rnd_reward']:
            for i in range(0, amount):
                new_tr = treasure.Treasure(
                    tr_id, mission['lvl'], self.db.cursor, self.tilesets,  self.resources, self.pygame_settings.audio,
                    self.resources.fate_rnd, grade=1
                )
                treasure.loot_validate(new_tr.props)
                treasure_list.append(new_tr)

                # SPECIAL MANUSCRIPT STATEMENT
                if new_tr.props['item_type'] == 'misc_man':  # Manuscript item treasure_id
                    rnd_roll = random.randrange(1, 10001)
                    mans_list = [
                        (mn, mn['roll_chance'])
                        for mn in dbrequests.manuscript_get(
                            self.db.cursor, (new_tr.props['class'],), new_tr.props['lvl'], rnd_roll
                        )
                    ]
                    if len(mans_list) == 0:
                        del treasure_list[-1]
                    else:
                        new_tr.props['desc'] = textinserts.insert(self, self.pc, pickrandom.items_get(mans_list, 1)[0]['desc'])
        return treasure_list

    def reward_manuscript_get(self, mission):
        new_man = treasure.Treasure(
            107, mission['lvl'], self.wins_dict['realm'].db.cursor, self.wins_dict['realm'].tilesets,
                self.wins_dict['realm'].resources, self.wins_dict['realm'].pygame_settings.audio,
                self.wins_dict['realm'].resources.fate_rnd,
                findmagic=self.pc.char_sheet.profs['prof_findmagic']
        )
        # SPECIAL MANUSCRIPT STATEMENT
        new_man.props['desc'] = textinserts.insert(
            self.wins_dict['realm'], self.pc,
            dbrequests.manuscript_get_by_id(
                self.wins_dict['realm'].db.cursor, mission['reward_manuscript_id']
            )['desc']
        )
        return new_man

    def tick(self):
        self.win_ui.tick()
        if self.win_ui.updated or self.updated:
            self.render()

    def render(self):
        self.win_ui.draw(self.win_rendered)
        self.updated = False

    def draw(self, surface):
        surface.blit(self.win_rendered, (self.offset_x, self.offset_y))

