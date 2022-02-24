# Projectile class for ranged attacks (monsters and pc)


class Projectile:
    def __init__(self, xy_sq, off_xy, duration, speed_xy, images, attack, destroy_on_limit=True,
                 collision_limit=1, blast_radius=0):
        self.x_sq, self.y_sq = xy_sq
        self.off_x, self.off_y = off_xy
        self.duration = duration
        self.collision_limit = collision_limit
        self.destroy_on_limit = destroy_on_limit
        self.blast_radius = blast_radius
        self.speed_x, self.speed_y = speed_xy
        self.images = images

        self.attack_value, self.attack_type, self.attack_is_crit, self.attack_owner = attack

    def tick(self, wins_dict, fate_rnd):
        self.x_sq += self.speed_x
        self.y_sq += self.speed_y

        if self.duration > 0:
            self.duration -= 1
        else:
            self.destroy()
            return False

        realm = wins_dict['realm']
        flags = realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)]
        if not flags.light:
            self.destroy()
            return False

        if self.collision_limit > 0:
            if self.attack_owner == realm.pc:
                if flags.mon is not None and flags.mon.alive:
                    flags.mon.wound(self.attack_value, self.attack_type, True, self.attack_is_crit,
                                    wins_dict, fate_rnd, realm.pc)
                    self.collision_limit -= 1
            elif round(realm.pc.x_sq) == round(self.x_sq) and round(realm.pc.y_sq) == round(self.y_sq):
                realm.pc.wound(wins_dict, self.attack_owner, {
                    'attack_type': self.attack_type,
                    'attack_val_base': self.attack_value,
                    'attack_val_spread': 0,
                    'range': True
                }, fate_rnd)
                self.collision_limit -= 1

        if self.collision_limit == 0 and self.destroy_on_limit:
            self.destroy()
            return False
        else:
            return True

    def destroy(self):
        if self.blast_radius > 0:
            self.detonate()

    def detonate(self):
        pass
