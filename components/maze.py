import random
from library import maths
from library import pickrandom, calc2darray, itemlist
from components import dbrequests, progression, room, door, stairs, trap, lock, flagtile, monster, gamesave, chest, initmod, treasure


class Maze:
    def __init__(self, db, animations, tile_sets, audio, pc, resources, use_saves=True):
        self.db = db
        self.animations = animations
        self.resources = resources

        self.MOB_HP_SCALE_RATE = 0.3
        self.MOB_DMG_SCALE_RATE = 0.2
        self.EXP_SCALE_RATE = 0.3
        # self.GOLD_SCALE_RATE = 1.3
        self.TRAP_SCALE_RATE = 0.2

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

        self.mob_utility_obj = monster.Monster(0, 0, None, {
            'label': 'deadly trap',
            'crit_chance': 5,
            'hp_max': None,
            'speed': None,
            'lvl': self.lvl
        }, 0)
        self.mob_utility_obj.alive = False

        self.tradepost_update = False

        self.tile_set = tile_sets.get_maze_tiles(self.stage_dict['tile_set'])
        self.trap_rate = self.stage_dict['trap_rate']
        self.lock_rate = self.stage_dict['lock_rate']
        self.grate_rate = self.stage_dict['grate_rate']
        self.magic_lock_rate = self.stage_dict['magic_lock_rate']
        self.monster_ids = self.stage_dict['monsters']
        self.monster_number = self.stage_dict['monster_number']

        self.array = maze_array(self.width, self.height)
        self.decor_rnds = []
        self.decor_array = None

        self.rooms = None
        self.doors = set()
        self.chests = []
        self.mobs = []
        self.traps = []
        self.exits = []
        self.loot = itemlist.ItemList(filters={
                'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                               'orb_ammo', 'orb_source', 'use_wand', 'exp_tools', 'exp_lockpick', 'exp_food', 'exp_key',
                               'light', 'aug_gem', 'sup_potion'],
            })
        self.text = []

        self.ANIM_LEN = 4
        self.anim_frame = 0
        self.anim_timing = self.stage_dict['anim_timing']
        self.anim_timer = 0

        # WORKING WITH PREGENERATED DATA
        stage_progress = dbrequests.chapter_progress_get(db.cursor, pc.char_sheet.id, stage_index=self.stage_index)
        if len(stage_progress) > 0 and use_saves:
            gamesave.load_maze(pc, self, db, tile_sets, animations)
        else:
            self.tradepost_update = True

        if len(stage_progress) == 0 or stage_progress[0]['maze_rolled'] == 0 or not use_saves:
            # self.generate_1(0, 0, self.height - 1, self.width - 1, 8, 8, False)
            getattr(self, self.stage_dict['maze_algorythm'])(pc, 0, 0, self.height-1, self.width-1,
                                                             self.stage_dict['room_min_width'],
                                                             self.stage_dict['room_min_height'], True)
        self.flag_array = flags_create(self, self.array)
        if len(stage_progress) == 0 or stage_progress[0]['monsters_rolled'] == 0 or not use_saves:
            populate(self.db, self, pc, self.animations)
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
        traps_set(self, 'monster_attacks', self.db, pc)

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


def rooms_attached(maze, rm, v_merge=1, h_merge=1, corr_width=2):
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
    read_rnds = False
    if maze.decor_rnds:
        read_rnds = True
        decor_rnds_copy = maze.decor_rnds.copy()
    maze_height = len(maze.array)
    try:
        maze_width = len(maze.array[0])
    except IndexError:
        return
    fine_maze = maze_array(maze_width, maze_height)

    for i in range(maze_height):
        for j in range(maze_width):
            if maze.array[i][j] == '0':
                if read_rnds:
                    fine_maze[i][j] = (maze.tile_set['floor_tiled'][maze.decor_rnds.pop()],)
                else:
                    rnd = random.randrange(0, len(maze.tile_set['floor_tiled']))
                    fine_maze[i][j] = (maze.tile_set['floor_tiled'][rnd],)
                    maze.decor_rnds.append(rnd)
            elif maze.array[i][j] == ' ':
                pass
            else:
                if read_rnds:
                    fine_maze[i][j] = (maze.tile_set['floor_ground'][maze.decor_rnds.pop()],)
                else:
                    rnd = random.randrange(0, len(maze.tile_set['floor_ground']))
                    fine_maze[i][j] = (maze.tile_set['floor_ground'][rnd],)
                    maze.decor_rnds.append(rnd)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
        (
            ('?',       '#',        '?'),
            ('.',       '+',        '?'),
            ('?',       '#',        '?'),
        ),
        (maze.tile_set['floor_ground'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '.', '?'),
             ('#', '+', '#'),
             ('?', '?', '?'),
         ),
         (maze.tile_set['floor_ground'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '#', '?'),
             ('0', '+', '?'),
             ('?', '#', '?'),
         ),
         (maze.tile_set['floor_tiled'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '0', '?'),
             ('#', '+', '#'),
             ('?', '?', '?'),
         ),
         (maze.tile_set['floor_tiled'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '.', '?'),
             ('?', '#', '.'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '0', '?'),
             ('?', '#', '0'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ' ', '?'),
             ('?', '#', ' '),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_corner_ne']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             (('#', '+'), '#', '#'),
             ('?', '?', '?')
         ),
         (None, maze.tile_set['wall_hor']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ('#', '+'), '?'),
             ('?', '#', '?'),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_ver']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             ('.', '#', '#'),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             ('0', '#', '#'),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             (' ', '#', '#'),
             ('?', ' ', '?')
         ),
         (None, maze.tile_set['wall_corner_sw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ('#', '+'), '?'),
             (('#', '+'), '#', ('.', ' ', '0')),
             ('?', ('.', ' ', '0'), '?')
         ),
         (None, maze.tile_set['wall_corner_se']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             ('?', '#', '#'),
             ('?', '#', '?')
         ),
         (None, maze.tile_set['wall_corner_nw']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ('#', '+'), '?'),
             ('.', '#', ('.', '0')),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_end_s']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ('#', '+'), '?'),
             ('0', '#', ('.', '0')),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_end_s']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '.', '?'),
             (('#', '+'), '#', '.'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['wall_end_e']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '0', '?'),
             (('#', '+'), '#', '0'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['wall_end_e']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             (('#', '+'), '#', '+'),
             ('?', ('.', '0'), '?')
         ),
         (maze.tile_set['doorway_hor_l'], None), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             ('#', '+', '#'),
             ('?', '.', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['doorway_hor_r']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '?', '?'),
             ('#', '+', '#'),
             ('?', '0', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['doorway_hor_r']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '#', '?'),
             ('?', '+', '.'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_ground'], maze.tile_set['doorway_ver_b']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', '#', '?'),
             ('?', '+', '0'),
             ('?', '#', '?')
         ),
         (maze.tile_set['floor_tiled'], maze.tile_set['doorway_ver_b']), replace=True)

    decorate(maze, fine_maze, maze_width, maze_height, read_rnds,
         (
             ('?', ('#', '+'), '?'),
             (('.', '0'), '#', ('.', '0')),
             ('?', '+', '?')
         ),
         (maze.tile_set['doorway_ver_t'], None), replace=True)

    if not read_rnds:
        maze.decor_rnds.reverse()
    else:
        maze.decor_rnds = decor_rnds_copy
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
                match_list.append([i + offset_x, j + offset_y])
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
    trap_density = (    # Level, Percents of a room space
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
        tr_dens = trap_density[-1][1]
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
            for dr in locked_room.doors:
                if dr.lock is not None:
                    continue
                if random.randrange(1, 101) <= 20:
                    dr.shut = False
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
    dr_remove = [dr for dr in maze.doors if dr.lock is None and random.randrange(1, 101) < 81]
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

        new_exit = stairs.Stairs(x_sq, y_sq, -24, -24, dest, rm, maze.tile_set[exits_list[i][1]], exits_list[i][1])

        maze.exits.append(new_exit)


def chest_set(maze, room, tileset, chest_number, db, attack_table_point):
    for i in range(0, chest_number):
        x_sq, y_sq = random.choice(
            ((random.randrange(room.left + 1, room.right - 1), random.choice((room.top + 1, room.bottom - 1))),
             (random.choice((room.left + 1, room.right - 1)), random.randrange(room.top + 1, room.bottom - 1)))
        )
        space_list = calc2darray.fill2d(maze.flag_array, {'mov': False, 'obj': 'True', 'floor': False},
                                        (x_sq, y_sq), (x_sq, y_sq), 1, 5, r_max=5)
        x_sq, y_sq = space_list[0]
        alignment = random.choice((0, 1))
        new_chest = chest.Chest(x_sq, y_sq, alignment, room, tileset, off_x=-4, off_y=-4, lvl=maze.lvl, items_number=2,
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


def array_pattern_apply(array, pattern, x, y):
    for i in range(0, len(pattern)):
        for j in range(0, len(pattern[i])):
            array[y + i][x + j] = pattern[i][j]


def populate(db, maze, pc, animations):
    maze_monster_pool = []
    pop_level = maze.stage_dict['lvl'] or pc.char_sheet.level
    mon_ids = maze.monster_ids[:]
    for i in range(0, maze.monster_number):
        new_mon = dbrequests.monster_get_by_id(db.cursor, pickrandom.items_get(mon_ids, 1)[0])
        if new_mon['lvl'] > pop_level:
            mon_ids = [(mon_id[0], mon_id[1]) for mon_id in mon_ids if mon_id[0] != new_mon['monster_id']]
            new_mon = dbrequests.monster_get_by_id(db.cursor, pickrandom.items_get(mon_ids, 1)[0])
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
        monster_apply_grade(db, mon, maze.resources.fate_rnd)
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
        space_list = calc2darray.fill2d(maze.flag_array,
                                        {'mov': False, 'obj': True, 'door': True, 'floor': False},
                                        (x_sq, y_sq), (x_sq, y_sq), len(room_mobs) + 1, 10, r_max=20)
        for mon_x_sq, mon_y_sq in space_list[1:]:
            rm_mob = room_mobs.pop()
            maze.mobs.append(
                monster.Monster(
                    mon_x_sq, mon_y_sq, animations.get_animation(rm_mob['animation']), rm_mob, state=0
                )
            )


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


def monster_apply_grade(db, mob_stats, fate_rnd):
    if mob_stats['grade'] is None:
        return

    if mob_stats['grade']['affix_amount'] > 0:
        affix_ids = set()
        if mob_stats['grade']['affix_amount'] >= 2:
            affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], mob_stats, is_suffix=0))
        if mob_stats['grade']['affix_amount'] >= 3:
            affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], mob_stats, is_suffix=0))
        affix_ids.add(mob_roll_affix(db.cursor, mob_stats['grade']['grade_level'], mob_stats))
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


def mob_roll_affix(db_cursor, grade, mob_stats, is_suffix=None):
    rnd_roll = random.randrange(0, 10001)
    affix_ids = dbrequests.get_affixes_mob(db_cursor, mob_stats['lvl'], grade, mob_stats['monster_type'], rnd_roll,
                                            is_suffix=is_suffix)
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
                False, False,
                (array[i][j] in ('.', '+', '0'))
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
