from library import maths
import random


def fill2d(array2d, stop_list, orig_xy, xy, max_spaces, max_dist, xy_stop_list=None, r=None, r_max=20):
    if xy_stop_list is None:
        xy_stop_list = [xy]
        r = 1
    spaces_list = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    random.shuffle(spaces_list)
    adjust_free = []
    for tile_x, tile_y in spaces_list:
        abs_x, abs_y = xy[0] + tile_x, xy[1] + tile_y
        """if (abs_x, abs_y) in xy_stop_list:
            continue"""
        if abs_x < 0 or abs_y < 0 or abs_x >= len(array2d[0]) or abs_y >= len(array2d):
            continue
        if maths.get_distance(orig_xy[0], orig_xy[1], abs_x, abs_y) >= max_dist:
            continue

        if len(xy_stop_list) >= max_spaces:
            return xy_stop_list
        xy_stop = False
        for flag_name, flag_value in stop_list.items():
            if getattr(array2d[abs_y][abs_x], flag_name) == flag_value:
                xy_stop = True
        if xy_stop:
            continue
        xy_stop_list.append((abs_x, abs_y))
        adjust_free.append((abs_x, abs_y))
    for tile_x, tile_y in adjust_free:
        if r < r_max and len(xy_stop_list) < max_spaces:
            abs_x, abs_y = xy[0] + tile_x, xy[1] + tile_y
            fill2d(array2d, stop_list, orig_xy, (abs_x, abs_y), max_spaces, max_dist, xy_stop_list, r + 1, r_max)
    return xy_stop_list


def path2d(array2d, stop_list, xy, dest_xy, max_spaces, max_dist, parent_index=0, xy_sq_list=None, xy_ind_list=None, r=None, r_max=20):
    goal = False
    if xy_sq_list is None:
        xy_sq_list = [xy]
        xy_ind_list = [0]
        r = 1
    spaces_list = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    spaces_list.sort(key=lambda x: (abs(dest_xy[0] - (xy[0] + x[0])) + abs(dest_xy[1] - (xy[1] + x[1]))))
    spaces_list = spaces_list[:4]
    # random.shuffle(spaces_list)
    if xy == dest_xy:
        return True, xy_sq_list, xy_ind_list
    for tile_x, tile_y in spaces_list:
        if goal:
            break
        abs_x, abs_y = xy[0] + tile_x, xy[1] + tile_y
        if (abs_x, abs_y) in xy_sq_list:
            continue
        if abs_x < 0 or abs_y < 0 or abs_x >= len(array2d[0]) or abs_y >= len(array2d):
            continue
        if len(xy_sq_list) >= max_spaces:
            return False, xy_sq_list, xy_ind_list
        xy_stop = False
        for flag_name, flag_value in stop_list.items():
            if getattr(array2d[abs_y][abs_x], flag_name) is flag_value:
                xy_stop = True
        if xy_stop:
            continue
        else:
            if abs_x == dest_xy[0] and abs_y == dest_xy[1]:
                return True, xy_sq_list, xy_ind_list
            xy_sq_list.append((abs_x, abs_y))
            xy_ind_list.append(parent_index)
            if r < r_max:
                abs_x, abs_y = xy[0] + tile_x, xy[1] + tile_y
                goal, sq_list, ind_list = path2d(array2d, stop_list, (abs_x, abs_y), dest_xy, max_spaces, max_dist,
                       parent_index=len(xy_ind_list) - 1, xy_sq_list=xy_sq_list, xy_ind_list=xy_ind_list, r=r+1, r_max=r_max)
    return goal, xy_sq_list, xy_ind_list


def calc_vision_rays(flag_array, x, y, max_distance, vision_prev, dark=True):
    visible_list = []
    for angle in range(0, 70):
        rads = angle * 0.09
        x2, y2 = maths.rads_dist_to_xy(x, y, rads, max_distance)

        visible_list.extend(cast_ray(flag_array, x, y, x2, y2))

    for sq in visible_list:
        try:
            flag_array[sq[1]][sq[0]].vis = True
        except IndexError:
            pass

    if dark and vision_prev is not None:
        darkening_list = [d_sq for d_sq in vision_prev if d_sq not in visible_list]
        for d_sq_x, d_sq_y in darkening_list:
            try:
                flag_array[d_sq_y][d_sq_x].vis = False
            except IndexError:
                pass
    return visible_list


def cast_ray(flag_array, x1, y1, x2, y2, sightonly=False):
    dist_x = x2 - x1
    dist_y = y2 - y1
    if abs(dist_x) >= abs(dist_y):
        if dist_x != 0:
            step_y = abs(dist_y / dist_x) * maths.sign(dist_y)
        else:
            step_y = 0
        step_x = maths.sign(dist_x)
    else:
        step_y = maths.sign(dist_y)
        if dist_y != 0:
            step_x = abs(dist_x / dist_y) * maths.sign(dist_x)
        else:
            step_x = 0
    temp_x = x1
    temp_y = y1
    if sightonly:
        hit = False
        while not hit and (abs(temp_x - x2) >= 1 or abs(temp_y - y2) >= 1):
            # self.part_gen(round(temp_x), round(temp_y), 'hit', 8, 2)
            if not flag_array[round(temp_y)][round(temp_x)].light:
                hit = True
            # test ray calculation
            temp_x += step_x / 2
            temp_y += step_y / 2

        if hit:
            return False
        else:
            return True
    else:
        squares = []
        hit = False
        while not hit and (abs(temp_x - x2) >= 1 or abs(temp_y - y2) >= 1):
            if not flag_array[round(temp_y)][round(temp_x)].light:
                hit = True
            squares.append((round(temp_x), round(temp_y)))
            # test ray calculation
            temp_x += step_x
            temp_y += step_y
        return squares
