class Particle:
    def __init__(self, xy, offset_xy, animation, duration, speed_xy=None, friction_xy=None, bounce_anim=False, step=1, frame_index=0):
        if speed_xy is None:
            speed_xy = (0,0)
        if friction_xy is None:
            friction_xy = (0,0)

        self.x, self.y = xy
        self.off_x, self.off_y = offset_xy
        self.image_strip = animation['images']
        self.timings = animation['timings']
        self.timer = duration
        self.sp_x, self.sp_y = speed_xy
        self.fr_x, self.fr_y = friction_xy
        self.bounce_anim = bounce_anim

        self.frame_index = frame_index
        self.frame_timer = 0
        self.step = step

    def tick(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            return False

        self.off_x += self.sp_x
        self.off_y += self.sp_y

        self.sp_x = round(self.sp_x * (1 - self.fr_x), 2)
        self.sp_y = round(self.sp_y * (1 - self.fr_y), 2)

        if self.frame_timer < self.timings[self.frame_index]:
            self.frame_timer += 1
        else:
            if (self.frame_index + self.step) >= len(self.timings):
                if self.bounce_anim:
                    self.step *= -1
                else:
                    self.frame_index = -1
            elif (self.frame_index + self.step) <= 0:
                if self.bounce_anim:
                    self.step *= -1
                else:
                    self.frame_index = len(self.timings)
            self.frame_index += self.step
            self.frame_timer = 0

        return True
