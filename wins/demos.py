# cutscenes window
import pygame
import settings
from components import ui
from library import pydraw, maths, typography


class Demos:
    def __init__(self, pygame_settings, resources, tilesets, animations, db, mouse_pointer, schedule_man, log=True):
        self.db = db
        self.pygame_settings = pygame_settings
        self.resources = resources
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

    def set_picture(self, panel_obj, duration, speed=None, fade_in=0, fade_out=0):
        if speed is None:
            speed = (0, 0)
        self.picture_list.append([panel_obj, duration, 0, speed, fade_in, fade_out])

    def text_add(self, text_obj, duration, speed=None, fade_in=0, fade_out=0):
        if speed is None:
            speed = (0,0)
        self.text_list.append([text_obj, duration, 0, speed, fade_in, fade_out])

    def ending_run(self, wins_dict, active_wins, pc, chapter_dict):
        active_wins.clear()
        active_wins.extend([wins_dict['overlay'], wins_dict['demos']])
        self.pausable = True

        text_obj = typography.Typography(self.pygame_settings,
                                         """You emerge from the dungeon with hopes of bringing the mysterious stone $n
                                         to someone with enough scholarship to comprehend it's nature, $n
                                         but as soon as sunlight touches the artefact, it turns into fine gray dust $n
                                         and before you know it, disappears from your hands. $n $n
                                         
                                         But the job is done. The dead have been put to rest and Ravenstone $n
                                         is as peaceful as ever been. You mount your horse and begin your way back $n
                                         into town - to gather strengths for your ongoing journey.
                                         """,
                                         (self.width // 2, self.height -100), 'large', 16,
                                         self.resources.colors['fnt_celeb'], self.resources.colors['bg'],
                                         'center', 'top', self.width, 48)
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 1, wins_dict['demos'], 'text_add',
                                                     (text_obj, 1500, (0,-1), 120, 120))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 79, wins_dict['overlay'], 'fade_out',
                                                     (active_wins, 20, None))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 80, wins_dict['demos'], 'back_to_title',
                                                     (wins_dict, active_wins))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 80, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

    def death_soft(self, wins_dict, active_wins, pc, chapter_dict):
        for mob in wins_dict['realm'].maze.mobs:
            mob.stop()
        pc.stop()

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
                                                     (wins_dict, active_wins, pc, wins_dict['realm'].maze))
        wins_dict['app_title'].schedule_man.task_add('realm_tasks', 16, wins_dict['overlay'], 'fade_in',
                                                     (active_wins, 20, None))

    def back_to_title(self, wins_dict, active_wins, pc, maze):
        self.picture_list.clear()
        self.text_list.clear()
        active_wins.clear()
        wins_dict['app_title'].char_save(pc, maze)
        wins_dict['app_title'].create_savegames()
        wins_dict['app_title'].char_loaded_info_update(wins_dict)
        active_wins.append(wins_dict['app_title'])

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
