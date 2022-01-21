import pygame


class Animations:
    def __init__(self):
        self.sets_dict = {
            'anthro_ragdoll': pygame.image.load('res/tilesets/anthro_ragdoll.png').convert()
        }
        for ts in self.sets_dict.values():
            ts.set_colorkey((0, 255, 0), pygame.RLEACCEL)

    def get_animation(self, anim_id):
        if anim_id == 'anthro_default':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (0, 1, 2, 3)),
                    'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (5, 6, 7, 8)),
                    'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (10, 11, 12, 13)),
                    'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (15, 16, 17, 18)),
                    'timings': (8, 8, 8, 8)
                }
            }
            return animation

    def get_image(self, image_id, dimensions, indexes):
        image_sheet = self.sets_dict[image_id]
        sheet_width = image_sheet.get_width()
        # sheet_height = image_sheet.get_height()
        sh_tiles_hor = sheet_width // dimensions[0]
        # sh_tiles_ver = sheet_height // dimensions[1]
        image_list = []
        for ind in indexes:
            ver, hor = divmod(ind, sh_tiles_hor)
            new_image = image_sheet.subsurface((hor * dimensions[0], ver * dimensions[1], dimensions[0], dimensions[1]))
            image_list.append(new_image)
        return image_list