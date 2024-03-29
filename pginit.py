# Importing pygame and game settings modules.
import pygame

import settings
from library import logfun
from library import audio


class PG:
	def __init__(self, resources, log=True):
		# Removing pygame audio playback delay.
		pygame.mixer.pre_init(44100, -16, 1, 512)
		# Initializing pygame and audio mixer.
		pygame.init()
		pygame.mixer.init()
		# Hiding OS cursor.
		# pygame.mouse.set_visible(False)
		self.audio = audio.Audio(resources, not settings.sound_enable, not settings.music_enable)
		# Initializing pygame display.
		# setting graphic scaling
		self.APP_SCALE = settings.app_scale
		# setting display
		self.screen_res = (320, 200)
		self.screen = None
		self.set_display()
		# Creating buffer canvas.
		self.canvas = pygame.Surface(settings.APP_RES)
		# Setting game caption.
		pygame.display.set_caption(settings.APP_CAPTION)
		# Retrieving fps variable.
		self.fps = settings.FPS
		# Creating pygame Clock object for maintaining stable framerate.
		self.clock = pygame.time.Clock()
		# Set Font resolution
		pygame.freetype.set_default_resolution(96)
		self.text_font = pygame.freetype.Font(resources.fonts['def_bold'], 24)
		logfun.put('Pygame initialized successfully.', log)

	def set_display(self):
		# For fullscreen mode:
		mode = pygame.HWACCEL | pygame.HWSURFACE | pygame.FULLSCREEN
		self.screen = pygame.display.set_mode((0,0), mode)
		self.screen_res = self.screen.get_size()
		pygame.display.update()