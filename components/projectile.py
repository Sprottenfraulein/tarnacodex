# Projectile class for ranged attacks (monsters and pc)
from library import particle, maths


class Projectile:
    def __init__(self, xy_sq, off_xy, duration, speed_xy, animation, attack, destroy_on_limit=True,
                 collision_limit=1, blast_radius=0, blast_sound=None, hit_freq=20):
        self.x_sq, self.y_sq = xy_sq
        self.off_x, self.off_y = off_xy
        self.duration = duration
        self.collision_limit = collision_limit
        self.destroy_on_limit = destroy_on_limit
        self.blast_radius = blast_radius
        self.speed_x, self.speed_y = speed_xy

        self.blast_sound = blast_sound
        self.image_strip = animation['images']
        self.timings = animation['timings']
        self.frame_index = 0
        self.frame_timer = 0
        self.step = 1

        self.attack_value, self.attack_type, self.attack_is_crit, self.attack_owner = attack

        self.hit_freq = hit_freq

    def tick(self, wins_dict, fate_rnd):
        self.x_sq += self.speed_x
        self.y_sq += self.speed_y

        if self.duration > 0:
            self.duration -= 1
        else:
            self.destroy(wins_dict, fate_rnd)
            return False

        self.animate()

        realm = wins_dict['realm']
        flags = realm.maze.flag_array[round(self.y_sq)][round(self.x_sq)]
        if not flags.light:
            self.destroy(wins_dict, fate_rnd)
            return False

        if self.collision_limit != 0 and self.duration % self.hit_freq == 0:
            if self.attack_owner == realm.pc:
                if flags.mon is not None and flags.mon.alive:
                    flags.mon.wound(self.attack_value, self.attack_type, True, self.attack_is_crit,
                                    wins_dict, fate_rnd, realm.pc)
                    self.collision_limit -= self.collision_limit > 0
            elif round(realm.pc.x_sq) == round(self.x_sq) and round(realm.pc.y_sq) == round(self.y_sq):
                realm.pc.wound(wins_dict, self.attack_owner, {
                    'attack_type': self.attack_type,
                    'attack_val_base': self.attack_value,
                    'attack_val_spread': 0,
                    'range': True
                }, fate_rnd)
                self.collision_limit -= self.collision_limit > 0

        if self.collision_limit == 0 and self.destroy_on_limit:
            self.destroy(wins_dict, fate_rnd)
            return False
        else:
            return True

    def destroy(self, wins_dict, fate_rnd):
        if self.blast_radius > 0:
            self.detonate(wins_dict, fate_rnd)
        else:
            wins_dict['realm'].particle_list.append(particle.Particle(
                (self.x_sq, self.y_sq), (-4, -4),
                 wins_dict['realm'].animations.get_animation('effect_dust_cloud')['default'], 16, speed_xy=(-0.25,-0.25)
            ))

    def detonate(self, wins_dict, fate_rnd):
        realm = wins_dict['realm']
        if self.attack_owner == realm.pc:
            for mon in realm.mobs_short:
                if (mon is not None and mon.alive
                        and maths.get_distance(self.x_sq, self.y_sq, mon.x_sq, mon.y_sq) - mon.size <= self.blast_radius):
                    mon.wound(self.attack_value, self.attack_type, True, self.attack_is_crit,
                                    wins_dict, fate_rnd, realm.pc)
        elif maths.get_distance(self.x_sq, self.y_sq, wins_dict['realm'].pc.x_sq, wins_dict['realm'].pc.y_sq) <= self.blast_radius:
            realm.pc.wound(wins_dict, self.attack_owner, {
                'attack_type': self.attack_type,
                'attack_val_base': self.attack_value,
                'attack_val_spread': 0,
                'range': True
            }, fate_rnd)

        wins_dict['realm'].particle_list.append(particle.Particle(
            (self.x_sq, self.y_sq), (-4, -4),
            wins_dict['realm'].animations.get_animation('effect_explosion')['default'], 25, speed_xy=(-0.25, -0.25)
        ))
        wins_dict['realm'].sound_inrealm(self.blast_sound, self.x_sq, self.y_sq)

    def animate(self):
        if self.frame_timer < self.timings[self.frame_index]:
            self.frame_timer += self.step
        else:
            self.frame_timer = 0
            if (self.frame_index + 1) < len(self.timings):
                self.frame_index += 1
            else:
                self.frame_index = 0

