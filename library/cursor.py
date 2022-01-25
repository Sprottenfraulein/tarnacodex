# Mouse pointer object
import pygame


class Cursor:
    def __init__(self, pygame_settings, resources):
        self.drag_item = None
        self.drag_ui = None
        self.image = None
        self.visible = True
        self.xy = (0,0)
        self.scaling = pygame_settings.APP_SCALE
        self.still_timer = 0
        self.still_max = 640
        self.inter_list = []

    def interact(self, inter_entry):
        self.inter_list.append(inter_entry)
        if len(self.inter_list) > 10:
            del self.inter_list[0]

    def move(self):
        if self.drag_ui is not None:
            self.drag_ui[0].offset_x = self.xy[0] - self.drag_ui[1]
            self.drag_ui[0].offset_y = self.xy[1] - self.drag_ui[2]

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.xy)
