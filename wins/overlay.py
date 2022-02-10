# mob targeting window
import pygame
import settings
from components import ui
from library import pydraw, maths


class Overlay:
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

        self.offset_x = 0
        self.offset_y = 0
        self.width, self.height = pygame_settings.screen_res
        self.color = (0, 0, 0)
        self.mode = 0
        self.timer = 0
        self.time = 0

    def event_check(self, event, log=True):
        # return True if interaction was made to prevent other windows from responding to this event
        pass

    def fade_out(self, ticks_number=20, color=None):
        self.width, self.height = self.pygame_settings.screen_res
        if color is not None:
            self.color = color
        self.time = self.timer = ticks_number
        self.mode = 0
        self.active_wins.insert(0, self)

    def fade_in(self, ticks_number=20, color=None):
        self.width, self.height = self.pygame_settings.screen_res
        if color is not None:
            self.color = color
        self.time = self.timer = ticks_number
        self.mode = 1
        self.active_wins.insert(0, self)

    def tick(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.timer = 0
            self.active_wins.remove(self)

    def draw(self, surface):
        # surface.blit(self.win_rendered, (self.offset_x, self.offset_y))
        if self.mode:
            surface.fill(self.color, (self.offset_x, self.offset_y + self.height * (self.time - self.timer) // self.time,
                                      self.width, self.height * self.timer // self.time))
        else:
            surface.fill(self.color, (self.offset_x, self.offset_y,
                                      self.width, self.height * (self.time - self.timer) // self.time))