# panel object
import pygame


class Panel:
    def __init__(self, pan_id, pan_xy, pan_size, pan_images=None,
                 pop_show=60, pop_hide=30, pop_obj=None, page=None):
        self.id = pan_id
        self.size = pan_size
        self.images = pan_images
        self.page = page
        self.mode = 0
        self.tags = []

        self.popup_time_show = pop_show
        self.popup_time_hide = pop_hide
        self.popup_element = pop_obj
        self.popup_active = False

        self.rendered_panel = pygame.Surface(pan_size)
        self.rendered_rect = self.rendered_panel.get_rect()
        self.rendered_rect.topleft = pan_xy
        # self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            pass

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        pass

    """def render(self):
        if self.images is None:
            return
       
        self.rendered_field.blit(self.images[0], (0,0))"""
        # self.rendered_rect = self.rendered_field.get_rect()

    def draw(self, surface):
        # surface.blit(self.rendered_field, self.rendered_rect)
        surface.blit(self.images[self.mode], self.rendered_rect)
