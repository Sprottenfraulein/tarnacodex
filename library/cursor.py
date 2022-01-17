# Mouse pointer object
import pygame


class Cursor:
    def __init__(self, pygame_settings, resources):
        self.drag_loot = None
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

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.xy)
