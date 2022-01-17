# This script loads and sets game resources.
# Importing os module for paths.
import pygame
import os
import settings
from library import counter


class ResMan:
    def __init__(self):
        # Declaring game colors.
        self.colors = {
            'fnt_muted': (200, 50, 0),
            'fnt_normal': (200, 100, 0),
            'fnt_header': (250, 150, 0),
            'fnt_attent': (255, 0, 0),
            'fnt_accent': (255, 230, 0),
            'fnt_bonus': (0, 254, 0),
            'frm_normal': (200, 100, 0),
            'fnt_celeb': (255, 255, 255),
            'bright_gold': (255, 219, 81),
            'sun': (255, 255, 200),
            'bg': (10, 10, 10),
            'transparent': (0, 255, 0),
            'gray_light': (200, 200, 200),
            'gray_mid': (130, 130, 130),
            'gray_dark': (50, 50, 50),
            'gray_darker': (20, 20, 25),
            'black': (0, 0, 0)
        }

        # Loading sounds.
        self.sounds = {}
        for snd in settings.sounds:
            try:
                self.sounds[snd[0]] = snd[1]
            except FileNotFoundError:
                pass
        # Loading music.
        self.music = {}
        for mus in settings.music:
            try:
                self.music[mus[0]] = mus[1]
            except FileNotFoundError:
                pass
        # setting game icon
        icon = pygame.Surface((16,16))
        # icon.blit(self.tilesets[0], (0, 0), (5,214,16,16))
        pygame.display.set_icon(icon)

        # preset packs
        self.sound_presets = {
            'text_input': (
                'bttn_click_down',
                'input_key_press',
                'input_enter',
            ),
            'button': (
                'bttn_click_up',
                'bttn_click_down',
            )
        }

        self.sprites = {
            'battleaxe_rare_floor': ('floor_items', (24, 24), (0,)),
            'battleaxe_rare_inv': ('inv_items', (24, 24), (0,)),
            'flail_rare_floor': ('floor_items', (24, 24), (1,)),
            'flail_rare_inv': ('inv_items', (24, 24), (1,))
        }
