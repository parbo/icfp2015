#!/usr/bin/env python

import math

DIRECTION_E = 0
DIRECTION_W = 1
DIRECTION_SE = 2
DIRECTION_SW = 3

TURN_CW = 0
TURN_CCW = 1

TURN_ANGLE = math.pi / 3.0

SIN_60 = math.sin(TURN_ANGLE)
COS_60 = math.cos(TURN_ANGLE)

def move(origin, direction):
    """ Calculates a new position given a current position and the direction of movement. """
    current_col, current_row = origin
    if direction == DIRECTION_E:
        dx = 1
        dy = 0
    elif direction == DIRECTION_W:
        dx = -1
        dy = 0
    elif direction == DIRECTION_SE:
        dx = 0 if current_row % 2 == 0 else 1
        dy = 1
    elif direction == DIRECTION_SW:
        dx = -1 if current_row % 2 == 0 else 0
        dy = 1
    new_col = current_col + dx
    new_row = current_row + dy
    return (new_col, new_row)

def to_real(col, row):
    x = col + 0.5 * (row % 2)
    y = float(row)
    return (x, y)

def to_int(x, y):
    row = int_coord(y)
    col = int_coord(x - 0.5 * (row % 2))
    return (col, row)

def int_coord(real_coord):
    return int(round(real_coord))

def distance(col0, row0, col1, row1):
    x0, y0 = to_real(col0, row0)
    x1, y1 = to_real(col1, row1)
    return (x1 - x0, y1 - y0)

def translate(col, row, dx, dy):
    x0, y0 = to_real(col, row)
    x1 = x0 + dx
    y1 = y0 + dy
    return to_int(x1, y1)

def rotate(pivot, col, row, direction):
    px, py = pivot
    x0, y0 = to_real(col, row)
    vx = x0 - px
    vy = y0 - py
    if direction == TURN_CW:
        x1 = px + vx * COS_60 - vy * SIN_60
        y1 = py + vx * SIN_60 + vy * COS_60
    else:
        x1 = px + vx * COS_60 + vy * SIN_60
        y1 = py - vx * SIN_60 + vy * COS_60
    return to_int(x1, y1)

if __name__ == '__main__':
    print rotate((1, 3), 4, 4, TURN_CCW)
