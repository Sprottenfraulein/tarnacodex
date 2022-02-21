import pygame
import random
from library import logfun


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

    def sound(self, name, log=True):
        if self.mute_snd:
            return
        if name is None or name not in self.bank_sounds:
            logfun.put('Can not find sound "%s"!' % name, log)
            return
        return self.bank_sounds[name].play()

    def sound_panned(self, name, direction, volume, log=True):
        if self.mute_snd:
            return
        if name is None or name not in self.bank_sounds:
            logfun.put('Can not find sound "%s"!' % name, log)
            return
        sc_right = round((3.14 - abs(direction)) / 3.14, 2)
        sc_left = round(abs(direction) / 3.14, 2)
        vol_mod = round(volume / 2, 2)
        snd_channel = self.bank_sounds[name].play()
        snd_channel.set_volume((vol_mod + sc_left * (1 - vol_mod)) * volume, (vol_mod + sc_right * (1 - vol_mod)) * volume)