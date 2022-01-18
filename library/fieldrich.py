# rich text field object
import pygame
from library import pydraw


class FieldRich:
    def __init__(self, resources, fr_id, fr_xy, fr_size, fr_images=None, text_dict=None,
                 pop_show=60, pop_hide=30, pop_win=None, page=None, img_stretch=True):
        self.resources = resources
        self.id = fr_id
        self.xy = fr_xy
        self.size = list(fr_size)
        if text_dict is None:
            self.text_dict = {}
        self.text_dict = text_dict
        self.images = fr_images
        self.img_stretch = img_stretch
        self.page = page
        self.mode = 0
        self.tags = []

        self.mouse_over = False
        self.popup_active = False

        self.par_div_height = 0

        self.rendered_field = None
        self.rendered_rect = None

    def mouse_down(self, m_button):
        if m_button == 1:
            pass

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        pass

    def render_text(self):
        for par in self.text_dict.values():
            par.render()

    def render(self):
        # calculating overall field size
        f_height = 0
        f_width = 0
        origin_y = 0
        for par in self.text_dict.values():
            f_width = max(f_width, par.max_width + par.x)
            f_height += (par.max_height + self.par_div_height)
            origin_y = min(origin_y, par.y)
        self.size[0] = f_width
        self.size[1] = f_height
        self.rendered_field = pygame.Surface(self.size)
        self.rendered_rect = self.rendered_field.get_rect()
        self.rendered_rect.topleft = self.xy
        # self.render_bg()
        # rendering in sequence
        for par in self.text_dict.values():
            par.draw(self.rendered_field, offset=(0, origin_y))
            origin_y += par.max_height

    def render_bg(self):
        """self.rendered_field = pydraw.square((0, 0), self.rendered_rect.size,
                              (self.resources.colors['gray_light'],
                               self.resources.colors['gray_dark'],
                               self.resources.colors['gray_mid'],
                               self.resources.colors['sun']),
                              sq_outsize=1, sq_bsize=0, sq_ldir=0, sq_fill=False,
                              sq_image=self.rendered_field, same_surface=True)"""
        pass

    def render_all(self):
        self.render_text()
        self.render()

    # I have to come up with idea how to render popup over eveerything
    def draw(self, surface):
        surface.blit(self.rendered_field, self.rendered_rect)
