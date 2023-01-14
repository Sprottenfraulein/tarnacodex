# This script loads and sets game resources.
# Importing os module for paths.
import pygame
import os
import settings
from library import fate
from components import dbrequests


class ResMan:
    def __init__(self):
        # creating fate
        self.fate_rnd = fate.Fate()
        # declaring names
        self.grades_loot = (
            'common', 'rare', 'enchanted', 'legendary', 'unique'
        )
        self.grade_colors = (
            'gray_light', 'bright_gold', 'indigo', 'fnt_attent', 'sun'
        )
        self.stat_captions = {
            'attr_str': 'Strength',
            'attr_dex': 'Dexterity',
            'attr_con': 'Constitution',
            'attr_int': 'Intelligence',
            'attr_wis': 'Wisdom',
            'attr_cha': 'Charisma',
            'HP': 'Maximum hit points',
            'MP': 'Maximum magic points',
            'FOOD': 'Maximum food points',
            'hp_pool': 'Hit points',
            'mp_pool': 'Magic points',
            'food_pool': 'Food points',
            'att_base': 'Base attack',
            'att_physical': 'Physical attack',
            'att_fire': 'Fire attack',
            'att_poison': 'Poison attack',
            'att_ice': 'Ice attack',
            'att_lightning': 'Lightning attack',
            'att_arcane': 'Arcane attack',
            'def_melee': 'Melee defence',
            'def_ranged': 'Missile defence',
            'def_physical': 'Physical resistance',
            'def_fire': 'Fire resistance',
            'def_poison': 'Poison resistance',
            'def_ice': 'Ice resistance',
            'def_lightning': 'Lightning resistance',
            'def_arcane': 'Arcane resistance',

            'prof_provoke': 'Aggro distance',  # distance of mobs becoming aggressive
            'prof_evade': 'Evade chance',  # avoid being hit by enemy
            'prof_crit': 'Critical hit chance',  # chance of critical attack
            'prof_thorns': 'Thorns',  # in percents x10 (100% = 1000), returns all close damage to attacker.
            'prof_reflect': 'Missile reflect',  # in percents x10 (100% = 1000), returns all ranged damage to attacker.

            'prof_picklock': 'Lockpicking',  # open locked doors without keys
            'prof_detect': 'Traps detection',  # make trap or hidden door visible
            'prof_disarm': 'Traps disarming',  # dismantle a trap

            'prof_findgold': 'Find gold',  # in percents x10 (100% = 1000), increases gold amounts dropped.
            'prof_findfood': 'Find food',  # in percents x10 (100% = 1000), increases food amounts dropped.
            'prof_findammo': 'Find ammo',  # in percents x10 (100% = 1000), increases ammo amounts dropped.
            'prof_findore': 'Find ores',
            # number competes against ore deposit level x10 to successfully drop an ore. based on intelligence
            'prof_findmagic': 'Find magical items',  # increases quality of drop items
            'prof_light': 'Illumination',  # increases quality of drop items

            'prof_lore': 'Lore',  # identify an item
            'prof_trade': 'Trade',  # buy cheaper
            'prof_craft': 'Crafting skills',  # number competes against item difficulty to successfully craft. based on intelligence

            'prof_bonusexp': 'Experience',
            'prof_range': 'Missile range',
            
            'condition_max': 'Durability' ,
            'charge_max': 'Charge'

        }
        # Declaring game colors.
        self.colors = {
            'fnt_muted': (200, 50, 0),
            'indigo': (60, 0, 255),
            'cyan': (200, 255, 255),
            'fnt_normal': (200, 100, 0),
            'fnt_header': (250, 150, 0),
            'pink': (255, 200, 200),
            'fnt_attent': (255, 0, 0),
            'bloody': (220, 20, 60),
            'fnt_accent': (255, 230, 0),
            'fnt_bonus': (0, 254, 0),
            'frm_normal': (200, 100, 0),
            'fnt_celeb': (255, 255, 255),
            'bright_gold': (255, 219, 81),
            'sun': (255, 255, 200),
            'bg': (10, 10, 10),
            'transparent': (0, 255, 0),
            'azure' : (0, 127, 255),
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
                'switch_click_push',
                'input_key_press',
                'input_enter',
            ),
            'button': (
                'button_click_push',
                'button_click_release',
                'switch_click_push',
                'switch_click_release',
            ),
            'damage': {
                'att_physical': 'hit_physical',
                'att_arcane': 'fire_putout'
            }
        }

        self.sprites = {
            'gold_coins_icon': ('interface', (24,24), (0,))
        }

        self.fonts = {
            'def_bold': './res/fonts/Cloude_Regular_Bold_1.02.ttf',
            'def_normal': './res/fonts/Cloude_Regular_1.02.ttf',
            'large': './res/fonts/NimbusRomNo9L-Med.otf'
        }