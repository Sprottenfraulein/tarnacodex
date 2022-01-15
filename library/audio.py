import pygame
import random


class Audio:
    def __init__(self, resources):

        self.bank_sounds = {}
        for snd_name, snd_path in resources.sounds.items():
            self.bank_sounds[snd_name] = pygame.mixer.Sound(snd_path)
        self.bank_music = resources.music

        self.music_playing = None
        self.mute_snd = False
        self.mute_mus = False

    def music(self, name, loops=-1):
        if not pygame.mixer.music.get_busy() and self.music_playing is not name:
            pygame.mixer.music.load(self.bank_music[name])
            pygame.mixer.music.play(loops)
        self.music_playing = name

    def playlist(self):
        self.music(random.choice(self.bank_music.keys()), 1)

    def music_stop(self):
        pygame.mixer.music.stop()
        self.music_playing = None

    def sound(self, name):
        if not self.mute_snd:
            self.bank_sounds[name].play()
