# cutscenes window
import pygame
import settings
from components import dbrequests
from library import pydraw, maths, typography, panel


class Demos:
    def __init__(self, pygame_settings, resources, tile_sets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.pygame_settings = pygame_settings
        self.resources = resources
        self.tile_sets = tile_sets
        self.mouse_pointer = mouse_pointer
        self.schedule_man = schedule_man
        self.animations = animations
        self.offset_x = 0
        self.offset_y = 0
        self.width, self.height = pygame_settings.screen_res

        self.picture_list = []
        self.text_list = []
        self.pause = False
        self.pausable = False

    def event_check(self, event, pygame_settings, resources, wins_dict, active_wins, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN) and self.pausable:
            self.pause = 1 - self.pause
            self.schedule_man.pause = 1 - self.schedule_man.pause

    def image_add(self, panel_obj, duration, speed=None, fade_in=0, fade_out=0):
        if speed is None:
            speed = (0, 0)
        self.picture_list.append([panel_obj, duration, 0, speed, fade_in, fade_out])

    def text_add(self, text_obj, duration, speed=None, fade_in=0, fade_out=0):
        if speed is None:
            speed = (0,0)
        self.text_list.append([text_obj, duration, 0, speed, fade_in, fade_out])

    def demo_run(self, wins_dict, active_wins, text_list, image_list, gameover=False):
        self.width, self.height = self.pygame_settings.screen_res
        active_wins.clear()
        active_wins.extend([wins_dict['overlay'], wins_dict['demos']])
        self.pausable = True

        time_ending = 1

        for cap in text_list:
            text_obj = typography.Typography(self.pygame_settings, cap['text'],
                                             (self.width * cap['x'] // 100, self.height * cap['y'] // 100),
                                             cap['font_name'], cap['font_size'], self.resources.colors[cap['font_color_name']],
                                             self.resources.colors['bg'], cap['align_h'], 'top',
                                             self.width * cap['width'] // 100, 48)
            wins_dict['app_title'].schedule_man.task_add('realm_tasks', cap['schedule_delta'], wins_dict['demos'], 'text_add',
                                                         (text_obj, cap['duration'], (cap['speed_x'], cap['speed_y']),
                                                          cap['fade_in'], cap['fade_out']))
            if cap['music_name'] is not None:
                wins_dict['app_title'].schedule_man.task_add(
                    'realm_tasks', cap['schedule_delta'],  wins_dict['demos'].pygame_settings.audio,
                    'music', (cap['music_name'])
                )
            if cap['sound_name'] is not None:
                wins_dict['app_title'].schedule_man.task_add(
                    'realm_tasks', cap['schedule_delta'],  wins_dict['demos'].pygame_settings.audio,
                    'sound', (cap['sound_name'])
                )
            time_ending = max(time_ending, cap['schedule_delta'] * self.schedule_man.ticks_per_round + cap['duration'])
        for img in image_list:
            images = self.tile_sets.get_image(img['image']['tileset'], (img['image']['width'], img['image']['height']), (img['image']['index'],))[0]
            img_panel = panel.Panel(None, (self.width * img['x'] // 100, self.height * img['y'] // 100),
                                    (img['image']['width'] * img['image']['scale_h'],
                                     img['image']['height'] * img['image']['scale_v']),
                                    pan_images=images, page=None, img_stretch=True)
            wins_dict['app_title'].schedule_man.task_add('realm_tasks', img['schedule_delta'], wins_dict['demos'], 'image_add',
                                                         (img_panel, img['duration'], (img['speed_x'], img['speed_y']),
                                                          img['fade_in'], img['fade_out']))
            if img['music_name'] is not None:
                wins_dict['app_title'].schedule_man.task_add(
                    'realm_tasks', img['schedule_delta'],  wins_dict['demos'].pygame_settings.audio,
                    'music', (img['music_name'])
                )
            if img['sound_name'] is not None:
                wins_dict['app_title'].schedule_man.task_add(
                    'realm_tasks', img['schedule_delta'],  wins_dict['demos'].pygame_settings.audio,
                    'sound', (img['sound_name'])
                )
            time_ending = max(time_ending, img['schedule_delta'] * self.schedule_man.ticks_per_round + img['duration'])

        schedule_delta_ending = time_ending // self.schedule_man.ticks_per_round + 3
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', schedule_delta_ending, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, self.schedule_man.ticks_per_round, None))
        if gameover:
            wins_dict['app_title'].schedule_man.task_add('realm_tasks', schedule_delta_ending + 1, wins_dict['demos'],
                                                         'back_to_title', (wins_dict, active_wins))
        else:
            wins_dict['app_title'].schedule_man.task_add('realm_tasks', schedule_delta_ending + 1, wins_dict['demos'],
                                                         'back_to_game', (wins_dict, active_wins))

        wins_dict['app_title'].schedule_man.task_add('realm_tasks', schedule_delta_ending + 1, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, self.schedule_man.ticks_per_round, None))

    def death_soft(self, wins_dict, active_wins, pc, chapter_dict):
        self.width, self.height = self.pygame_settings.screen_res
        wins_dict['realm'].pause = True

        wins_dict['app_title'].char_save(pc, wins_dict['realm'].maze)

        active_wins.clear()
        active_wins.extend([wins_dict['demos'], wins_dict['realm']])
        self.pausable = False

        text_obj_1 = typography.Typography(self.pygame_settings,
                                         """YOU DIED""",
                                         (self.width // 2, self.height // 2 - 64), 'large', 64,
                                         self.resources.colors['bloody'], self.resources.colors['bg'],
                                         'center', 'top', self.width, 48)
        text_obj_2 = typography.Typography(self.pygame_settings,
                                         """Returning to hub...""",
                                         (self.width // 2, self.height // 2 + 32), 'large', 18,
                                         self.resources.colors['fnt_celeb'], self.resources.colors['bg'],
                                         'center', 'top', self.width, 48)

        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['demos'], 'text_add',
                                                     (text_obj_1, 240, (0, 0), 80, 80))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['demos'], 'text_add',
                                                     (text_obj_2, 240, (0, 0), 80, 80))

        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 15, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, 20, None))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 16, wins_dict['demos'], 'back_to_title',
                                                     (wins_dict, active_wins))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 16, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

    def death_hardcore(self, wins_dict, active_wins, pc, monster, chapter_dict):
        self.width, self.height = self.pygame_settings.screen_res
        wins_dict['realm'].pause = True

        wins_dict['app_title'].char_save(pc, wins_dict['realm'].maze)

        active_wins.clear()
        active_wins.extend([wins_dict['demos'], wins_dict['realm']])
        self.pausable = False

        text_obj_1 = typography.Typography(self.pygame_settings,
                                         """THE LEGEND OF %s $n $n
                                         ...And thus, %s the %s has fallen, killed by %s at %s. $n 
                                         The legends about their deeds and unfortunate death will stay forever $n 
                                         among the common folk, being passed from parent to child $n 
                                         of the forecoming generations.  If they'll happen to be, though, $n 
                                         in the world consumed by darkness. $n $n
                                         Ages of pain and suffering are coming, until, may be, another hero $n
                                         will dare to challenge the forces of Great Evil, and may be, $n
                                         the Gods of Fortune will make them triumph... $n $n
                                         THE END""" % (pc.location[0]['label'].upper(), pc.char_sheet.name.capitalize(),
                                                       pc.char_sheet.type.capitalize(), monster.stats['label'],
                                                       wins_dict['realm'].maze.stage_dict['label']),
                                         (self.width // 2, self.height -100), 'large', 16,
                                         self.resources.colors['fnt_celeb'], self.resources.colors['bg'],
                                         'center', 'top', self.width, 48)
        """text_obj_2 = typography.Typography(self.pygame_settings,
                                         "Returning to hub...",
                                         (self.width // 2, self.height // 2 + 32), 'large', 18,
                                         self.resources.colors['fnt_celeb'], self.resources.colors['bg'],
                                         'center', 'top', self.width, 48)"""

        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['demos'], 'text_add',
                                                     (text_obj_1, 1500, (0,-1), 120, 120))
        """wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['demos'], 'text_add',
                                                     (text_obj_2, 240, (0, 0), 80, 80))"""

        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 79, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, 20, None))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 80, wins_dict['demos'], 'back_to_title',
                                                     (wins_dict, active_wins))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 80, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

    def back_to_title(self, wins_dict, active_wins):
        self.picture_list.clear()
        self.text_list.clear()
        active_wins.clear()
        wins_dict['pools'].pc = None
        wins_dict['app_title'].create_savegames()
        wins_dict['app_title'].char_loaded_info_update(wins_dict)
        active_wins.append(wins_dict['app_title'])

    def back_to_game(self, wins_dict, active_wins):
        self.picture_list.clear()
        self.text_list.clear()
        active_wins.clear()
        active_wins.append(wins_dict['pools'], wins_dict['realm'])

    def tick(self, pygame_settings, wins_dict, active_wins, mouse_pointer):
        if self.pause:
            return
        for i in range(len(self.picture_list)-1, -1, -1):
            panel, dur, timer, sp, fi, fo = self.picture_list[i]
            sp_x, sp_y = sp

            if timer % 2 == 0:
                panel.rendered_rect.x += sp_x
                panel.rendered_rect.y += sp_y

            if fi > 0 and timer <= fi:
                panel.rendered_panel.set_alpha(timer * 255 // fi)
            if fo > 0 and timer >= dur - fo:
                panel.rendered_panel.set_alpha((dur - timer) * 255 // fo)

            if timer < dur:
                self.picture_list[i][2] += 1
            else:
                del self.picture_list[i]

        for i in range(len(self.text_list) - 1, -1, -1):
            text, dur, timer, sp, fi, fo = self.text_list[i]
            sp_x, sp_y = sp

            if timer % 2 == 0:
                text.rendered_rect.x += sp_x
                text.rendered_rect.y += sp_y

            if fi > 0 and timer <= fi:
                text.rendered_text.set_alpha(timer * 255 // fi)
            if fo > 0 and timer >= dur - fo:
                text.rendered_text.set_alpha((dur - timer) * 255 // fo)

            if timer < dur:
                self.text_list[i][2] += 1
            else:
                del self.text_list[i]

    def draw(self, surface):
        # surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
        for panel in self.picture_list:
            panel[0].draw(surface)
        for text in self.text_list:
            text[0].draw(surface)
