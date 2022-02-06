# panel object
import pygame


class Panel:
    def __init__(self, pan_id, pan_xy, pan_size, pan_images=None, page=None, img_stretch=False, tags=None, win=None):
        self.id = pan_id
        self.win = win
        self.size = pan_size
        self.images = pan_images
        self.page = page
        self.mode = 0
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

        self.mouse_over = False
        self.popup_active = False

        self.img_stretch = img_stretch

        self.rendered_panel = pygame.Surface(pan_size).convert()
        self.rendered_panel.set_colorkey((0,255,0))
        self.rendered_rect = self.rendered_panel.get_rect()
        self.rendered_rect.topleft = pan_xy
        self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            pass

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        pass

    def images_update(self, images):
        self.images = images
        self.render()

    def render(self):
        if self.img_stretch:
            pygame.transform.scale(self.images[self.mode], self.rendered_rect.size, self.rendered_panel)
        else:
            self.rendered_panel.blit(self.images[self.mode], (0,0))

    def draw(self, surface):
        surface.blit(self.rendered_panel, self.rendered_rect)

