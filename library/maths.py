# mathematical functions
import math, random


def exponential(ratio, value, multiplier):
    return round(ratio ** value * multiplier)


def sign(x):
    return (x > 0) - (x < 0)


def rads_dist_to_xy(x, y, rads, distance):
    xx = x + (distance * math.cos(rads))
    yy = y + (distance * math.sin(rads))
    return xx, yy


def xy_dist_to_rads(x1, y1, x2, y2):
    rad = math.atan2(y2 - y1, x2 - x1)
    return rad


def get_distance(x1, y1, x2, y2):
    dist = int(round(math.sqrt((abs(x2 - x1)) ** 2 + (
            abs(y2 - y1)) ** 2)))
    return dist


def rect_in_bounds(rect_x, rect_y, rect_width, rect_height, space_x, space_y, space_width, space_height):
    if rect_x < space_x:
        rect_x = space_x
    elif rect_x + rect_width > space_x + space_width:
        rect_x = space_x + space_width - rect_width
    if rect_y < space_y:
        rect_y = space_y
    elif rect_y + rect_height > space_y + space_height:
        rect_y = space_y + space_height - rect_height
    return rect_x, rect_y


def rect_to_center(rect_x, rect_y, rect_width, rect_height, space_x, space_y, space_width, space_height):
    if rect_x > space_x + space_width // 2:
        rect_x = rect_x - rect_width
    if rect_y > space_y + space_height // 2:
        rect_y = rect_y - rect_height
    return rect_x, rect_y


def expo_rnd_sample(minimum=1, maximum=1000, expolambda=0.004):
    r = int(random.expovariate(expolambda))
    if minimum <= r <= maximum:
        return r
    return


def get_rnd_expo_list(range_min, range_max, n):
    sample_list = [expo_rnd_sample() for i in range(0, n)]
    filtered = list(filter(lambda x: x is not None, sample_list))
    spread = range_max - range_min
    result_list = [i * spread // 1000 + range_min for i in filtered]
    return result_list
