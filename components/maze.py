import random
from library import maths
from library import pickrandom, calc2darray, itemlist
from components import dbrequests, progression, room, door, stairs, trap, lock, flagtile, monster


class Maze:
    def __init__(self, db, animations, width, height, lvl, exits_list, tile_set,
                 monster_types=None, monster_type_amount=2, monster_amount_rate=1,
                 anim_timing=15, trap_rate=1, lock_rate=70, magic_lock_rate=30):
        self.db = db
        self.animations = animations
        self.width = width
        self.height = height
        self.lvl = lvl
        self.exits_list = exits_list
        self.tile_set = tile_set
        self.trap_rate = trap_rate
        self.lock_rate = lock_rate
        self.magic_lock_rate = magic_lock_rate
        self.monster_types = monster_types
        self.monster_type_amount = monster_type_amount
        self.monster_amount_rate = monster_amount_rate

        self.array = maze_array(width, height)
        self.decor_array = None
        self.flag_array = None

        self.rooms = None
        self.doors = set()
        self.mobs = []
        self.traps = []
        self.exits = []
        self.loot = itemlist.ItemList(filters={
                'item_types': ['wpn_melee', 'wpn_ranged', 'wpn_magic', 'arm_head', 'arm_chest', 'acc_ring', 'orb_shield',
                           'orb_ammo', 'orb_source', 'use_potion', 'use_wand', 'use_tools', 'light'],
            })
        self.text = []

        self.ANIM_LEN = 4
        self.anim_frame = 0
        self.anim_timing = anim_timing
        self.anim_timer = 0

        self.generate_1(0, 0, height - 1, width - 1, 8, 8, False)

    def generate_1(self, top, left, bottom, right, min_width, min_height, prop, vert_chance=50):
        self.rooms = split_build(top, left, bottom, right, min_width, min_height, prop, r_limit=14)
        random.shuffle(self.rooms)
        for i in range(0, len(self.rooms) // 10):
            del self.rooms[0]
        for rm in self.rooms:
            square(self.array, rm.top, rm.left, rm.bottom + 1, rm.right + 1, '#', '.', True)
        for rm in self.rooms:
            rooms_attached(self, rm, 2, 2, max(min_width, min_height))
        self.flag_array = flags_create(self, self.array)
        exits_set(self, self.exits_list)
        doors_set(self, self.tile_set, self.db)
        traps_set(self, 'monster_attacks', self.db)
        self.decor_array = decor_maze(self.array, self.tile_set, self.flag_array)
        flags_update(self, self.flag_array)

        populate(self.db, self, self.animations)

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


def split_build(top, left, bottom, right, min_width, min_height, prop, vertical=50, r_limit=4):
    if r_limit <= 0:
        return []
    room_list = []
    width = right - left
    height = bottom - top
    if random.randrange(1, 101) <= vertical or (prop and width > height):
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


def decor_maze(maze, tile_set, flag_array):
    maze_height = len(maze)
    try:
        maze_width = len(maze[0])
    except IndexError:
        return
    fine_maze = maze_array(maze_width, maze_height)

    for i in range(maze_height):
        for j in range(maze_width):
            if maze[i][j] == '0':
                fine_maze[i][j] = [random.choice(tile_set['floor_tiled']),]
            elif maze[i][j] == ' ':
                pass
            else:
                fine_maze[i][j] = [random.choice(tile_set['floor_ground']), ]

    decorate(maze, fine_maze, maze_width, maze_height,
        (
            ('?',       '#',        '?'),
            ('.',       '+',        '?'),
            ('?',       '#',        '?'),
        ),
        [
            random.choice(tile_set['floor_ground']),
        ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
         (
             ('?', '.', '?'),
             ('#', '+', '#'),
             ('?', '?', '?'),
         ),
         [
             random.choice(tile_set['floor_ground']),
         ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '#', '?'),
                 ('0', '+', '?'),
                 ('?', '#', '?'),
             ),
             [
                 random.choice(tile_set['floor_tiled']),
             ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '0', '?'),
                 ('#', '+', '#'),
                 ('?', '?', '?'),
             ),
             [
                 random.choice(tile_set['floor_tiled']),
             ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('.', '0'), '?'),
                 ('?', '#', ('.', '0')),
                 ('?', '#', '?')
             ),
             (
                 random.choice(tile_set['wall_corner_ne']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ' ', '?'),
                 ('?', '#', ' '),
                 ('?', '#', '?')
             ),
             [
                 random.choice(tile_set['wall_corner_ne']),
             ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 (('#', '+'), '#', '#'),
                 ('?', '?', '?')
             ),
             (
                 random.choice(tile_set['wall_hor']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('#', '+'), '?'),
                 ('?', '#', '?'),
                 ('?', '#', '?')
             ),
             (
                 random.choice(tile_set['wall_ver']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 (('.', '0'), '#', '#'),
                 ('?', ('.', '0'), '?')
             ),
             (
                 random.choice(tile_set['wall_corner_sw']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 (' ', '#', '#'),
                 ('?', ' ', '?')
             ),
             [
                 random.choice(tile_set['wall_corner_sw']),
             ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('#', '+'), '?'),
                 (('#', '+'), '#', ('.', ' ', '0')),
                 ('?', ('.', ' ', '0'), '?')
             ),
             (
                 random.choice(tile_set['wall_corner_se']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('.', '0', ' '), '?'),
                 ('?', '#', ('.', '0', ' ')),
                 ('?', '#', '?')
             ),
             (
                 random.choice(tile_set['wall_corner_ne']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 ('?', '#', '#'),
                 ('?', '#', '?')
             ),
             (
                 random.choice(tile_set['wall_corner_nw']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '#', '?'),
                 (('.', '0'), '#', ('.', '0')),
                 ('?', ('.', '0'), '?')
             ),
             (
                 random.choice(tile_set['wall_end_s']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('.', '0'), '?'),
                 ('#', '#', ('.', '0')),
                 ('?', ('.', '0'), '?')
             ),
             (
                 random.choice(tile_set['wall_end_e']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 (('#', '+'), '#', '+'),
                 ('?', ('.', '0'), '?')
             ),
             [
                 random.choice(tile_set['doorway_hor_l']),
             ], replace=True)

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '?', '?'),
                 ('#', '+', '#'),
                 ('?', ('.', '0'), '?')
             ),
             (
                 random.choice(tile_set['doorway_hor_r']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', '#', '?'),
                 ('?', '+', ('.', '0')),
                 ('?', '#', '?')
             ),
             (
                 random.choice(tile_set['doorway_ver_b']),
             ))

    decorate(maze, fine_maze, maze_width, maze_height,
             (
                 ('?', ('#', '+'), '?'),
                 (('.', '0'), '#', ('.', '0')),
                 ('?', '+', '?')
             ),
             [
                 random.choice(tile_set['doorway_ver_t']),
             ], replace=True)


    return fine_maze


def decorate(maze, fine_maze, maze_width, maze_height, pattern, tiles_list, replace=False):
    locations = pattern_find(maze, -1, -1, maze_width + 1, maze_height + 1, pattern, 1, 1, 1, 1)
    if locations is not False:
        for location in locations:
            if replace:
                fine_maze[location[1]][location[0]] = tiles_list.copy()
            else:
                fine_maze[location[1]][location[0]].extend(tiles_list)


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


def traps_set(maze, attacks_table_point, db):
    traps_num = maze.width * maze.height * progression.scale_to_lvl(maze.trap_rate, maze.lvl) // 100
    room_rnd_list = [(rm, rm.rating) for rm in maze.rooms]
    trapped_rooms = pickrandom.items_get(room_rnd_list, items_number=traps_num)
    for trap_room in trapped_rooms:
        trap_params_list = dbrequests.trap_params_get(db.cursor, attacks_table_point, maze.lvl)
        if not trap_params_list:
            continue
        label, rang, dam_type, dam_val_base, dam_val_spread, lvl = random.choice(trap_params_list)
        x_sq = random.randrange(trap_room.left + 1, trap_room.right)
        y_sq = random.randrange(trap_room.top + 1, trap_room.bottom)
        no_place = False
        for ot in trap_room.traps:
            if ot.x_sq == x_sq and ot.y_sq == y_sq:
                no_place = True
        if no_place or x_sq is None or y_sq is None:
            x_sq = random.randrange(trap_room.left + 1, trap_room.right)
            y_sq = random.randrange(trap_room.top + 1, trap_room.bottom)
        new_trap = trap.Trap(x_sq, y_sq, maze.lvl, trap_room, label, rang, dam_type, dam_val_base, dam_val_spread, lvl)
        trap_room.traps.append(new_trap)
        trap_room.rating += 25
        maze.traps.append(new_trap)


def doors_set(maze, tile_set, db):
    # lock all rooms that are not corridors
    for locked_room in maze.rooms:
        if locked_room.corridor:
            for dr in locked_room.doors:
                if dr.lock is not None:
                    continue
                if random.randrange(1, 101) <= 50:
                    dr.shut = False
            continue
        if random.randrange(1, 101) <= maze.lock_rate:
            if random.randrange(1, 101) <= maze.magic_lock_rate:
                for dr in locked_room.doors:
                    if dr.lock is None:
                        dr.lock = lock.Lock(maze.lvl, magical=True)
                    dr.shut = True
                locked_room.rating += 150
                square(maze.array, locked_room.top + 1, locked_room.left + 1, locked_room.bottom, locked_room.right,
                       '0', '0', True)
            else:
                for dr in locked_room.doors:
                    if dr.lock is None:
                        dr.lock = lock.Lock(maze.lvl)
                    dr.shut = True
                locked_room.rating += 100
                square(maze.array, locked_room.top + 1, locked_room.left + 1, locked_room.bottom, locked_room.right,
                       '0', '0', True)
        if random.randrange(1, 101) <= progression.scale_to_lvl(maze.trap_rate, maze.lvl) and locked_room.doors:
            trap_params_list = dbrequests.trap_params_get(db.cursor, 'monster_attacks', maze.lvl)
            if not trap_params_list:
                continue
            label, rang, dam_type, dam_val_base, dam_val_spread, lvl = random.choice(trap_params_list)
            new_trap = trap.Trap(None, None, maze.lvl, locked_room, label, rang, dam_type, dam_val_base, dam_val_spread,
                                 lvl)
            random.choice(locked_room.doors).trap = new_trap
            maze.traps.append(new_trap)
            locked_room.rating += 50
    # create list of all doors
    for rm in maze.rooms:
        maze.doors.update(rm.doors)
    dr_remove = [dr for dr in maze.doors if dr.lock is None and not dr.shut and random.randrange(1, 101) < 81]
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
        mz_dr.image = mz_dr.image_update()


def exits_set(maze, exits_list):
    valid_rooms = [rm for rm in maze.rooms if not rm.locked]
    exit_rooms = random.sample(valid_rooms, len(exits_list))

    for i in range(0, len(exits_list)):
        dest = exits_list[i]
        room = exit_rooms[i]
        print(room.locked, 'lock room')
        x_sq = random.randrange(room.left + 1, room.right)
        y_sq = random.randrange(room.top + 1, room.bottom)
        new_exit = stairs.Stairs(x_sq, y_sq, -24, -24, dest, room, maze.tile_set['exit_up'])

        maze.exits.append(new_exit)


def array_pattern_apply(array, pattern, x, y):
    for i in range(0, len(pattern)):
        for j in range(0, len(pattern[i])):
            array[y + i][x + j] = pattern[i][j]


def populate(db, maze, animations):
    mon_ids = roll_monsters(db.cursor, maze.lvl, 0, maze.monster_types, maze.monster_type_amount)
    maze_monster_pool = [dbrequests.monster_get_by_id(db.cursor, mon_id) for mon_id in mon_ids]

    mob_populate_alg_1(maze, animations, maze_monster_pool, maze.monster_amount_rate)


def mob_populate_alg_1(maze, animations, maze_monster_pool, monster_amount_rate):
    for i in range(0, round(len(maze.rooms) * monster_amount_rate)):
        room = maze.rooms[random.randrange(0, len(maze.rooms))]
        mon_x_sq = random.randrange(room.left + 1, room.right)
        mon_y_sq = random.randrange(room.top + 1, room.bottom)

        for mon in maze.mobs:
            if mon.x_sq == mon_x_sq and mon.y_sq == mon_y_sq:
                break
        else:
            rnd_mob = maze_monster_pool[random.randrange(0, len(maze_monster_pool))]

            nmon = monster.Monster(mon_x_sq, mon_y_sq,
                                   animations.get_animation(rnd_mob['animation']), rnd_mob, state=0)
            maze.flag_array[round(mon_y_sq)][round(mon_x_sq)].mon = nmon
            maze.mobs.append(nmon)


def roll_monsters(db_cursor, max_level, max_grade, monster_types, mon_amount=1):
    rnd_roll = random.randrange(0, 10001)
    monster_ids = dbrequests.get_monsters(db_cursor, max_level, max_grade, monster_types, rnd_roll)
    monster_list = []
    for i in range(0, mon_amount):
        monster_list.append(monster_ids[random.randrange(0, len(monster_ids))])
    return monster_list


def flags_create(maze, array):
    flags_array = maze_array(maze.width, maze.height, 0)
    for i in range(0, maze.height):
        for j in range(0, maze.width):
            flags_array[i][j] = flagtile.FlagTile(
                None, None, None, None, [],
                (array[i][j] in ('.', '+')),
                (array[i][j] in ('.', '+')),
                False, False,
                (array[i][j] in ('.', '+'))
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
        fl.mov = True
        fl.obj = ex
        # fl.light = True
    for tr in maze.traps:
        if tr.x_sq is not None and tr.y_sq is not None:
            flags_array[tr.y_sq][tr.x_sq].trap = tr