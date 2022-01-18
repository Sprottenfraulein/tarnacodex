# edit object
import pygame


class FieldEdit:
    def __init__(self, fe_id, fe_xy, fe_size, text_obj=None, cursor_obj=None, fe_maxlen=-1, fe_align=-1,
                 fe_sounds=None, fe_images=None, fe_mode=0, fe_blink=30,
                 pop_show=60, pop_hide=30, pop_win=None, page=None):
        self.id = fe_id
        self.size = fe_size
        self.text_obj = text_obj
        self.cursor_symbol = cursor_obj
        self.images = fe_images
        self.sounds = fe_sounds
        self.mode = fe_mode
        self.tags = []
        self.page = page
        self.maxlen = fe_maxlen
        self.cursor_blink_time = fe_blink
        self.blink_timer = 0
        self.cursor_visible = False

        self.mouse_over = False
        self.popup_active = False

        self.rendered_field = pygame.Surface(self.images[0].get_rect().size)
        self.rendered_rect = self.rendered_field.get_rect()
        self.rendered_rect.topleft = fe_xy
        self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            self.blink_timer = 0
            self.cursor_visible = True
            self.mode = 1
            self.render()

            self.do_sound(0)

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        self.mode = 0
        self.render()

    def tick(self):
        if self.mode == 0 and self.cursor_visible:
            self.cursor_visible = False
            self.render()
            return
        self.blink_timer += 1
        if self.mode == 1 and self.blink_timer >= self.cursor_blink_time:
            self.blink_timer = 0
            if self.cursor_visible:
                self.cursor_visible = False
            else:
                self.cursor_visible = True
            self.render()

    def do_sound(self, sound_index=None):
        if sound_index is None:
            sound_index = self.mode
        try:
            self.sounds[sound_index].play()
        except TypeError or IndexError:
            pass

    def render(self):
        self.rendered_field.fill((0,0,0))
        self.rendered_field.blit(self.images[self.mode], (0,0))
        if self.text_obj:
            self.text_obj.draw(self.rendered_field)
            if self.cursor_visible:
                self.cursor_symbol.rendered_rect.left = self.text_obj.actual_width
                self.cursor_symbol.draw(self.rendered_field)
        # self.rendered_rect = self.rendered_field.get_rect()

    def draw(self, surface):
        surface.blit(self.rendered_field, self.rendered_rect)