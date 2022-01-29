# button object
import pygame


class Button:
    def __init__(self, bttn_id, bttn_xy, bttn_size, text_obj=None,
                 bttn_func=None, bttn_images=None, bttn_sounds=None, bttn_mode=0, bttn_switch=False,
                 pop_show=60, pop_hide=30, pop_win=None, page=None):
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
        self.tags = []

        self.mouse_over = False
        self.popup_active = False

        self.rendered_button = pygame.Surface(self.images[0].get_rect().size)
        self.rendered_rect = self.rendered_button.get_rect()
        self.rendered_rect.topleft = bttn_xy
        self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            if self.switch:
                if self.mode == 1:
                    pass
                else:
                    self.mode = 1
                    self.sw_op = True
                    self.do_sound()
            else:
                self.mode = 1
                self.do_sound()

            self.render()

    def mouse_up(self, m_button, outside=False):
        if m_button == 1:
            if self.switch:
                if self.sw_op:
                    self.sw_op = False
                elif not outside:
                    self.mode = 0
                    self.do_sound()
                    self.render()
            else:
                self.mode = 0
                if not outside:
                    self.do_sound()
                self.render()
                return self.func

    def release(self, m_button):
        if not self.switch:
            self.mode = 0
            self.render()

    def do_sound(self, sound_index=None):
        if sound_index is None:
            sound_index = self.mode
        try:
            self.sounds[sound_index].play()
        except TypeError or IndexError:
            pass

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
