# game items object
from library import logfun


class Treasure:
    def __init__(self, tile_sets, resources, audio, treasure_dict, x_sq=-1, y_sq=-1, stashed=True, log=True):
        self.x_sq = x_sq
        self.y_sq = y_sq
        self.off_x = self.off_y = 0
        self.stashed = stashed

        self.props = treasure_dict

        # adding container list
        self.container_max = self.props['container']
        if self.container_max > 0:
            self.props['container'] = []
        else:
            del self.props['container']

        # linking images and sounds
        for prop in ('image_floor', 'image_inventory', 'image_on_char', 'image_inventory_empty'):
            try:
                self.props[prop] = tile_sets.get_image(*resources.sprites[self.props[prop]])
            except KeyError:
                logfun.put('Treasure creation: could not find image "%s".' % prop, log)

        for prop in ('sound_pick', 'sound_drop', 'sound_swing', 'sound_use'):
            try:
                self.props[prop] = audio.bank_sounds[self.props[prop]]
            except KeyError:
                logfun.put('Treasure creation: could not find sound "%s".' % prop, log)
