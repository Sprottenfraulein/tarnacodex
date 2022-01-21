# edit object
import pygame


class FieldText:
    def __init__(self, ft_id, ft_xy, ft_size, text_obj=None, ft_align=-1, ft_images=None,
                 pop_show=60, pop_hide=30, pop_win=None, page=None):
        self.id = ft_id
        self.size = ft_size
        self.text_obj = text_obj
        self.images = ft_images
        self.page = page
        self.mode = 0
        self.tags = []

        self.mouse_over = False
        self.popup_active = False

        self.rendered_field = pygame.Surface(ft_size)
        self.rendered_rect = self.rendered_field.get_rect()
        self.rendered_rect.topleft = ft_xy
        self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            pass

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        pass

    def render_all(self):
        self.text_obj.render()
        self.render()

    def render(self):
        if self.images is None:
            if self.text_obj is not None:
                self.rendered_field = self.text_obj.rendered_text
        else:
            self.rendered_field.blit(self.images[0], (0,0))
            if self.text_obj:
                self.text_obj.draw(self.rendered_field)

        # self.rendered_rect = self.rendered_field.get_rect()

    def draw(self, surface):
        surface.blit(self.rendered_field, self.rendered_rect)
