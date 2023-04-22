import random

import pygame

from library import maths
from library import pickrandom, calc2darray, itemlist
from components import dbrequests, progression, room, door, stairs, trap, lock, flagtile, monster, gamesave, chest, initmod, treasure, furniture, trigger


class Maze:
    def __init__(self, db, animations, tile_sets, audio, pc, resources, use_saves=True):
        self.db = db
        self.animations = animations
        self.resources = resources
        self.audio = audio
        self.tile_sets = tile_sets

        self.MOB_HP_SCALE_RATE = 0.5
        self.MOB_DMG_SCALE_RATE = 0.4
        self.EXP_SCALE_RATE = 0.3
        # self.GOLD_SCALE_RATE = 1.3
        self.TRAP_SCALE_RATE = 0.5

        self.chapter, self.stage_index = pc.location
        self.stage_dict = get_chapter_stage(db, self.chapter, self.stage_index)
        self.exits_list = [('up', 'exit_up')]

        # adding second exit to the lower floor if there are more levels ahead.
        if self.stage_index < self.chapter['stage_number'] - 1:
            self.exits_list.append(('down', 'exit_down'))

        self.width = self.stage_dict['width']
        self.height = self.stage_dict['height']

        if self.stage_dict['lvl'] is None:
            self.lvl = pc.char_sheet.level
        else:
            self.lvl = self.stage_dict['lvl']

        self.mob_utility_obj = monster.Lurker(0, 0, None, {
            'label': 'deadly trap',
            'crit_chance': 5,
            'hp_max': None,
            'speed': None,
            'lvl': self.lvl
        }, 0)
        self.mob_utility_obj.alive = False

        self.tradepost_update = False

        self.trap_rate = self.stage_dict['trap_rate']
        self.lock_rate = self.stage_dict['lock_rate']
        self.grate_rate = self.stage_dict['grate_rate']
        self.magic_lock_rate = self.stage_dict['magic_lock_rate']
        self.monster_ids = self.stage_dict['monsters']
        self.monster_number = self.stage_dict['monster_number']

        self.array = maze_array(self.width, self.height)
        self.decor_rnds = []
        self.decor_array = None
        self.shading_color = (0,0,0)

        self.rooms = None
        self.doors = set()
        self.chests = []
        self.mobs = []
        self.traps = []
        self.exits = []
        self.furnitures = []
        self.triggers = []
        self.loot = itemlist.ItemList(filters={
                'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                               'orb_ammo', 'orb_source', 'use_wand', 'exp_tools', 'exp_lockpick', 'exp_food', 'exp_key',
                               'light', 'aug_gem', 'sup_potion', 'use_learn', 'use_craft', 'exp_res', 'misc_man'],
            })
        self.text = []

        self.ANIM_LEN = 4
        self.anim_frame = 0
        self.anim_timing = self.stage_dict['anim_timing']
        self.anim_timer = 0

        # WORKING WITH PREGENERATED DATA
        stage_progress = dbrequests.chapter_progress_get(db.cursor, pc.char_sheet.id, stage_index=self.stage_index)
        if len(stage_progress) > 0 and use_saves:
            gamesave.load_maze(pc, self, db, tile_sets, animations, flags_create)

        else:
            self.tradepost_update = True
            self.decor_rnds_read = False
            if self.stage_dict['tile_set'] == 'randomized':
                self.tile_set = tile_sets.get_random_maze(self.decor_rnds, self.decor_rnds_read)
            else:
                self.tile_set = tile_sets.get_maze_tiles(self.stage_dict['tile_set'])
            if self.stage_dict['shading_color'] == 'randomized':
                if random.randrange(0, 10) > 8:
                    self.shading_color = random.choice([key for key, value in self.resources.colors.items() if 'shade' in key])
                else:
                    self.shading_color = 'shade_darkness'
            else:
                self.shading_color = self.stage_dict['shading_color']

        if len(stage_progress) == 0 or stage_progress[0]['maze_rolled'] == 0 or not use_saves:
            # self.generate_1(0, 0, self.height - 1, self.width - 1, 8, 8, False)
            getattr(self, self.stage_dict['maze_algorythm'])(pc, 0, 0, self.height-1, self.width-1,
                                                             self.stage_dict['room_min_width'],
                                                             self.stage_dict['room_min_height'], True)
        if len(stage_progress) == 0 or stage_progress[0]['monsters_rolled'] == 0 or not use_saves:
            populate(self.db, self, pc, self.animations, self.resources.fate_rnd)
        self.decor_array = decor_maze(self)
        flags_update(self, self.flag_array)

    def generate_1(self, pc, top, left, bottom, right, min_width, min_height, prop, vert_chance=50):
        self.rooms = split_build(top, left, bottom, right, min_width, min_height, prop, vertical=vert_chance, r_limit=14)
        random.shuffle(self.rooms)
        for rm in self.rooms:
            square(self.array, rm.top, rm.left, rm.bottom + 1, rm.right + 1, '#', '.', True)
        for rm in self.rooms:
            # rooms_attached(self, rm, 2, 2, max(min_width, min_height))
            rooms_attached(self, rm, 2, 2, 3)
        room_seq = get_room_sequence(self.rooms)
        bonus_rooms = [rm for rm in self.rooms if rm not in room_seq]

        # Removing part of additional rooms
        for i in range(0, len(bonus_rooms)):
            rnd_room = random.choice(bonus_rooms)
            if any(rrm in rnd_room.adj_rooms for rrm in room_seq):
                continue
            square(self.array, rnd_room.top, rnd_room.left, rnd_room.bottom + 1, rnd_room.right + 1, '#', ' ', True)
            for rm in self.rooms:
                if rnd_room in rm.adj_rooms:
                    rm.adj_rooms.remove(rnd_room)
                    for dr in rnd_room.doors:
                        if dr in rm.doors:
                            rm.doors.remove(dr)
            for dr in rnd_room.doors:
                if dr in self.doors:
                    self.doors.remove(dr)
            if rnd_room in self.rooms:
                self.rooms.remove(rnd_room)
            bonus_rooms.remove(rnd_room)

        self.flag_array = flags_create(self, self.array)
        exits_set(self, self.exits_list, room_seq)
        doors_set(self, self.tile_set, self.db, 'monster_attacks', bonus_rooms)
        grate_controls(self, room_seq)
        traps_set(self, 'monster_attacks', self.db, pc)
        well_set(self, room_seq, bonus_rooms)
        furniture_set(self)

    def generate_2(self, pc, top, left, bottom, right, min_width, min_height, prop, vert_chance=50, rooms_number=None):
        square(self.array, top, left, bottom, right, '#', '.', True)
        self.rooms = scatter_build(top, left, bottom, right, min_width, min_height, min_width * 2, min_height * 2, 2, rooms_number)
        random.shuffle(self.rooms)
        for rm in self.rooms:
            square(self.array, rm.top, rm.left, rm.bottom + 1, rm.right + 1, '#', '.', True)
        for rm in self.rooms:
            # rooms_attached(self, rm, 2, 2, max(min_width, min_height))
            rooms_attached(self, rm, 2, 2, 3, mandatory_doors=random.randrange(1, 5))

        columns_set(self.array, '#', double_space=True)
        bonus_rooms = self.rooms[:round(len(self.rooms) / 2)]
        self.flag_array = flags_create(self, self.array)
        doors_set(self, self.tile_set, self.db, 'monster_attacks', bonus_rooms)
        free_rooms = [rm for rm in self.rooms if not rm.locked]
        grate_controls(self, free_rooms)

        exits = self.exits_list[:]
        while len(exits) > 0:
            x_sq = random.randrange(left + 1, right -1)
            y_sq = random.randrange(top + 1, bottom -1)
            for rm in self.rooms:
                if rm.right + 1 >= x_sq >= rm.left - 1 and rm.bottom + 1 >= y_sq >= rm.top - 1:
                    break
            else:
                if self.array[y_sq][x_sq] == '#' or self.array[y_sq+1][x_sq] == '#':
                    continue
                ex = exits.pop()
                dest = ex[0]
                new_exit = stairs.Stairs(x_sq, y_sq, -1, -1, dest, None, self.tile_set[ex[1]], ex[1])
                self.exits.append(new_exit)

        traps_set(self, 'monster_attacks', self.db, pc)
        well_set(self, self.rooms, free_rooms)
        furniture_set(self)

    def mob_populate_alg_1(self, db, maze, animations, maze_monster_pool, monster_number, pop_level):
        mob_populate_alg_1(db, maze, animations, maze_monster_pool, monster_number, pop_level)

    def tick(self):
        if self.anim_timer >= self.anim_timing:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.anim_frame >= self.ANIM_LEN:
                self.anim_frame -= self.ANIM_LEN
        else:
            self.anim_timer += 1

    def spawn_loot(self, x_sq, y_sq, loot_list):
        for lt in loot_list:
            lt.x_sq, lt.y_sq = x_sq, y_sq
            self.loot.append(lt)
            flags = self.flag_array[y_sq][x_sq]
            flags.item.append(lt)

    def longwayhome_reroll(self, realm):
        for i in range(0, realm.maze.chapter['stage_number'] - 1):
            dbrequests.chapter_progress_set(realm.db, realm.pc.char_sheet.id, i, 1, 0, 1, 0, 0, 1)
        realm.spawn_realmtext('new_txt', "This is it! I need to go back now.", (0, 0), (0, -24),
                              'cyan', realm.pc, None, 240, 'def_bold', 24)
        realm.sound_inrealm('realmtext_noise', realm.pc.x_sq, realm.pc.y_sq)

    def remains_add(self, pc, wins_dict):
        for rm in self.rooms:
            if rm.inside(pc.x_sq, pc.y_sq):
                death_room = rm
                break
        else:
            death_room = None
        space_list = calc2darray.fill2d(self.flag_array, ('mov', 'obj', 'door', 'floor'),
                                        (round(pc.x_sq), round(pc.y_sq)), (round(pc.x_sq), round(pc.y_sq)), 2, 10, r_max=8)
        x_sq, y_sq = space_list[-1]
        furn = furniture.Remains(x_sq, y_sq, death_room, self.tile_sets,
                                 [itm for itm in pc.char_sheet.inventory if itm is not None and not 'quest_item' in itm.props],
                                 pc.char_sheet.gold_coins)
        furn.inventory.extend(pc.char_sheet.quest_item_remove(wins_dict))
        self.furnitures.append(furn)
        fl = self.flag_array[y_sq][x_sq]
        fl.mov = fl.mov and not furn.solid
        fl.obj = furn
        for i in range(len(pc.char_sheet.inventory)):
            pc.char_sheet.inventory[i] = None
        pc.char_sheet.gold_coins = 0


def get_room_sequence(rooms):
    total_rooms = len(rooms)
    room_seq = [random.choice(rooms)]
    for i in range(0, total_rooms // 2):
        room_choices = [rm for rm in room_seq[-1].adj_rooms if rm not in room_seq and not any(itm in rm.adj_rooms for itm in [rs for rs in room_seq if rs != room_seq[-1]])]
        if room_choices:
            room_seq.append(random.choice(room_choices))
        else:
            break
    return room_seq


def split_build(top, left, bottom, right, min_width, min_height, prop, vertical=50, r_limit=4):
    if r_limit <= 0:
        return []
    room_list = []
    width = right - left
    height = bottom - top
    if random.randrange(0, 8) == 0 and len(room_list) > 1:
        room_list.append(room.Room(top, left, bottom, right))
    elif random.randrange(1, 101) <= vertical or (prop and width > height):
        if width > min_width * 2:
            rnd_slice = random.randrange(min_width, width - min_width + 1)
            room_list.extend(
                split_build(top, left, bottom, left + rnd_slice, min_width, min_height, vertical, r_limit - 1))
            room_list.extend(
                split_build(top, left + rnd_slice, bottom, right, min_width, min_height, vertical, r_limit - 1))
        elif width == min_width * 2:
            room_list.append(room.Room(top, left, bottom, right - min_width))
            room_list.append(room.Room(top, right - min_width, bottom, right))
        else:
            room_list.append(room.Room(top, left, bottom, right))
    else:
        if height > min_height * 2:
            rnd_slice = random.randrange(min_height, height - min_height + 1)
            room_list.extend(
                split_build(top, left, top + rnd_slice, right, min_width, min_height, vertical, r_limit - 1))
            room_list.extend(
                split_build(top + rnd_slice, left, bottom, right, min_width, min_height, vertical, r_limit - 1))
        elif height == min_height * 2:
            room_list.append(room.Room(top, left, bottom - min_height, right))
            room_list.append(room.Room(bottom - min_height, left, bottom, right))
        else:
            room_list.append(room.Room(top, left, bottom, right))
    return room_list


def scatter_build(top, left, bottom, right, min_width, min_height, max_width, max_height, space, number):
    if number is None:
        number = (bottom - top) * (right - left) // (((max_width - min_width) // 2 + 1) * ((max_height - min_height) // 2 + 1)) // 2
    room_list = []
    errors = 0
    max_errors = 50
    while number > 0 and min_width < max_width and min_height < max_height:
        if errors == max_errors:
            if max_width > min_width:
                max_width -= 1
            if max_height > min_height:
                max_height -= 1
            errors = 0

        rnd_top = random.randrange(top + space, bottom - space - min_height)
        rnd_bottom = random.randrange(rnd_top + min_height, rnd_top + min(max_height+1, bottom - space - rnd_top))
        rnd_left = random.randrange(left + space, right - space - min_width)
        rnd_right = random.randrange(rnd_left + min_width, rnd_left + min(max_width+1, right - space - rnd_left))
        rnd_rect = pygame.Rect(rnd_left, rnd_top, rnd_right-rnd_left, rnd_bottom - rnd_top)
        for rm in room_list:
            if rnd_rect.colliderect((rm.left - space, rm.top - space, rm.right - rm.left + space * 2, rm.bottom - rm.top + space * 2)):

                errors += 1
                break
        else:
            new_room = room.Room(rnd_top, rnd_left, rnd_bottom, rnd_right)
            room_list.append(new_room)
            errors = 0
            number -= 1

    return room_list


def columns_set(array, column_byte, double_space=True, step=None):
    if double_space:
        step = step or 3
        pattern = (
            (('.','0'), ('.','0'), ('.','0'), ('.','0'), ('.','0'), ),
            (('.','0'), ('.','0'), ('.','0'), ('.','0'), ('.','0'), ),
            (('.','0'), ('.','0'), ('.','0'), ('.','0'), ('.','0'), ),
            (('.', '0'), ('.', '0'), ('.', '0'), ('.', '0'), ('.', '0'),),
            (('.', '0'), ('.', '0'), ('.', '0'), ('.', '0'), ('.', '0'),),
        )
        locations = pattern_find(array, -1, -1, len(array[0]) + 1, len(array) + 1, pattern, step, step, 2, 2)
        if locations:
            for loc_x, loc_y in locations:
                array[loc_y][loc_x] = column_byte
    else:
        step = step or 2
        pattern = (
            (('.', '0'), ('.', '0'), ('.', '0')),
            (('.', '0'), ('.', '0'), ('.', '0')),
            (('.', '0'), ('.', '0'), ('.', '0')),
        )
        locations = pattern_find(array, -1, -1, len(array[0]) + 1, len(array) + 1, pattern, step, step, 1, 1)
        if locations:
            for loc_x, loc_y in locations:
                array[loc_y][loc_x] = column_byte


def maze_array(width, height, byte_def=' '):
    new_maze = []
    for i in range(0, height):
        new_maze.append([byte_def] * width)
    return new_maze


def square(maze, top, left, bottom, right, byte_draw, byte_fill=None, fill=False):
    if fill and not byte_fill:
        byte_fill = byte_draw
    for i in range(top, bottom):
        for j in range(left, right):
            if top < i < bottom - 1 and left < j < right - 1:
                if fill:
                    try:
                        maze[i][j] = byte_fill
                    except IndexError:
                        pass
                else:
                    continue
            else:
                try:
                    maze[i][j] = byte_draw
                except IndexError:
                    pass


def rooms_attached(maze, rm, v_merge=1, h_merge=1, corr_width=2, mandatory_doors=0):
    if mandatory_doors > 0:
        for j in range(mandatory_doors):
            align = random.choice((0, 1, 2, 3))
            if align == 0:
                i = random.randrange(rm.left + 2, rm.right)
                if maze.array[rm.top][i + 1] == '+' or maze.array[rm.top][i - 1] == '+':
                    continue
                maze.array[rm.top][i] = '+'
                new_door = door.Door(i, rm.top, 0, maze.tile_set)
                rm.doors.append(new_door)
            elif align == 1:
                i = random.randrange(rm.top + 2, rm.bottom)
                if maze.array[i + 1][rm.right] == '+' or maze.array[i - 1][rm.right] == '+':
                    continue
                maze.array[i][rm.right] = '+'
                new_door = door.Door(rm.right, i, 1, maze.tile_set)
                rm.doors.append(new_door)
            elif align == 2:
                i = random.randrange(rm.left + 2, rm.right)
                if maze.array[rm.bottom][i + 1] == '+' or maze.array[rm.bottom][i - 1] == '+':
                    continue
                maze.array[rm.bottom][i] = '+'
                new_door = door.Door(i, rm.bottom, 0, maze.tile_set)
                rm.doors.append(new_door)
            elif align == 3:
                i = random.randrange(rm.top + 2, rm.bottom)
                if maze.array[i + 1][rm.left] == '+' or maze.array[i - 1][rm.left] == '+':
                    continue
                maze.array[i][rm.left] = '+'
                new_door = door.Door(rm.left, i, 1, maze.tile_set)
                rm.doors.append(new_door)
        return

    for ar in maze.rooms:
        if rm == ar or ar in rm.adj_rooms:
            continue

        corridor = False
        attached = False
        if rm.top == ar.bottom and rm.left < ar.right - h_merge and rm.right > ar.left + h_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.left + 1, ar.left + 1),
                                            min(rm.right, ar.right), 0, corr_width, '+', '.')
        elif rm.left == ar.right and rm.top < ar.bottom - v_merge and rm.bottom > ar.top + v_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.top + 1, ar.top + 1),
                                            min(rm.bottom, ar.bottom), 3, corr_width, '+', '.')
        elif rm.bottom == ar.top and rm.left < ar.right - h_merge and rm.right > ar.left + h_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.left + 1, ar.left + 1),
                                            min(rm.right, ar.right), 2, corr_width, '+', '.')
        elif rm.right == ar.left and rm.top < ar.bottom - v_merge and rm.bottom > ar.top + v_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.top + 1, ar.top + 1),
                                            min(rm.bottom, ar.bottom), 1, corr_width, '+', '.')

        if attached:
            rm.adj_rooms.append(ar)
            ar.adj_rooms.append(rm)
        if corridor:
            rm.corridor = True
            ar.corridor = True


def rooms_join(maze, room1, room2, ap, bp, align, corr_width, door_byte, corr_byte):
    corridor = False
    attached = False
    if bp - ap <= corr_width and not room1.corridor:
        for i in range(ap, bp):
            if align == 0:
                maze.array[room1.top][i] = corr_byte
            elif align == 1:
                maze.array[i][room1.right] = corr_byte
            elif align == 2:
                maze.array[room1.bottom][i] = corr_byte
            elif align == 3:
                maze.array[i][room1.left] = corr_byte
        corridor = True
        attached = True
    # elif len(room1.doors) + len(room2.doors) < 3:
    # elif len(room2.doors) == 0 or (len(room1.doors) < 3 and len(room2.doors) < 3):
    elif len(room1.doors) < 3 and len(room2.doors) < 3:
        # else:
        i = random.randrange(ap + 1, bp)
        if align == 0:
            maze.array[room1.top][i] = door_byte
            new_door = door.Door(i, room1.top, 0, maze.tile_set)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 1:
            maze.array[i][room1.right] = door_byte
            new_door = door.Door(room1.right, i, 1, maze.tile_set)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 2:
            maze.array[room1.bottom][i] = door_byte
            new_door = door.Door(i, room1.bottom, 0, maze.tile_set)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 3:
            maze.array[i][room1.left] = door_byte
            new_door = door.Door(room1.left, i, 1, maze.tile_set)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        attached = True
    return corridor, attached


def decor_maze(maze):
    maze_height = len(maze.array)
    try:
        maze_width = len(maze.array[0])
    except IndexError:
        return
    fine_maze = maze_array(maze_width, maze_height)

    for i in range(maze_height):
        for j in range(maze_width):
            if maze.array[i][j] == '0':
                if maze.decor_rnds_read:
                    fine_maze[i][j] = (maze.tile_set['floor_tiled'][maze.decor_rnds.pop()],)
                else:
                    rnd = random.randrange(0, len(maze.tile_set['floor_tiled']))
                    fine_maze[i][j] = (maze.tile_set['floor_tiled'][rnd],)
                    maze.decor_rnds.append(rnd)
            elif maze.array[i][j] == ' ':
                pass
            else:
                if maze.decor_rnds_read:
                    fine_maze[i][j] = (maze.tile_set['floor_ground'][maze.decor_rnds.pop()],)
                else:
                    rnd = random.randrange(0, len(maze.tile_set['floor_ground']))
                    fine_maze[i][j] = (maze.tile_set['floor_ground'][rnd],)
                    maze.decor_rnds.append(rnd)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
             (
                 (('0','.'), ('0','.'), ('0','.')),
                 (('0','.'), '#', ('0','.')),
                 (('0','.'), ('0','.'), ('0','.')),
             ),
             (maze.tile_set['floor_ground'], maze.tile_set['column']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
        (
            ('?',       '#',        '?'),
            ('.',       '+',        '?'),
            ('?',       '#',        '?'),
        ),
        (maze.tile_set['floor_ground'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '.', '?'),
             ('#', '+', '#'),
             ('?', '?', '?'),
         ),
         (maze.tile_set['floor_ground'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '#', '?'),
             ('0', '+', '?'),
             ('?', '#', '?'),
         ),
         (maze.tile_set['floor_tiled'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '0', '?'),
             ('#', '+', '#'),
             ('?', '?', '?'),
         ),
         (maze.tile_set['floor_tiled'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '.', '?'),
             ('?', '#', '.'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '0', '?'),
             ('?', '#', '0'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ' ', '?'),
             ('?', '#', ' '),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             (('#', '+'), '#', '#'),
             ('?', '?', '?')
         ),
         (None, maze.tile_set['wall_hor']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ('#', '+'), '?'),
             ('?', '#', '?'),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_ver']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             ('.', '#', '#'),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             ('0', '#', '#'),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             (' ', '#', '#'),
             ('?', ' ', '?')
         ),
         (None, maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ('#', '+'), '?'),
             (('#', '+'), '#', ('.', ' ', '0')),
             ('?', ('.', ' ', '0'), '?')
         ),
         (None, maze.tile_set['wall_corner_se']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             ('?', '#', '#'),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_corner_nw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ('#', '+'), '?'),
             ('.', '#', ('.', '0')),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_end_s']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ('#', '+'), '?'),
             ('0', '#', ('.', '0')),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_end_s']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '.', '?'),
             (('#', '+'), '#', '.'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_end_e']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '0', '?'),
             (('#', '+'), '#', '0'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_end_e']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             (('#', '+'), '#', '+'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['doorway_hor_l'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             ('#', '+', '#'),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['doorway_hor_r']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '?', '?'),
             ('#', '+', '#'),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['doorway_hor_r']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '#', '?'),
             ('?', '+', '.'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['doorway_ver_b']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', '#', '?'),
             ('?', '+', '0'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['doorway_ver_b']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, maze.decor_rnds_read,
         (
             ('?', ('#', '+'), '?'),
             (('.', '0'), '#', ('.', '0')),
             ('?', '+', '?')
         ),
         (maze.tile_set['doorway_ver_t'], None), replace=True)

    if not maze.decor_rnds_read:
        maze.decor_rnds.reverse()
    else:
        maze.decor_rnds = maze.decor_rnds_copy
    return fine_maze


def decorate(maze, fine_maze, maze_width, maze_height, read_rnds, pattern, tiles_list, replace=False):
    locations = pattern_find(maze.array, -1, -1, maze_width + 1, maze_height + 1, pattern, 1, 1, 1, 1)
    if locations is not False:
        for location in locations:
            if replace:
                new_pie = []
                for tile in tiles_list:
                    if tile is None:
                        new_pie.append(None)
                    else:
                        if read_rnds:
                            rnd = maze.decor_rnds.pop()
                        else:
                            rnd = random.randrange(0, len(tile))
                            maze.decor_rnds.append(rnd)
                        new_pie.append(tile[rnd])
                fine_maze[location[1]][location[0]] = tuple(new_pie)
            else:
                dec_list = list(fine_maze[location[1]][location[0]])
                for i in range(0, len(tiles_list)):
                    if tiles_list[i] is None:
                        continue
                    if read_rnds:
                        rnd = maze.decor_rnds.pop()
                    else:
                        rnd = random.randrange(0, len(tiles_list[i]))
                    if i >= len(dec_list):
                        dec_list.append(tiles_list[i][rnd])
                    elif dec_list[i] is None:
                        dec_list[i] = tiles_list[i][rnd]
                fine_maze[location[1]][location[0]] = tuple(dec_list)


def pattern_find(maze, start_x, start_y, end_x, end_y, pattern_matrix, step_hor, step_ver, offset_x, offset_y):
    match_list = []
    matrix_height = len(pattern_matrix)
    matrix_width = len(pattern_matrix[0])
    for i in range(start_x, end_x - matrix_width + 1, step_hor):
        for j in range(start_y, end_y - matrix_height + 1, step_ver):
            if compare_grid_pattern(maze, i, j, pattern_matrix, matrix_width, matrix_height):
                match_list.append((i + offset_x, j + offset_y))
    if len(match_list) > 0:
        return match_list
    else:
        return False


def compare_grid_pattern(maze, lab_x, lab_y, pattern_matrix, matrix_width, matrix_height):
    for m in range(0, matrix_height):
        for n in range(0, matrix_width):
            try:
                lab_byte = maze[lab_y + m][lab_x + n]
            except IndexError:
                lab_byte = ' '
            if lab_byte not in pattern_matrix[m][n] and pattern_matrix[m][n] != '?':
                return False
    return True


def traps_set(maze, attacks_table_point, db, pc):
    traps_num = round(maze.width * maze.height * progression.scale_to_lvl(maze.trap_rate, maze.lvl) // 100)
    room_rnd_list = [(rm, rm.rating) for rm in maze.rooms]
    """trap_density = (    # Level, Percents of a room space
        (1, 10),
        (5, 20),
        (10, 30),
        (15, 40),
        (20, 50),
        (25, 60),
        (30, 70),
        (40, 80),
        (50, 90),
        (60, 100)
    )
    for lv, dens in trap_density:
        if maze.lvl <= lv:
            tr_dens = dens
            break
    else:
        tr_dens = trap_density[-1][1]"""
    tr_dens = 100
    while traps_num > 0 and len(room_rnd_list) > 0:
        tr_room = pickrandom.items_get(room_rnd_list, items_pop=True)[0]
        rm_space = ((tr_room.right - 2) - (tr_room.left + 1)) * ((tr_room.bottom - 2) - (tr_room.top + 1))
        max_traps = rm_space * tr_dens // 100
        for i in range(0, max_traps):
            trap_params_list = dbrequests.trap_params_get(db.cursor, attacks_table_point, maze.lvl)
            if not trap_params_list:
                traps_num = 0
                break
            label, rang, dam_type, dam_val_base, dam_val_spread, init_lvl, sound_trigger = random.choice(trap_params_list)
            dam_val_base, dam_val_spread, lvl = traps_scale(maze, dam_val_base, dam_val_spread)
            x_sq = random.randrange(tr_room.left + 1, tr_room.right - 1)
            y_sq = random.randrange(tr_room.top + 1, tr_room.bottom - 1)
            for ot in tr_room.traps:
                if ot.x_sq == x_sq and ot.y_sq == y_sq:
                    continue
            new_trap = trap.Trap(x_sq, y_sq, lvl, maze.tile_set, label, rang,
                                 dam_type, dam_val_base, dam_val_spread, sound_trigger)
            new_trap.mob_utility_obj = maze.mob_utility_obj
            tr_room.traps.append(new_trap)
            tr_room.rating += 25
            maze.traps.append(new_trap)
            traps_num -= 1


def traps_scale(maze, dam_val_base, dam_val_spread):
    lvl = maze.lvl
    dam_val_base = round(dam_val_base + dam_val_base * maze.TRAP_SCALE_RATE * (lvl - 1))
    dam_val_spread = round(dam_val_spread + dam_val_spread * maze.TRAP_SCALE_RATE * (lvl - 1))
    return dam_val_base, dam_val_spread, lvl


def doors_set(maze, tile_set, db, attack_table_point, bonus_rooms):
    # lock all rooms that are not corridors
    for locked_room in maze.rooms:
        if locked_room.corridor:
            """for dr in locked_room.doors:
                if dr.lock is not None:
                    continue
                if random.randrange(1, 101) <= 20:
                    dr.shut = False"""
            continue
        """if len(locked_room.doors) == 0:
            continue"""
        if random.randrange(1, 9) <= progression.scale_to_lvl(maze.trap_rate, maze.lvl) and locked_room.doors:
            trap_params_list = dbrequests.trap_params_get(db.cursor, attack_table_point, maze.lvl)
            if trap_params_list:
                label, rang, dam_type, dam_val_base, dam_val_spread, init_lvl, sound_trigger = random.choice(trap_params_list)
                dam_val_base, dam_val_spread, lvl = traps_scale(maze, dam_val_base, dam_val_spread)

                new_trap = trap.Trap(None, None, maze.lvl, maze.tile_set, label, rang, dam_type, dam_val_base,
                                     dam_val_spread, sound_trigger)
                new_trap.mob_utility_obj = maze.mob_utility_obj
                random.choice(locked_room.doors).trap = new_trap
                maze.traps.append(new_trap)
                locked_room.rating += 50
        if len(locked_room.doors) <= 1:
            locked_room.rating += 250
        if locked_room not in bonus_rooms:
            continue
        elif random.randrange(1, 101) <= maze.lock_rate:
            if random.randrange(1, 101) <= maze.magic_lock_rate:
                for dr in locked_room.doors:
                    if dr.lock is None:
                        dr.lock = lock.Lock(maze.lvl, magical=True)
                        # chest_set(maze, locked_room, tile_set, 1, db, attack_table_point)
                    dr.shut = True
                locked_room.rating += 250
                square(maze.array, locked_room.top + 1, locked_room.left + 1, locked_room.bottom, locked_room.right,
                       '0', '0', True)
            else:
                for dr in locked_room.doors:
                    if dr.lock is None:
                        dr.lock = lock.Lock(maze.lvl)
                        # chest_set(maze, locked_room, tile_set, 1, db, attack_table_point)
                    dr.shut = True
                locked_room.rating += 250
                square(maze.array, locked_room.top + 1, locked_room.left + 1, locked_room.bottom, locked_room.right,
                       '0', '0', True)
        if locked_room.rating >= 250:
            chest_set(maze, locked_room, tile_set, 1, db, attack_table_point)

    # create list of all doors
    for rm in maze.rooms:
        maze.doors.update(rm.doors)
    dr_remove = [dr for dr in maze.doors if dr.lock is None and random.randrange(1, 101) < 51]
    for dr in dr_remove:
        maze.doors.remove(dr)
        for rm in maze.rooms:
            try:
                rm.doors.remove(dr)
            except ValueError:
                pass

    # check for locked rooms
    for rm in maze.rooms:
        for dr in rm.doors:
            if dr.lock is None:
                rm.locked = False
                break
        else:
            rm.locked = True
    for mz_dr in maze.doors:
        if random.randrange(1, 100) <= maze.grate_rate:
            mz_dr.grate = True
        mz_dr.image = mz_dr.image_update()


def exits_set(maze, exits_list, room_seq):
    room_pool = None
    for i in range(0, len(exits_list)):
        if not room_pool:
            room_pool = room_seq[:]
        dest = exits_list[i][0]
        if exits_list[i][1] == 'exit_up':
            rm = room_pool.pop(0)
        elif exits_list[i][1] == 'exit_down':
            rm = room_pool.pop(-1)
        else:
            rm = random.sample(room_pool, k=1)[0]

        x_sq = random.randrange(rm.left + 1, rm.right)
        y_sq = random.randrange(rm.top + 1, rm.bottom - 1)
        space_list = calc2darray.fill2d(maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                        (x_sq, y_sq), (x_sq, y_sq), 2, 5, r_max=5)
        x_sq, y_sq = space_list[-1]

        new_exit = stairs.Stairs(x_sq, y_sq, -1, -1, dest, rm, maze.tile_set[exits_list[i][1]], exits_list[i][1])
        maze.flag_array[y_sq][x_sq].obj = new_exit
        maze.exits.append(new_exit)


def chest_set(maze, room, tileset, chest_number, db, attack_table_point):
    for i in range(0, chest_number):
        x_sq, y_sq = random.choice(
            ((random.randrange(room.left + 1, room.right - 1), random.choice((room.top + 1, room.bottom - 1))),
             (random.choice((room.left + 1, room.right - 1)), random.randrange(room.top + 1, room.bottom - 1)))
        )
        space_list = calc2darray.fill2d(maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                        (x_sq, y_sq), (x_sq, y_sq), 2, 5, r_max=5)
        x_sq, y_sq = space_list[-1]
        alignment = random.choice((0, 1))
        new_chest = chest.Chest(x_sq, y_sq, alignment, room, tileset, off_x_sq=-0.125, off_y_sq=-0.125, lvl=maze.lvl, items_number=2,
                                gp_number=3, treasure_group=0, item_type=None, char_type=None, container=None,
                                disappear=False)

        diff_mod = 1
        if random.randrange(1, 101) <= maze.lock_rate:
            if random.randrange(1, 101) <= maze.magic_lock_rate:
                new_chest.lock = lock.Lock(new_chest.lvl, magical=True)
            else:
                new_chest.lock = lock.Lock(new_chest.lvl)
            diff_mod += 1
        if random.randrange(1, 9) <= progression.scale_to_lvl(maze.trap_rate, new_chest.lvl):
            trap_params_list = dbrequests.trap_params_get(db.cursor, attack_table_point, new_chest.lvl)
            if not trap_params_list:
                continue
            label, rang, dam_type, dam_val_base, dam_val_spread, init_lvl, sound_trigger = random.choice(trap_params_list)
            dam_val_base, dam_val_spread, lvl = traps_scale(maze, dam_val_base, dam_val_spread)
            new_trap = trap.Trap(None, None, maze.lvl, maze.tile_set, label, rang, dam_type, dam_val_base,
                                 dam_val_spread, sound_trigger)
            new_trap.mob_utility_obj = maze.mob_utility_obj
            new_chest.trap = new_trap
            maze.traps.append(new_trap)
            diff_mod += 1

        new_chest.items_number *= diff_mod
        new_chest.gp_number *= diff_mod

        maze.chests.append(new_chest)


def well_set(maze, room_seq, bonus_rooms):
    room_list = [rm for rm in bonus_rooms if not rm.locked]
    if len(room_list) == 0:
        room_list = [rm for rm in room_seq]
    rnd_room = random.choice(room_list)
    x_sq, y_sq = random.choice(
        ((random.randrange(rnd_room.left + 1, rnd_room.right - 2), random.choice((rnd_room.top + 1, rnd_room.bottom - 2))),
         (random.choice((rnd_room.left + 1, rnd_room.right - 2)), random.randrange(rnd_room.top + 1, rnd_room.bottom - 2)))
    )
    space_list = calc2darray.fill2d(maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                    (x_sq, y_sq), (x_sq, y_sq), 2, 5, r_max=5)
    x_sq, y_sq = space_list[-1]
    new_chest = chest.Chest(x_sq, y_sq, None, rnd_room, maze.tile_set, off_x_sq=-0.125, off_y_sq=-0.125, lvl=maze.lvl, items_number=0,
                            gp_number=0, treasure_group=0, item_type=None, char_type=None, container=[
                                treasure.Treasure(146, maze.lvl, maze.db.cursor, maze.tile_sets, maze.resources,
                                                  maze.audio, maze.resources.fate_rnd, grade=1)
                            ], disappear=False, allow_mimic=False, name_replace='well')
    maze.flag_array[y_sq][x_sq].obj = new_chest
    maze.chests.append(new_chest)


def furniture_set(maze):
    total_amount = len(maze.rooms) * maze.stage_dict['furniture_rate'] // 100
    room_pool = [(rm, rm.rating) for rm in maze.rooms]
    furn_rooms = pickrandom.items_get(room_pool, total_amount)
    for furn_room in furn_rooms:
        if furn_room.corridor:
            furn_type = 'corridor'
        elif furn_room.locked:
            furn_type = 'treasury'
        else:
            furn_type = None
        furniture_add(maze.db, maze, furn_room, 1, 'dungeon', furn_type)


def furniture_add(db, maze, maze_room, amount=1, furn_tag=None, furn_type=None, solid=None, on_wall=None):
    furn_list = dbrequests.furniture_get(db.cursor, furn_tag, furn_type, solid, on_wall, 10000)
    random.shuffle(furn_list)
    for i in range(amount):
        furn = furn_list.pop()
        if furn['on_wall'] == 1:
            furn_align = random.choice((0, 3))
        else:
            furn_align = random.choice((0, 1, 2, 3))
        furn_image = dbrequests.furniture_get_image(db.cursor, furn['furniture_id'], furn_align)
        if furn['on_wall'] is None:
            furn['on_wall'] = random.choice((True, False))
        xy_sq = furniture_get_place(maze, maze_room, furn_align, furn['on_wall'], furn['width_sq'], furn['height_sq'])
        if xy_sq is None:
            continue
        x_sq, y_sq = xy_sq
        furn = furniture.Furniture(furn['furniture_type'], x_sq, y_sq, furn_align, maze_room, furn_image,
                                        maze.tile_sets, furn['solid'], furn['offset_x'], furn['offset_y'],
                                   render_later=(furn['on_wall'] == 1 and furn['width_sq'] == 1))
        maze.furnitures.append(furn)


def furniture_get_place(maze, maze_room, furn_align, on_wall, width_sq, height_sq):
    if on_wall == 1:
        if furn_align == 0:
            y_sq = maze_room.top
            rnd_list = [x for x in range(maze_room.left + 1 + (width_sq > 1), maze_room.right)
                        if maze.array[y_sq][x] == '#'
                        and maze.array[y_sq][x - (width_sq > 1)] == '#'
                        and not maze.flag_array[y_sq + (height_sq > 1)][x].obj]
            if len(rnd_list) < 2:
                return None
            x_sq = random.choice(rnd_list)
            y_sq += (height_sq > 1)
        elif furn_align == 3:
            x_sq = maze_room.left
            rnd_list = [y for y in range(maze_room.top + 1 + (height_sq > 1), maze_room.bottom)
                        if maze.array[y][x_sq] == '#'
                        and maze.array[y - (width_sq > 1)][x_sq] == '#'
                        and not maze.flag_array[y][x_sq + (width_sq > 1)].obj]
            if len(rnd_list) < 2:
                return None
            y_sq = random.choice(rnd_list)
            x_sq += (width_sq > 1)
        else:
            return None
    else:
        if furn_align == 0:
            orig_xy_sq = random.choice(
                ((maze_room.left + 1, maze_room.top + 1), (maze_room.right - 1, maze_room.top + 1))
            )
        elif furn_align == 1:
            orig_xy_sq = random.choice(
                ((maze_room.right - 1, maze_room.top + 1), (maze_room.right - 1, maze_room.bottom -1))
            )
        elif furn_align == 2:
            orig_xy_sq = random.choice(
                ((maze_room.left + 1, maze_room.bottom - 1), (maze_room.right - 1, maze_room.bottom -1))
            )
        elif furn_align == 3:
            orig_xy_sq = random.choice(
                ((maze_room.left + 1, maze_room.top + 1), (maze_room.left + 1, maze_room.bottom -1))
            )
        else:
            return None

        space_list = calc2darray.fill2d(maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                        orig_xy_sq, orig_xy_sq, 2, 10, r_max=10)
        x_sq, y_sq = random.choice(space_list)

    if x_sq is None or y_sq is None:
        return None
    else:
        return x_sq, y_sq


def array_pattern_apply(array, pattern, x, y):
    for i in range(0, len(pattern)):
        for j in range(0, len(pattern[i])):
            array[y + i][x + j] = pattern[i][j]


def populate(db, maze, pc, animations, fate_rnd):
    maze_monster_pool = []
    pop_level = maze.stage_dict['lvl'] or pc.char_sheet.level
    mon_ids = maze.monster_ids[:]
    for i in range(0, maze.monster_number):
        new_mon = dbrequests.monster_get_by_id(db.cursor, pickrandom.items_get(mon_ids, 1)[0], fate_rnd)
        if new_mon['lvl'] > pop_level:
            mon_ids = [(mon_id[0], mon_id[1]) for mon_id in mon_ids if mon_id[0] != new_mon['monster_id']]
            new_mon = dbrequests.monster_get_by_id(db.cursor, pickrandom.items_get(mon_ids, 1)[0], fate_rnd)
        maze_monster_pool.append(new_mon)
    for mon in maze_monster_pool:
        # Monster grade definining
        grade_list = dbrequests.grade_set_get(db.cursor, mon['grade_set_monster'], pop_level)
        if len(grade_list) > 0:
            if len(grade_list) > 1:
                mon['grade'] = pickrandom.items_get([(grade, grade['roll_chance']) for grade in grade_list])[0]
            else:
                mon['grade'] = grade_list[0]
        else:
            mon['grade'] = None
        del mon['grade_set_monster']
        monster_apply_grade(db, mon, pop_level, maze.resources.fate_rnd)
        scale_mob(mon, pop_level, maze)

    getattr(maze, maze.stage_dict['populate_algorythm'])(db, maze, animations, maze_monster_pool,
                                                         maze.monster_number, pop_level)


def mob_populate_alg_1(db, maze, animations, maze_monster_pool, monster_number, pop_level):
    rooms_list = maze.rooms[:]
    for ex in maze.exits:
        try:
            rooms_list.remove(ex.room)
        except ValueError:
            pass
    if not rooms_list:
        return
    random.shuffle(rooms_list)
    random.shuffle(maze_monster_pool)
    reserved_rooms = []
    while len(maze_monster_pool) > 0 and (len(rooms_list) > 0 or len(reserved_rooms) > 0):
        if len(rooms_list) > 0:
            rm = rooms_list.pop()
            if len(rm.traps) > 0:
                reserved_rooms.append(rm)
                continue
        else:
            rm = reserved_rooms.pop()
        rm_space = ((rm.right - 2) - (rm.left + 1)) * ((rm.bottom - 2) - (rm.top + 1))
        room_mobs = []
        mob_types_set = set()
        for j in range(len(maze_monster_pool) - 1, -1, -1):
            mob = maze_monster_pool[j]
            if mob['monster_id'] not in mob_types_set and len(mob_types_set) > 1:
                continue
            mob_types_set.add(mob['monster_id'])
            room_mobs.append(mob)
            del maze_monster_pool[j]
            if len(room_mobs) == rm_space:
                break
        x_sq = (rm.left + rm.right - 1) // 2
        y_sq = (rm.top + rm.bottom - 1) // 2
        space_list = calc2darray.fill2d(maze.flag_array, ('mov', 'obj', 'door', 'floor'),
                                        (x_sq, y_sq), (x_sq, y_sq), len(room_mobs) + 1, 10, r_max=20)
        for mon_x_sq, mon_y_sq in space_list[1:]:
            rm_mob = room_mobs.pop()
            mob_add(maze, mon_x_sq, mon_y_sq, animations, rm_mob)


def mob_add(maze, mon_x_sq, mon_y_sq, animations, mob_props):
    if mob_props['behavior'] == 'lurker':
        maze.mobs.append(
            monster.Lurker(
                mon_x_sq, mon_y_sq, animations.get_animation(mob_props['animation']), mob_props, state=0
            )
        )
    elif mob_props['behavior'] == 'mimic':
        maze.mobs.append(
            monster.Mimic(
                mon_x_sq, mon_y_sq, animations.get_animation(mob_props['animation']), mob_props, state=0
            )
        )
    elif mob_props['behavior'] == 'giant':
        maze.mobs.append(
            monster.Giant(
                mon_x_sq, mon_y_sq, animations.get_animation(mob_props['animation']), mob_props, state=0
            )
        )
    else:   # Catch-all safe option
        maze.mobs.append(
            monster.Lurker(
                mon_x_sq, mon_y_sq, animations.get_animation(mob_props['animation']), mob_props, state=0
            )
        )
    new_mob = maze.mobs[-1]
    maze.flag_array[mon_y_sq][mon_x_sq].mon = new_mob
    return new_mob


def roll_monsters(db_cursor, max_level, max_grade, monster_types, mon_amount=1):
    rnd_roll = random.randrange(0, 10001)
    monster_ids = dbrequests.get_monsters(db_cursor, max_level, max_grade, monster_types, rnd_roll)
    monster_list = []
    for i in range(0, mon_amount):
        monster_list.append(monster_ids[random.randrange(0, len(monster_ids))])
    return monster_list


def scale_mob(mob_stats, level, maze):
    init_level = mob_stats['lvl']
    mob_stats['hp_max'] = round(mob_stats['hp_max'] + mob_stats['hp_max'] * (maze.MOB_HP_SCALE_RATE * ((level - 1) * level / 2)))

    mob_stats['exp'] = round(mob_stats['exp'] + mob_stats['exp'] * maze.EXP_SCALE_RATE * (level - 1))
    # Gold being scaled during drop generation.
    # mob_stats['gold'] = round(mob_stats['gold'] * level / init_level * scale_rate)
    for m_a in mob_stats['attacks_melee']:
        mob_scale_attack(m_a, level, init_level, maze.MOB_DMG_SCALE_RATE)
    for m_r in mob_stats['attacks_ranged']:
        mob_scale_attack(m_r, level, init_level, maze.MOB_DMG_SCALE_RATE)

    mob_stats['init_lvl'] = init_level
    mob_stats['lvl'] = level

    return mob_stats


def mob_scale_attack(m_a, level, init_level, scale_rate):
    m_a['attack_val_base'] = round(m_a['attack_val_base'] + m_a['attack_val_base'] * scale_rate * (level - 1))
    m_a['attack_val_spread'] = round(m_a['attack_val_spread'] + m_a['attack_val_spread'] * scale_rate * (level - 1))


def monster_apply_grade(db, mob_stats, pop_level, fate_rnd):
    if mob_stats['grade'] is None:
        return

    if mob_stats['grade']['affix_amount'] > 0:
        affix_ids = set()
        if mob_stats['grade']['affix_amount'] >= 2:
            affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], pop_level, mob_stats['monster_type'], is_suffix=0))
        if mob_stats['grade']['affix_amount'] >= 3:
            affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], pop_level, mob_stats['monster_type'], is_suffix=0))
        affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], pop_level, mob_stats['monster_type']))
        if None in affix_ids:
            affix_ids.remove(None)
        for aff in affix_ids:
            mob_affix_add(db.cursor, mob_stats, dbrequests.affix_mob_get_by_id(db.cursor, aff), fate_rnd)
            new_melee_att, new_ranged_att = dbrequests.affixed_attack_get(db.cursor, aff)
            mob_stats['attacks_ranged'].extend(new_ranged_att)
            mob_stats['attacks_melee'].extend(new_melee_att)

    # images_update(db_cursor, loot_props, tile_sets)
    # sounds_update(db_cursor, loot_props)

    # FOR TESTING PURPOSES:
    """debuff.DeBuff(dbrequests.de_buff_get_by_id(realm.db.cursor, 1)[0], target.de_buff_dict)
    wins_dict['target'].refresh_aim()
    target.wound(damage, 'att_physical', False, is_crit, wins_dict, fate_rnd, pc)"""


def mob_roll_affix(db_cursor, grade, pop_level, monster_type, is_suffix=None):
    rnd_roll = random.randrange(0, 10001)
    affix_ids = dbrequests.get_affixes_mob(db_cursor, pop_level, grade, monster_type, rnd_roll, is_suffix=is_suffix)
    if len(affix_ids) > 0:
        return random.choice(affix_ids)
    else:
        return None


def mob_affix_add(db_cursor, mob_stats, affix_dicts, fate_rnd):
    base_props, modifier_list, de_buff_list = affix_dicts

    # inserting modifiers
    base_props['mods'] = {}
    for mod_dict in modifier_list:
        initmod.init_modifier(base_props, mod_dict, fate_rnd)

    for key, value in base_props['mods'].items():
        if value['value_type'] == 2:
            mob_stats[key] += mob_stats[key] * value['value_base'] // 1000
        elif value['value_type'] == 1:
            mob_stats[key] += value['value_base']
        elif value['value_type'] == 0:
            mob_stats[key] = value['value_base']

    # inserting de_buffs
    for db_dict in de_buff_list:
        modifier_list = dbrequests.de_buff_get_mods(db_cursor, db_dict['de_buff_id'])

        db_dict['mods'] = {}
        for mod_dict in modifier_list:
            initmod.init_modifier(db_dict, mod_dict, fate_rnd)

        for key, value in db_dict['mods'].items():
            if value['value_type'] == 2:
                mob_stats[key] += mob_stats[key] * value['value_base'] // 1000

    base_props['de_buffs'] = de_buff_list

    if 'affixes' not in mob_stats:
        mob_stats['affixes'] = [base_props]
    else:
        mob_stats['affixes'].append(base_props)


def flags_create(maze, array):
    flags_array = maze_array(maze.width, maze.height, 0)
    for i in range(0, maze.height):
        for j in range(0, maze.width):
            flags_array[i][j] = flagtile.FlagTile(
                None, None, None, None, [],
                (array[i][j] in ('.', '+', '0')),
                (array[i][j] in ('.', '+', '0')),
                False, None,
                (array[i][j] in ('.', '0'))
            )
    return flags_array


def flags_update(maze, flags_array):
    for dr in maze.doors:
        fl = flags_array[dr.y_sq][dr.x_sq]
        fl.door = dr
        if dr.shut:
            fl.mov = False
            if not dr.grate:
                fl.light = False
    for fu in maze.furnitures:
        fl = flags_array[round(fu.y_sq)][round(fu.x_sq)]
        fl.mov = fl.mov and not fu.solid
        fl.obj = fu
    for tr in maze.triggers:
        fl = flags_array[round(tr.y_sq)][round(tr.x_sq)]
        fl.mov = False
        fl.obj = tr
    for ex in maze.exits:
        fl = flags_array[ex.y_sq][ex.x_sq]
        fl.mov = False
        fl.obj = ex
        # fl.light = True
    for ch in maze.chests:
        fl = flags_array[ch.y_sq][ch.x_sq]
        fl.mov = False
        fl.obj = ch
    for tr in maze.traps:
        if tr.x_sq is not None and tr.y_sq is not None:
            flags_array[tr.y_sq][tr.x_sq].trap = tr
    for mob in maze.mobs:
        maze.flag_array[round(mob.y_sq)][round(mob.x_sq)].mon = mob
    for loot in maze.loot:
        maze.flag_array[round(loot.y_sq)][round(loot.x_sq)].item.append(loot)


def get_chapter_stage(db, chapter, stage_index):
    rnd_roll = random.randrange(1, 10001)
    stages_list = dbrequests.stage_get(db.cursor, chapter['chapter_id'], stage_index, rnd_roll)
    if len(stages_list) > 0:
        stage = random.sample(stages_list, 1)
        return stage[0]
    else:
        return None


def grate_controls(maze, rooms):
    bonus_rooms = [rm for rm in maze.rooms if not rm.locked and rm not in rooms and any(rrm in rooms for rrm in rm.adj_rooms)]
    if not bonus_rooms:
        bonus_rooms = rooms
    maze.doors = list(maze.doors)
    control_list = [[] for rm in rooms]
    control_list_tr = [[] for rm in bonus_rooms]
    grate_list = []
    grate_locked_list = []
    for dr in maze.doors:
        if not dr.grate:
            continue
        if dr.lock is None:
            grate_list.append(maze.doors.index(dr))
    for rm in maze.rooms:
        if not rm.locked:
            continue
        rm_grates = []
        for dr in rm.doors:
            if dr.grate and dr.lock is not None:
                rm_grates.append(maze.doors.index(dr))
        if rm_grates:
            grate_locked_list.append(rm_grates)
    random.shuffle(grate_list)
    random.shuffle(grate_locked_list)
    if control_list:
        while grate_list:
            control_list[random.randrange(0, len(control_list))].append(grate_list.pop())
    if control_list_tr:
        while grate_locked_list:
            control_list_tr[random.randrange(0, len(control_list_tr))].extend(grate_locked_list.pop())
    modifier = 0
    for tr_list in (control_list, control_list_tr):
        while tr_list:
            ctrl_grates = tr_list.pop()
            if not ctrl_grates:
                continue
            if tr_list == control_list:
                min_rm_index = len(rooms) - 1
                for gr in ctrl_grates:
                    for rm in maze.rooms:
                        if maze.doors[gr] in rm.doors and rm in rooms:
                            min_rm_index = min(min_rm_index, rooms.index(rm))
                lever_room = rooms[max(min_rm_index - modifier, 0)]
            else:
                lever_room = random.choice(bonus_rooms)
            hor_spaces = [(x, lever_room.top) for x in range(lever_room.left + 1, lever_room.right)
                            if maze.array[lever_room.top][x] == '#'
                                and maze.array[lever_room.top][x + 1] == '#'
                                and maze.array[lever_room.top][x - 1] == '#'
                                and not maze.flag_array[lever_room.top][x].obj]
            ver_spaces = [(lever_room.left, y) for y in range(lever_room.top + 1, lever_room.bottom)
                            if maze.array[y][lever_room.left] == '#'
                                and maze.array[y + 1][lever_room.left] == '#'
                                and maze.array[y - 1][lever_room.left] == '#'
                                and not maze.flag_array[y][lever_room.left].obj]
            if hor_spaces:
                x_sq, y_sq = random.choice(hor_spaces)
                alignment = 0
            elif ver_spaces:
                x_sq, y_sq = random.choice(ver_spaces)
                alignment = 1
            else:
                if lever_room in bonus_rooms:
                    tr_list.append(ctrl_grates)
                    continue
                elif rooms.index(lever_room) > 0:
                    modifier += 1
                    tr_list.append(ctrl_grates)
                    continue
                else:
                    for gr in ctrl_grates:
                        if not maze.doors[gr].lock:
                            maze.doors[gr].shut = False
                            maze.flag_array[maze.doors[gr].y_sq][maze.doors[gr].x_sq].mov = True
                    continue
            new_trigger = trigger.Trigger(x_sq, y_sq, alignment, maze.tile_set, ctrl_grates, value=False)
            maze.triggers.append(new_trigger)
            maze.flag_array[y_sq][x_sq].obj = new_trigger
