#!/usr/bin/env python

import collections

Hex = collections.namedtuple('Hex', ['x', 'y', 'z'])

DIRECTION_E = Hex(1, -1, 0)
DIRECTION_W = Hex(-1, 1, 0)
DIRECTION_SE = Hex(0, -1, 1)
DIRECTION_SW = Hex(-1, 0, 1)
DIRECTION_NE = Hex(1, 0, -1)
DIRECTION_NW = Hex(0, 1, -1)

DIRECTIONS = (DIRECTION_E,
              DIRECTION_SE,
              DIRECTION_SW,
              DIRECTION_W,
              DIRECTION_NW,
              DIRECTION_NE,
)

TURN_CW = 0
TURN_CCW = 1

def hex_add(a, b):
    return Hex(a.x + b.x, a.y + b.y, a.z + b.z)

def hex_sub(a, b):
    return Hex(a.x - b.x, a.y - b.y, a.z - b.z)

def hex_scale(scale, h):
    return Hex(scale * h.x, scale * h.y, scale * h.z)

def distance(h0, h1):
    return (abs(h1.x - h0.x) + abs(h1.y - h0.y) + abs(h1.z - h0.z)) / 2

def move(h, direction):
    return hex_add(h, direction)

def rotate(pivot, h, direction):
    vect = hex_sub(h, pivot)
    if direction == TURN_CW:
        return hex_add(pivot, Hex(-vect.z, -vect.x, -vect.y))
    else:
        return hex_add(pivot, Hex(-vect.y, -vect.z, -vect.x))

def circle(center, radius):
    members = []
    h = hex_add(center, hex_scale(radius, DIRECTION_NW))
    for direction in DIRECTIONS:
        for step in range(radius):
            members.append(h)
            h = hex_add(h, direction)
    return members

def offset_distance(c0, c1):
    return distance(to_hex(*c0), to_hex(*c1))

def offset_move(cell, direction):
    h = to_hex(*cell)
    return to_offset(move(h, direction))

def offset_rotate(pivot, cell, direction):
    hp = to_hex(*pivot)
    h = to_hex(*cell)
    return to_offset(rotate(hp, h, direction))

def offset_translate(origin, vector):
    h = to_hex(*origin)
    return to_offset(hex_add(h, vector))

def offset_vector(c0, c1):
    h0 = to_hex(*c0)
    h1 = to_hex(*c1)
    return hex_sub(h1, h0)

def offset_circle(center, radius):
    hc = circle(to_hex(*center), radius)
    return [to_offset(h) for h in hc]

def to_offset(h):
    col = h.x + (h.z - (h.z % 2)) / 2
    row = h.z
    return (col, row)

def to_hex(col, row):
    x = col - (row - (row % 2)) / 2
    z = row
    y = -x-z
    return Hex(x, y, z)
