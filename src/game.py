#!/usr/bin/env python

import hx
import json

CELL_EMPTY = ''
CELL_FILLED = 'F'
CELL_UNIT = 'U'

class Board(object):
    def __init__(self, width, height, filled=None):
        self.width = width
        self.height = height
        self.cells = []
        for row in range(height):
            self.cells.append(self.create_empty_row())
        if filled is not None:
            for col, row in filled:
                self.cells[row][col] = True

    def __str__(self):
        filled = []
        for row in range(self.height):
            for col in range(self.width):
                if self.filled_cell(col, row):
                    filled.append((col, row))
        return 'Board(%d, %d, %s)' % (self.width, self.height, filled)

    def view(self):
        rows = []
        for row in range(self.height):
            padding = '' if row % 2 == 0 else ' '
            rows.append(padding + ' '.join(['%d' % c for c in self.cells[row]]))
        return '\n'.join(rows)

    def filled_cell(self, col, row):
        return self.cells[row][col]

    def filled_hex(self, h):
        col, row = hx.to_offset(h)
        return self.filled_cell(col, row)

    def filled_row(self, row):
        return all(self.cells[row])

    def clear_row(self, row):
        for row in range(row, 0, -1):
            self.cells[row] = self.cells[row - 1]
        self.cells[0] = self.create_empty_row()

    def lock(self, cells):
        for c in cells:
            col, row = c
            self.cells[row][col] = True

    def position(self, origin, direction):
        """
        Calculates a new position given a current position and the direction of movement.
        Raises LookupError if the new position is invalid.
        """
        col, row = hx.offset_move(origin, direction)
        if (0 < col < self.width) and (0 < row < self.height):
            return (col, row)
        raise LookupError('Invalid position: (%d, %d)' % (col, row))

    def create_empty_row(self):
        return self.width * [False]

class Unit(object):
    def __init__(self, pivot, members):
        self.pivot = pivot
        self.members = members

    def __contains__(self, cell):
        return cell in self.members

    def move(self, direction):
        pivot = hx.offset_move(self.pivot, direction)
        members = [hx.offset_move(member, direction) for member in self.members]
        return Unit(pivot, members)

    def rotate(self, direction):
        members = [hx.offset_rotate(self.pivot, member, direction) for member in self.members]
        return Unit(self.pivot, members)

def lcg(seed):
    modulus = 2**32
    multiplier = 1103515245
    increment = 12345
    curr = seed
    while True:
        new = (multiplier * curr + increment) % modulus
        yield (curr >> 16) & 0x7fff
        curr = new

class Game(object):
    def __init__(self, board, units, max_units, seed):
        self.board = board
        self.units = units
        self.max_units = max_units
        self.num_units = 0
        self.rnd = lcg(seed)
        self.ls_old = 0
        self.score = 0
        self.next_unit()

    def next_unit(self):
        if self.num_units == self.max_units:
            self.unit = None
            return
        self.curr_unit = self.rnd.next() % len(self.units)
        unit = self.units[self.curr_unit]
        # Center unit (TODO: move this code to unit)
        left_most = None
        right_most = None
        top = None
        for m in unit.members:
            x, y = m
            if left_most is None or x < left_most:
                left_most = x
            if right_most is None or x > right_most:
                right_most = x
            if top is None or y < top:
                top = y
        w = right_most - left_most + 1
        start = (self.board.width - w) / 2
        for i in range(left_most, start):
            unit = unit.move(hx.DIRECTION_E)
        # Now it should be centered
        if self.is_unit_valid(unit):
            self.unit = unit
            self.num_units += 1
        else:
            self.unit = None

    def is_unit_valid(self, unit):
        return all((self.is_valid_pos(p) for p in unit.members))

    def cell(self, col, row):
        if self.unit is not None:
            if (col, row) in self.unit:
                return CELL_UNIT
        if self.board.filled_cell(col, row):
            return CELL_FILLED
        else:
            return CELL_EMPTY

    @property
    def size(self):
        return (self.board.width, self.board.height)

    def is_valid_pos(self, pos):
        x, y = pos
        if x < 0:
            return False
        elif x >= self.board.width:
            return False
        if y < 0:
            return False
        elif y >= self.board.height:
            return False
        elif self.board.filled_cell(x, y):
            return False
        return True

    def move_unit(self, direction):
        if self.unit is None:
            return
        unit = self.unit.move(direction)
        if self.is_unit_valid(unit):
            self.unit = unit
        else:
            self.board.lock(self.unit.members)
            ls = 0
            row = self.board.height - 1
            while row > 0:
                if self.board.filled_row(row):
                    ls += 1
                    self.board.clear_row(row)
                else:
                    row -= 1
            points = len(self.unit.members) + 100 * (1 + ls) * ls / 2
            line_bonus = 0
            if self.ls_old > 1:
                line_bonus = math.floor((self.ls_old - 1) * points / 10)
            self.ls_old = ls
            self.score = self.score + points + line_bonus
            self.next_unit()

def jc2t(coord):
    """Convert a json coordinate to a (x, y) tuple."""
    return (coord["x"], coord["y"])

class Problem(object):
    def __init__(self, problem):
        self.id = problem["id"]
        self.height = problem["height"]
        self.width = problem["width"]
        self.source_seeds = problem["sourceSeeds"]
        self.source_length = problem["sourceLength"]
        self.units = [Unit(jc2t(u["pivot"]), [jc2t(m) for m in u["members"]]) for u in problem["units"]]
        self.filled = [jc2t(f) for f in problem["filled"]]

    def make_game(self, seed_index):
        return Game(Board(self.width, self.height, self.filled), self.units, self.source_length, self.source_seeds[seed_index])

    @staticmethod
    def load(filename):
        with open(filename) as pf:
            return Problem(json.load(pf))

if __name__ == '__main__':
    board = Board(10, 10, [(1, 1)])
    print board
    print board.view()
