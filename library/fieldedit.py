# edit object
import pygame


class FieldEdit:
    def __init__(self, ui, fe_id, fe_xy, fe_size, text_obj=None, cursor_obj=None, fe_maxlen=-1, fe_align='left',
                 fe_sounds=None, fe_images=None, fe_mode=0, fe_blink=30, page=None):
        self.id = fe_id
        self.ui = ui
        self.size = fe_size
        self.text_obj = text_obj
        self.cursor_symbol = cursor_obj
        self.images = fe_images
        self.sounds = fe_sounds
        self.mode = fe_mode
        self.tags = []
        self.page = page
        self.maxlen = fe_maxlen
        self.fe_align = fe_align
        self.cursor_blink_time = fe_blink
        self.blink_timer = 0
        self.cursor_visible = False

        self.mouse_over = False
        self.popup_active = False

        self.rendered_field = pygame.Surface(self.images[0].get_rect().size)
        self.rendered_rect = self.rendered_field.get_rect()
        self.rendered_rect.topleft = fe_xy

        if self.fe_align == 'left':
            self.cursor_symbol.rendered_rect.left = self.text_obj.actual_width
        elif self.fe_align == 'right':
            self.cursor_symbol.rendered_rect.left = self.rendered_rect.width - self.text_obj.actual_width
        elif self.fe_align == 'center':
            self.cursor_symbol.rendered_rect.left = self.rendered_rect.width // 2 + self.text_obj.actual_width // 2

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
            self.ui.updated = True

    def do_sound(self, sound_index=None):
        if sound_index is None:
            sound_index = self.mode
        try:
            self.sounds[sound_index].play()
        except TypeError or IndexError:
            pass

    def render_all(self):
        self.text_obj.update_and_render()
        self.render()

    def render(self):
        self.rendered_field.fill((0,0,0))
        self.rendered_field.blit(self.images[self.mode], (0,0))
        if self.text_obj:
            self.text_obj.draw(self.rendered_field)
            if self.cursor_visible:
                if self.fe_align == 'left':
                    self.cursor_symbol.rendered_rect.left = self.text_obj.actual_width
                elif self.fe_align == 'right':
                    self.cursor_symbol.rendered_rect.left = self.rendered_rect.width - self.text_obj.actual_width
                elif self.fe_align == 'center':
                    self.cursor_symbol.rendered_rect.left = self.rendered_rect.width // 2 + self.text_obj.actual_width // 2
                self.cursor_symbol.draw(self.rendered_field)
        # self.rendered_rect = self.rendered_field.get_rect()

    def draw(self, surface):
        surface.blit(self.rendered_field, self.rendered_rect)