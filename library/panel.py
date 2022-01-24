# panel object
import pygame


class Panel:
    def __init__(self, pan_id, pan_xy, pan_size, pan_images=None, page=None, img_stretch=False):
        self.id = pan_id
        self.size = pan_size
        self.images = pan_images
        self.page = page
        self.mode = 0
        self.tags = []

        self.mouse_over = False
        self.popup_active = False

        self.img_stretch = img_stretch

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
        if self.img_stretch:
            str_img = pygame.transform.scale(self.images[self.mode], self.rendered_rect.size)
            surface.blit(str_img, self.rendered_rect)
        else:
            surface.blit(self.images[self.mode], self.rendered_rect)
