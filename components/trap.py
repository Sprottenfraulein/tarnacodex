import random
from library import particle


class Trap:
    def __init__(self, x_sq, y_sq, lvl, tileset, label, rang, dam_type, dam_val_base, dam_val_spread, sound_trigger=None):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = 0
        self.off_y = 0
        self.lvl = lvl
        self.tileset = tileset
        self.label = label
        self.range = rang
        self.dam_type = dam_type
        self.dam_val_base = dam_val_base
        self.dam_val_spread = dam_val_spread
        self.visible = 0  # Visibility: -1 - undetectable trap, 0 - undetected yet, 1 - is visible to player.
        self.mode = 1  # Behavior: -1 - triggered trap, 0 - disarmed trap,
        # 1 - trap armed against pc, 2 - trap armed against mobs.
        self.mob_utility_obj = None  # Monster object for convenience.

        self.sound_trigger = sound_trigger
        self.images = None
        self.image_update()

    def disarm(self, wins_dict, pc, tool_mod=0):
        lvl_dif = min(1, pc.char_sheet.level - self.lvl)
        skill = pc.char_sheet.profs['prof_disarm'] + lvl_dif * 250 + tool_mod  # 25% per level penalty
        rnd_roll = random.randrange(0, 1001)
        if rnd_roll - skill >= 500:
            """wins_dict['realm'].spawn_realmtext('new_txt', "Oh no!", (0, 0), (0, -24), None, pc, None,
                                               120, 'def_bold', 24)"""
            self.trigger(wins_dict, pc)
            return False
        if skill >= rnd_roll:
            wins_dict['realm'].spawn_realmtext('new_txt', "Easy as pie!", (0, 0), (0, -24), None, pc, None, 120,
                                               'def_bold', 24)

            exp = self.lvl * 100
            pc.char_sheet.experience_get(wins_dict, pc, exp)
            wins_dict['pools'].updated = True
            wins_dict['charstats'].updated = True
            wins_dict['realm'].spawn_realmtext('new_txt', '%s exp.' % (exp),
                                               (0, 0), (0, -24), 'sun', pc, (0, -2), 60, 'large', 16, 0,
                                               0.17)
            wins_dict['realm'].pygame_settings.audio.sound('trap_operate')
            return True
        else:
            wins_dict['realm'].spawn_realmtext('new_txt', "Too hard!", (0, 0), (0, -24), None, pc, None, 120,
                                               'def_bold', 24)
            wins_dict['realm'].pygame_settings.audio.sound('mech_hard')
            return False

    def trigger(self, wins_dict, pc):
        pc.wound(wins_dict, self.mob_utility_obj, {'range': self.range, 'attack_type': self.dam_type,
                                                   'attack_val_base': self.dam_val_base,
                                                   'attack_val_spread': self.dam_val_spread}, None, no_reflect=True, no_evade=True)
        self.mode = -1
        self.visible = 1
        wins_dict['realm'].spawn_realmtext(None, 'Ouch!', (0, 0), offset_xy=(0,-24),
                                           color='fnt_attent', stick_obj=pc,
                                           speed_xy=(0, 0), kill_timer=240, font='large', size=16, frict_y=0)
        if self.images is not None:
            self.image_update()
        pc.state_change(8)

        """if self.x_sq is None or self.y_sq is None:
            x_sq, y_sq = pc.x_sq, pc.y_sq
        else:
            x_sq, y_sq = self.x_sq, self.y_sq"""
        if self.dam_type == 'att_physical':
            x_sq, y_sq = pc.x_sq, pc.y_sq
            wins_dict['realm'].particle_list.append(particle.Particle((x_sq, y_sq), (-4, -4),
                                                   wins_dict['realm'].animations.get_animation('effect_dust_cloud')['default'], 16,
                                                                      speed_xy=(-0.25,-0.25)))
        elif self.dam_type == 'att_fire':
            x_sq, y_sq = pc.x_sq, pc.y_sq
            wins_dict['realm'].particle_list.append(particle.Particle((x_sq, y_sq), (-4, -4),
                                                   wins_dict['realm'].animations.get_animation('effect_explosion')['default'], 25,
                                                                      speed_xy=(-0.25,-0.25)))
        if self.sound_trigger is not None:
            wins_dict['realm'].sound_inrealm(self.sound_trigger, pc.x_sq, pc.y_sq)

    def detect(self, wins_dict, pc):
        skill_value = pc.char_sheet.profs['prof_detect']
        lvl_dif = min(1, pc.char_sheet.level - self.lvl)
        rnd_roll = random.randrange(1, 1001)
        if skill_value + lvl_dif * 250 >= rnd_roll:
            self.visible = 1
            wins_dict['realm'].spawn_realmtext(None, 'Trapped!', (0, 0), offset_xy=(0,-24),
                                               color='fnt_attent', stick_obj=pc, kill_timer=240)
            return True
        else:
            return False

    def image_update(self):
        if self.mode == -1:
            self.images = self.tileset['trap_triggered']
        elif self.mode == 0:
            self.images = self.tileset['trap_disarmed']
        elif self.mode == 1:
            self.images = self.tileset['trap_armed']
        elif self.mode == 2:
            self.images = self.tileset['trap_tuned']