import pygame
import settings


class Tilesets:
    def __init__(self):
        # Loading tilesets. ADD NEW TILESETS IN THIS LIST. HAS TO BE 256x256 pixels.
        self.sets_dict = {}
        for tileset in settings.tilesets:
            try:
                self.sets_dict[tileset[0]] = pygame.image.load(tileset[1]).convert()
                colorkey = (0,255,0)
                self.sets_dict[tileset[0]].set_colorkey(colorkey, pygame.RLEACCEL)
            except FileNotFoundError:
                pass

        self.img_cooldown = pygame.Surface((48,48)).convert_alpha()
        self.img_cooldown.fill((255,255,255))
        self.img_cooldown.set_alpha(130)

    def get_maze_tiles(self, set_id):
        if set_id == 'dung_default':
            tileset = {
                'wall_hor': self.get_image('dung_bricks', (24, 24), (12, 32)),
                'wall_ver': self.get_image('dung_bricks', (24, 24), (21, 23)),
                'wall_corner_sw': self.get_image('dung_bricks', (24, 24), (40,)),
                'wall_corner_se': self.get_image('dung_bricks', (24, 24), (33,)),
                'wall_corner_ne': self.get_image('dung_bricks', (24, 24), (4,)),
                'wall_corner_nw': self.get_image('dung_bricks', (24, 24), (0,)),
                'wall_end_s': self.get_image('dung_bricks', (24, 24), (6,)),
                'wall_end_e': self.get_image('dung_bricks', (24, 24), (60,)),
                'doorway_hor_l': self.get_image('dung_bricks', (24, 24), (1,)),
                'doorway_hor_r': self.get_image('dung_bricks', (24, 24), (3,)),
                'doorway_ver_b': self.get_image('dung_bricks', (24, 24), (30,)),
                'doorway_ver_t': self.get_image('dung_bricks', (24, 24), (10,)),
                'floor_tiled': self.get_image('dung_bricks', (24, 24), (55,)),
                'floor_ground': self.get_image('dung_bricks', (24, 24), (65,66,67,68,69)),
                'door_ver_mlock': self.get_image('dung_doors', (24, 48), (0, 1, 2)),
                'door_ver_lock': self.get_image('dung_doors', (24, 48), (3,)),
                'door_ver_shut': self.get_image('dung_doors', (24, 48), (4,)),
                'door_ver_open': self.get_image('dung_doors', (24, 48), (5,)),
                'door_hor_mlock': self.get_image('dung_doors', (48, 24), (6, 7, 8)),
                'door_hor_lock': self.get_image('dung_doors', (48, 24), (9,)),
                'door_hor_shut': self.get_image('dung_doors', (48, 24), (10,)),
                'door_hor_open': self.get_image('dung_doors', (48, 24), (11,)),
                'grate_ver_mlock': self.get_image('dung_doors', (24, 48), (12, 13, 14)),
                'grate_ver_lock': self.get_image('dung_doors', (24, 48), (15,)),
                'grate_ver_shut': self.get_image('dung_doors', (24, 48), (16,)),
                'grate_ver_open': self.get_image('dung_doors', (24, 48), (17,)),
                'grate_hor_mlock': self.get_image('dung_doors', (48, 24), (18, 19, 20)),
                'grate_hor_lock': self.get_image('dung_doors', (48, 24), (21,)),
                'grate_hor_shut': self.get_image('dung_doors', (48, 24), (22,)),
                'grate_hor_open': self.get_image('dung_doors', (48, 24), (23,)),
                'chest_ver_open': self.get_image('dung_chests', (24, 24), (0,)),
                'chest_ver_shut': self.get_image('dung_chests', (24, 24), (1,)),
                'chest_ver_lock': self.get_image('dung_chests', (24, 24), (2,)),
                'chest_ver_mlock': self.get_image('dung_chests', (24, 24), (3,4,5)),
                'chest_hor_open': self.get_image('dung_chests', (24, 24), (6,)),
                'chest_hor_shut': self.get_image('dung_chests', (24, 24), (7,)),
                'chest_hor_lock': self.get_image('dung_chests', (24, 24), (8,)),
                'chest_hor_mlock': self.get_image('dung_chests', (24, 24), (9,10,11)),
                'exit_up': self.get_image('dung_bricks', (48, 48), (4,)),
                'exit_down': self.get_image('dung_bricks', (48, 48), (9,)),
                'trap_triggered': self.get_image('dung_bricks', (24, 24), (90,)),
                'trap_disarmed': self.get_image('dung_bricks', (24, 24), (91,)),
                'trap_armed': self.get_image('dung_bricks', (24, 24), (92,)),
                'trap_tuned': self.get_image('dung_bricks', (24, 24), (93,))
            }
            return tileset
        elif set_id == 'dung_dark':
            tileset = {
                'wall_hor': self.get_image('dark_bricks', (24, 24), (12, 32)),
                'wall_ver': self.get_image('dark_bricks', (24, 24), (21, 23)),
                'wall_corner_sw': self.get_image('dark_bricks', (24, 24), (40,)),
                'wall_corner_se': self.get_image('dark_bricks', (24, 24), (33,)),
                'wall_corner_ne': self.get_image('dark_bricks', (24, 24), (4,)),
                'wall_corner_nw': self.get_image('dark_bricks', (24, 24), (0,)),
                'wall_end_s': self.get_image('dark_bricks', (24, 24), (6,)),
                'wall_end_e': self.get_image('dark_bricks', (24, 24), (60,)),
                'doorway_hor_l': self.get_image('dark_bricks', (24, 24), (1,)),
                'doorway_hor_r': self.get_image('dark_bricks', (24, 24), (3,)),
                'doorway_ver_b': self.get_image('dark_bricks', (24, 24), (30,)),
                'doorway_ver_t': self.get_image('dark_bricks', (24, 24), (10,)),
                'floor_tiled': self.get_image('dark_bricks', (24, 24), (55,)),
                'floor_ground': self.get_image('dark_bricks', (24, 24), (65,66,67,68,69)),
                'door_ver_mlock': self.get_image('dung_doors', (24, 48), (0, 1, 2)),
                'door_ver_lock': self.get_image('dung_doors', (24, 48), (3,)),
                'door_ver_shut': self.get_image('dung_doors', (24, 48), (4,)),
                'door_ver_open': self.get_image('dung_doors', (24, 48), (5,)),
                'door_hor_mlock': self.get_image('dung_doors', (48, 24), (6, 7, 8)),
                'door_hor_lock': self.get_image('dung_doors', (48, 24), (9,)),
                'door_hor_shut': self.get_image('dung_doors', (48, 24), (10,)),
                'door_hor_open': self.get_image('dung_doors', (48, 24), (11,)),
                'chest_ver_open': self.get_image('dung_chests', (24, 24), (0,)),
                'chest_ver_shut': self.get_image('dung_chests', (24, 24), (1,)),
                'chest_ver_lock': self.get_image('dung_chests', (24, 24), (2,)),
                'chest_ver_mlock': self.get_image('dung_chests', (24, 24), (3,4,5)),
                'chest_hor_open': self.get_image('dung_chests', (24, 24), (6,)),
                'chest_hor_shut': self.get_image('dung_chests', (24, 24), (7,)),
                'chest_hor_lock': self.get_image('dung_chests', (24, 24), (8,)),
                'chest_hor_mlock': self.get_image('dung_chests', (24, 24), (9,10,11)),
                'exit_up': self.get_image('dark_bricks', (48, 48), (4,)),
                'exit_down': self.get_image('dark_bricks', (48, 48), (9,)),
                'trap_triggered': self.get_image('dark_bricks', (24, 24), (90,)),
                'trap_disarmed': self.get_image('dark_bricks', (24, 24), (91,)),
                'trap_armed': self.get_image('dark_bricks', (24, 24), (92,)),
                'trap_tuned': self.get_image('dark_bricks', (24, 24), (93,))
            }
            return tileset

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

    def images_rotate_to_dir(self, image_pack, direction):
        images = None
        if 0.39 <= direction < 1.17:
            # NW
            images = [pygame.transform.rotate(img, 180) for img in image_pack[0]]
        elif 1.17 <= direction < 1.95:
            # N
            images = [pygame.transform.rotate(img, 90) for img in image_pack[1]]
        elif 1.95 <= direction < 2.73:
            # NE
            images = [pygame.transform.rotate(img, 90) for img in image_pack[0]]
        elif 2.73 <= direction or -2.73 >= direction:
            # E
            images = image_pack[1]
        elif -0.39 >= direction > -1.17:
            # SW
            images = [pygame.transform.rotate(img, -90) for img in image_pack[0]]
        elif -1.17 >= direction > -1.95:
            # S
            images = [pygame.transform.rotate(img, -90) for img in image_pack[1]]
        elif -1.95 >= direction > -2.73:
            # SE
            images = image_pack[0]
        elif 0.39 > direction > -0.39:
            # W
            images = [pygame.transform.rotate(img, -180) for img in image_pack[1]]
        return images or image_pack

# get_maze_tiles('default')