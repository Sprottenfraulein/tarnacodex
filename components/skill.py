# game skill object
from components import dbrequests


class Skill:
    def __init__(self, skill_id, level, db_cursor, tile_sets, resources, audio, x_sq=-1, y_sq=-1, log=True):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = self.off_y = 0

        self.cooldown_timer = 0

        self.props = dbrequests.skill_get_by_id(db_cursor, skill_id)

        calc_level(level, self.props)

        # linking images and sounds
        images_update(db_cursor, self.props, tile_sets)

        sounds_update(db_cursor, self.props, audio)


def images_update(db_cursor, skill_props, tile_sets):
    images_dict = dbrequests.skill_images_get(db_cursor, skill_props['skill_id'], skill_props['grade'])
    try:
        skill_props['image_inventory'] = tile_sets.get_image(images_dict[0]['tileset'],
                                                        (images_dict[0]['width'], images_dict[0]['height']),
                                                        (images_dict[0]['index'],))
    except KeyError:
        pass
    try:
        skill_props['image_floor'] = tile_sets.get_image(images_dict[1]['tileset'],
                                                        (images_dict[1]['width'], images_dict[1]['height']),
                                                        (images_dict[1]['index'],))
    except KeyError:
        pass


def sounds_update(db_cursor, skill_props, audio):
    sounds_dict = dbrequests.skill_sounds_get(db_cursor, skill_props['skill_id'], skill_props['grade'])
    try:
        skill_props['sound_drop'] = audio.bank_sounds[sounds_dict[0]]
        skill_props['sound_pickup'] = audio.bank_sounds[sounds_dict[1]]
        skill_props['sound_use'] = audio.bank_sounds[sounds_dict[2]]
    except KeyError:
        pass


def calc_level(level, skill_props):
    skill_props['price_buy'] = skill_props['price_buy'] * level // skill_props['lvl']
        # skill_props['price_sell'] = skill_props['price_sell'] * level // skill_props['lvl']

    skill_props['lvl'] = level


def calc_grade(db_cursor, grade, skill_props, tile_sets, audio):
    # set grade according to skill level. I left this mostly for a way to change skill icon appearance

    images_update(db_cursor, skill_props, tile_sets)
    sounds_update(db_cursor, skill_props, audio)

    skill_props['grade'] = grade
