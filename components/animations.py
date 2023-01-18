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
        if anim_id == 'anthro_kingslayer':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_kingslayer', (24, 24), (20,)), 'timings': (18,)
                }
            }
            return animation
        if anim_id == 'anthro_cosmologist':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_cosmologist', (24, 24), (20,)), 'timings': (18,)
                }
            }
            return animation
        if anim_id == 'anthro_skeleton_red':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_skeleton_red', (24, 24), (20,)), 'timings': (18,)
                },
                'missile_nw': {
                    'images': self.get_image('anthro_skeleton_red', (12, 12), (92, 93, 94, 95)),
                    'timings': (4, 4, 4, 4)
                },
                'missile_w': {
                    'images': self.get_image('anthro_skeleton_red', (12, 12), (92, 93, 94, 95)),
                    'timings': (4, 4, 4, 4)
                },
                'affix_mark': {
                    'images': self.get_image('anthro_skeleton_red', (12, 12), (82, 83, 84, 85)), 'timings': (10,10,10,10)
                }
            }
            return animation
        if anim_id == 'anthro_skeleton_yellow':
            animation = {
                'face_north': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (0, 1, 0, 2)), 'timings': (8, 8, 8, 8)
                },
                'face_east': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (5, 6, 5, 7)), 'timings': (8, 8, 8, 8)
                },
                'face_south': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (10, 11, 10, 12)), 'timings': (8, 8, 8, 8)
                },
                'face_west': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (15, 16, 15, 17)), 'timings': (8, 8, 8, 8)
                },
                'act_north': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (3,0)), 'timings': (18, 18)
                },
                'act_east': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (8,5)), 'timings': (18, 18)
                },
                'act_south': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (13,10)), 'timings': (18, 18)
                },
                'act_west': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (18,15)), 'timings': (18, 18)
                },
                'lay_down': {
                    'images': self.get_image('anthro_skeleton_yellow', (24, 24), (20,)), 'timings': (18,)
                },
                'missile_nw': {
                    'images': self.get_image('anthro_skeleton_yellow', (12, 12), (92, 93, 94, 95, 96, 97, 98, 99)),
                    'timings': (2, 2, 2, 2, 2, 2, 2, 2)
                },
                'missile_w': {
                    'images': self.get_image('anthro_skeleton_yellow', (12, 12), (92, 93, 94, 95, 96, 97, 98, 99)),
                    'timings': (2, 2, 2, 2, 2, 2, 2, 2)
                },
                'affix_mark': {
                    'images': self.get_image('anthro_skeleton_yellow', (12, 12), (82, 83, 84, 85)), 'timings': (10,10,10,10)
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
        elif anim_id == 'effect_arcane_vortex':
            animation = {
                'default': {
                    'images': self.get_image('item_effects', (24, 24), (48, 49, 50, 51, 52)),
                    'timings': (4, 4, 4, 4, 4)
                }
            }
            return animation
        elif anim_id == 'effect_arcane_dust':
            animation = {
                'default': {
                    'images': self.get_image('item_effects', (24, 24), (40, 41, 42, 43, 44)),
                    'timings': (4, 4, 4, 4, 4)
                }
            }
            return animation
        elif anim_id == 'effect_explosion':
            animation = {
                'default': {
                    'images': self.get_image('item_effects', (32, 32), (5, 11, 17, 23, 29)),
                    'timings': (5, 5, 5, 5, 5)
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