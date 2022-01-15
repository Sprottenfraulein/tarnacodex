# mathematical functions
import math


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