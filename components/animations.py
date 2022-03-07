class Animations:
    def __init__(self, tilesets):
        self.sets_dict = tilesets.sets_dict

    def get_animation(self, anim_id):
        if anim_id == 'anthro_default':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_ragdoll', (24, 24), (20,)), 'timings': (18,)
                }
            }
            return animation
        if anim_id == 'anthro_champion':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_champion', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_champion', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_champion', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_champion', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_champion', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_champion', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_champion', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_champion', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_champion', (24, 24), (20,)), 'timings': (18,)
                }
            }
            return animation
        elif anim_id == 'effect_dust_cloud':
            animation = {
                'default': {
                    'images': self.get_image('item_effects', (24, 24), (56, 57, 58, 59)),
                    'timings': (4, 4, 4, 4)
                }
            }
            return animation
        elif anim_id == 'effect_blood_cloud':
            animation = {
                'default': {
                    'images': self.get_image('item_effects', (24, 24), (60, 61, 62, 63)),
                    'timings': (4, 4, 4, 4)
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