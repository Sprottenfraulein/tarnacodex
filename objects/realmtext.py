# Dynamic text object
import pygame


class RealmText:
    def __init__(self, dt_id, dt_xy_sq, text_obj=None, stick_obj=None, offset_xy=None, page=None):
        if offset_xy is None:
            self.off_x, self.off_y = (0, 0)
        else:
            self.off_x, self.off_y = offset_xy
        self.id = dt_id
        self.text_obj = text_obj
        self.page = page
        self.mode = 0
        self.stick_obj = stick_obj
        self.tags = []

        self.mouse_over = False
        self.popup_active = False

        self.x_sq, self.y_sq = dt_xy_sq
        self.render()

    def mouse_down(self, m_button):
        if m_button == 1:
            pass

    def mouse_up(self, m_button):
        if m_button == 1:
            pass

    def release(self, m_button):
        pass

    def tick(self):
        if self.stick_obj is not None:
            self.x_sq, self.y_sq = self.stick_obj.x_sq, self.stick_obj.y_sq

    def render(self):
        self.text_obj.render()

    def draw(self, surface, x_px, y_px):
        surface.blit(self.text_obj.rendered_text, (x_px + self.text_obj.rendered_rect.left, y_px + self.text_obj.rendered_rect.top))