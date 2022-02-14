# Dynamic text object
import pygame


class RealmText:
    def __init__(self, realm, dt_id, dt_xy_sq, text_obj=None, stick_obj=None, offset_xy=None, page=None,
                 speed_xy=None, kill_timer=None, frict_x=0, frict_y=0):
        if offset_xy is None:
            self.off_x, self.off_y = (0, 0)
        else:
            self.off_x, self.off_y = offset_xy
        if speed_xy is None:
            self.speed_xy = [0,0]
        else:
            self.speed_xy = [speed_xy[0], speed_xy[1]]
        self.realm = realm
        self.kill_timer = kill_timer
        self.frict_x, self.frict_y = frict_x, frict_y
        self.id = dt_id
        self.text_obj = text_obj
        self.page = page
        self.mode = 0
        self.stick_obj = stick_obj

        self.mouse_over = False
        self.popup_active = False

        self.x_sq, self.y_sq = dt_xy_sq
        self.stick_to_obj()
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
        self.off_x += self.speed_xy[0]
        self.off_y += self.speed_xy[1]
        self.speed_xy[0] -= self.speed_xy[0] * self.frict_x
        self.speed_xy[1] -= self.speed_xy[1] * self.frict_y

        self.stick_to_obj()

        if self.kill_timer is not None:
            if self.kill_timer > 0:
                self.kill_timer -= 1
            else:
                self.realm.text_short.remove(self)
                if self in self.realm.maze.text:
                    self.realm.maze.text.remove(self)

    def stick_to_obj(self):
        if self.stick_obj is not None:
            self.x_sq, self.y_sq = self.stick_obj.x_sq + 0.5, self.stick_obj.y_sq + 0.5

    def render(self):
        self.text_obj.render()

    def draw(self, surface, x_px, y_px):
        surface.blit(self.text_obj.rendered_text, (x_px + self.text_obj.rendered_rect.left + self.off_x,
                                                   y_px + self.text_obj.rendered_rect.top + self.off_y))