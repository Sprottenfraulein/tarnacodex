# button object
import pygame


class Button:
    def __init__(self, bttn_id, bttn_xy, bttn_size, audio, text_obj=None,
                 bttn_func=None, bttn_images=None, bttn_sounds=None, bttn_mode=0, bttn_switch=False, tags=None,
                 page=None):
        self.audio = audio
        self.id = bttn_id
        self.size = bttn_size
        self.text_obj = text_obj
        self.func = bttn_func
        self.images = bttn_images
        self.sounds = bttn_sounds
        self.mode = bttn_mode
        self.switch = bttn_switch
        self.sw_op = False
        self.page = page
        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.enabled = True

        self.mouse_over = False
        self.popup_active = False

        self.rendered_button = pygame.Surface(self.images[0].get_rect().size).convert()

        self.rendered_rect = self.rendered_button.get_rect()
        self.rendered_rect.topleft = bttn_xy
        self.render()

    def mouse_down(self, m_button):
        if not self.enabled:
            return
        if m_button == 1:
            if self.switch:
                if self.mode == 1:
                    pass
                else:
                    self.mode = 1
                    self.sw_op = True
                    self.do_sound(2)
            else:
                self.mode = 1
                self.do_sound(0)

            self.render()

    def mouse_up(self, m_button, outside=False):
        if not self.enabled:
            return
        if m_button == 1:
            if self.switch:
                if self.sw_op:
                    self.sw_op = False
                elif not outside:
                    self.mode = 0
                    self.do_sound(3)
                    self.render()
            else:
                self.mode = 0
                if not outside:
                    self.do_sound(1)
                self.render()
                return self.func

    def release(self, m_button):
        if not self.enabled:
            return
        if not self.switch and m_button == 1:
            self.mode = 0
            self.render()

    def do_sound(self, sound_index):
        self.audio.sound(self.sounds[sound_index])

    def render(self):
        self.rendered_button.fill((0,0,0))
        self.rendered_button.blit(self.images[self.mode], (0,0))
        if self.text_obj is not None:
            if self.mode == 1:
                self.text_obj.draw(self.rendered_button, (0,1))
            else:
                self.text_obj.draw(self.rendered_button)
        # self.rendered_rect = self.rendered_button.get_rect()

    def draw(self, surface):
        surface.blit(self.rendered_button, self.rendered_rect)
