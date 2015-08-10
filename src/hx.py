#!/usr/bin/env python

import collections
import math

class CHex(object):
#    __slots__ = ['x', 'y', 'z']
    __hash__ = None

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.x != 0 or self.y != 0 or self.z != 0

    def __len__(self):
        return 3

    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y, self.z]
        l[key] = value
        self.x, self.y, self.z = l

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y, self.z)['xyz'.index(c)] for c in name])
        except ValueError:
            raise AttributeError, name

USE_NAMEDTUPLE = False
if USE_NAMEDTUPLE:
    Hex = collections.namedtuple('Hex', ['x', 'y', 'z'])
else:
    Hex = CHex

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

def rotate(pivot, h, direction):
    vect = hex_sub(h, pivot)
    if direction == TURN_CW:
        return hex_add(pivot, Hex(-vect.z, -vect.x, -vect.y))
    else:
        return hex_add(pivot, Hex(-vect.y, -vect.z, -vect.x))

def _normalize(vect):
    if vect.x == 0 and vect.y == 0 and vect.z == 0:
        return vect
    length = math.sqrt(vect.x ** 2 + vect.y ** 2 + vect.z ** 2)
    return Hex(vect.x / length, vect.y / length, vect.z / length)

def abs_rotation_distance(v0, v1):
    n0 = _normalize(v0)
    n1 = _normalize(v1)
    s = n0.x * n1.x + n0.y * n1.y + n0.z * n1.z
    if s > 0.8:
        return 0
    elif s > 0.0:
        return 1
    elif s > -0.8:
        return 2
    else:
        return 3

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
    return to_offset(hex_add(h, direction))

def offset_rotate(pivot, cell, direction):
    hp = to_hex(*pivot)
    h = to_hex(*cell)
    return to_offset(rotate(hp, h, direction))

def offset_rotate_list(pivot, cells, direction):
    hp = to_hex(*pivot)
    return [to_offset(rotate(hp, to_hex(*cell), direction)) for cell in cells]

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
