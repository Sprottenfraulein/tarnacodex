# Maze builder.
import random


def maze_array(width, height, byte_def=' '):
    new_maze = []
    for i in range(0, height):
        new_maze.append([byte_def] * width)
    return new_maze


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
            room_list.append(Room(top, left, bottom, right - min_width))
            room_list.append(Room(top, right - min_width, bottom, right))
        else:
            room_list.append(Room(top, left, bottom, right))
    else:
        if height > min_height * 2:
            rnd_slice = random.randrange(min_height, height - min_height + 1)
            room_list.extend(
                split_build(top, left, top + rnd_slice, right, min_width, min_height, vertical, r_limit - 1))
            room_list.extend(
                split_build(top + rnd_slice, left, bottom, right, min_width, min_height, vertical, r_limit - 1))
        elif height == min_height * 2:
            room_list.append(Room(top, left, bottom - min_height, right))
            room_list.append(Room(bottom - min_height, left, bottom, right))
        else:
            room_list.append(Room(top, left, bottom, right))
    return room_list


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


def rooms_attached(maze, rooms, rm, v_merge=1, h_merge=1, corr_width=2):
    for ar in rooms:
        if rm == ar or ar in rm.adj_rooms:
            continue

        corridor = False
        attached = False
        if rm.top == ar.bottom and rm.left < ar.right - h_merge and rm.right > ar.left + h_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.left + 1, ar.left + 1),
                                            min(rm.right, ar.right), 0, corr_width, 'd', ' ')
        elif rm.left == ar.right and rm.top < ar.bottom - v_merge and rm.bottom > ar.top + v_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.top + 1, ar.top + 1),
                                            min(rm.bottom, ar.bottom), 3, corr_width, 'd', ' ')
        elif rm.bottom == ar.top and rm.left < ar.right - h_merge and rm.right > ar.left + h_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.left + 1, ar.left + 1),
                                            min(rm.right, ar.right), 2, corr_width, 'd', ' ')
        elif rm.right == ar.left and rm.top < ar.bottom - v_merge and rm.bottom > ar.top + v_merge:
            corridor, attached = rooms_join(maze, rm, ar, max(rm.top + 1, ar.top + 1),
                                            min(rm.bottom, ar.bottom), 1, corr_width, 'd', ' ')

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
                maze[room1.top][i] = corr_byte
            elif align == 1:
                maze[i][room1.right] = corr_byte
            elif align == 2:
                maze[room1.bottom][i] = corr_byte
            elif align == 3:
                maze[i][room1.left] = corr_byte
        corridor = True
        attached = True
    # elif len(room1.doors) + len(room2.doors) < 3:
    # elif len(room2.doors) == 0 or (len(room1.doors) < 3 and len(room2.doors) < 3):
    elif len(room1.doors) < 3 and len(room2.doors) < 3:
        # else:
        i = random.randrange(ap + 1, bp)
        if align == 0:
            maze[room1.top][i] = door_byte
            new_door = (i, room1.top)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 1:
            maze[i][room1.right] = door_byte
            new_door = (room1.right, i)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 2:
            maze[room1.bottom][i] = door_byte
            new_door = (i, room1.bottom)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        elif align == 3:
            maze[i][room1.left] = door_byte
            new_door = (room1.left, i)
            room1.doors.append(new_door)
            room2.doors.append(new_door)
        attached = True
    return corridor, attached


class Room:
    def __init__(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        # self.rating = 100
        self.adj_rooms = []
        self.doors = []
        # self.traps = []
        self.corridor = False
