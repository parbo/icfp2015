#!/usr/bin/env python

import collections

Hex = collections.namedtuple('Hex', ['x', 'y', 'z'])

DIRECTION_E = Hex(1, -1, 0)
DIRECTION_W = Hex(-1, 1, 0)
DIRECTION_SE = Hex(0, -1, 1)
DIRECTION_SW = Hex(-1, 0, 1)

TURN_CW = 0
TURN_CCW = 1

def hex_add(a, b):
    return Hex(a.x + b.x, a.y + b.y, a.z + b.z)

def hex_sub(a, b):
    return Hex(a.x - b.x, a.y - b.y, a.z - b.z)

def move(h, direction):
    return hex_add(h, direction)

def rotate(pivot, h, direction):
    vect = hex_sub(h, pivot)
    if direction == TURN_CW:
        return hex_add(pivot, Hex(-vect.z, -vect.x, -vect.y))
    else:
        return hex_add(pivot, Hex(-vect.y, -vect.z, -vect.x))

def offset_move(cell, direction):
    h = to_hex(*cell)
    return to_offset(move(h, direction))

def offset_rotate(pivot, cell, direction):
    hp = to_hex(*pivot)
    h = to_hex(*cell)
    return to_offset(rotate(hp, h, direction))

def to_offset(h):
    col = h.x + (h.z - (h.z % 2)) / 2
    row = h.z
    return (col, row)

def to_hex(col, row):
    x = col - (row - (row % 2)) / 2
    z = row
    y = -x-z
    return Hex(x, y, z)
