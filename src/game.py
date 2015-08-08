#!/usr/bin/env python

import copy
import hx
import json
import math

CELL_EMPTY = ''
CELL_FILLED = 'F'
CELL_UNIT = 'U'

TURN = {'CW': hx.TURN_CW,
        'CCW': hx.TURN_CCW,
}

MOVE = {'W': hx.DIRECTION_W,
        'E': hx.DIRECTION_E,
        'SW': hx.DIRECTION_SW,
        'SE': hx.DIRECTION_SE,
}

MOVES = TURN.keys() + MOVE.keys()

MOVE_OK = 0
MOVE_LOCK = 1
MOVE_ERROR = 2

class Board(object):
    def __init__(self, width, height, filled=None):
        self.width = width
        self.height = height
        self.cells = []
        self.ceiling = width * [height]
        for row in range(height):
            self.cells.append(self.create_empty_row())
        if filled is not None:
            for col, row in filled:
                self._fill_cell(col, row)

    def _fill_cell(self, col, row):
        self.cells[row][col] = True
        self.ceiling[col] = min(self.ceiling[col], row)

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
        for col in range(self.width):
            # self.ceiling[col] can't be greater than row since the row should be
            # filled in order to be cleared.
            if self.ceiling[col] < row:
                self.ceiling[col] += 1
            elif self.ceiling[col] == row:
                self.ceiling[col] = self.height
                for r in range(row, self.height):
                    if self.filled_cell(col, r):
                        self.ceiling[col] = r

    def lock(self, cells):
        for c in cells:
            col, row = c
            self._fill_cell(col, row)

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
    def __init__(self, pivot, members, radius=None):
        self.pivot = pivot
        self.members = members
        if radius is None:
            self.radius = max([hx.offset_distance(pivot, member) for member in members])
        else:
            self.radius = radius

    def __contains__(self, cell):
        return cell in self.members

    def __eq__(self, other):
        return self.footprint == other.footprint

    def __ne__(self, other):
        return self.footprint != other.footprint

    def __hash__(self):
        return hash(self.footprint)

    def to_position(self, cell, rotation=0):
        vector = hx.offset_vector(self.pivot, cell)
        members = [hx.offset_translate(member, vector) for member in self.members]
        unit = Unit(cell, members, self.radius)
        if rotation > 0:
            unit = unit.rotate(hx.TURN_CW, rotation)
        elif rotation < 0:
            unit = unit.rotate(hx.TURN_CCW, -rotation)
        return unit

    def to_spawn(self, board_width):
        # Move vertically
        col, row = self.pivot
        spawn_row = row - self.north_border
        unit = self.to_position((col, spawn_row))
        # Move horizontally
        west_border = unit.west_border
        width = unit.east_border - west_border + 1
        spawn_border_col = (board_width - width) / 2
        col, row = unit.pivot
        spawn_col = col + spawn_border_col - west_border
        return unit.to_position((spawn_col, row))

    def move(self, direction):
        pivot = hx.offset_move(self.pivot, direction)
        members = [hx.offset_move(member, direction) for member in self.members]
        return Unit(pivot, members, self.radius)

    def rotate(self, direction, steps=1):
        members = self.members
        for step in range(steps):
            members = [hx.offset_rotate(self.pivot, member, direction) for member in members]
        return Unit(self.pivot, members, self.radius)

    def action(self, direction_str):
        if direction_str in TURN:
            return self.rotate(TURN[direction_str])
        else:
            return self.move(MOVE[direction_str])

    def move_to_reach(self, other):
        for move in MOVES:
            unit = self.action(move)
            if unit == other:
                return move
        return None

    @property
    def footprint(self):
        return tuple(sorted(self.members))

    @property
    def west_border(self):
        return min([col for col, row in self.members])

    @property
    def east_border(self):
        return max([col for col, row in self.members])

    @property
    def north_border(self):
        return min([row for col, row in self.members])

    @property
    def south_border(self):
        return max([row for col, row in self.members])

    @property
    def reach(self):
        """
        Return a new Unit which contains all cells that can be touched by executing
        moves on this unit.
        """
        touched = set()
        for move in MOVES:
            unit = self.action(move)
            touched.update(set(unit.members))
        return Unit(self.pivot, list(touched))

def lcg(seed):
    modulus = 2**32
    multiplier = 1103515245
    increment = 12345
    curr = seed
    while True:
        new = (multiplier * curr + increment) % modulus
        yield ((curr >> 16) & 0x7fff, curr)
        curr = new

class Game(object):
    def __init__(self, board, units, max_units, seed, unit=None):
        self.board = board
        self.units = units
        self.max_units = max_units
        self.num_units = 0
        self.curr_seed = seed
        self.rnd = lcg(seed)
        self.ls_old = 0
        self.score = 0
        if unit:
            self.unit = unit
        else:
            self.next_unit()

    def clone(self):
        board = copy.deepcopy(self.board)
        units = copy.deepcopy(self.units)
        unit = copy.deepcopy(self.unit)
        game = Game(board, units, self.max_units - self.num_units, self.curr_seed, unit=unit)
        game.footprints = copy.deepcopy(self.footprints)
        game.score = self.score
        game.ls_old = self.ls_old
        return game

    def next_unit(self):
        if self.num_units == self.max_units:
            self.unit = None
            return
        rand, self.curr_seed = self.rnd.next()
        self.curr_unit = rand % len(self.units)
        unit = self.units[self.curr_unit].to_spawn(self.board.width)
        if self.is_unit_valid(unit):
            self.unit = unit
            self.footprints = set([self.unit.footprint])
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

    def move_result(self, direction):
        unit = self.unit.action(direction)
        if unit.footprint in self.footprints:
            return MOVE_ERROR
        elif self.is_unit_valid(unit):
            return MOVE_OK
        else:
            return MOVE_LOCK

    def moves(self):
        results = {MOVE_OK: [],
                   MOVE_LOCK: [],
                   MOVE_ERROR: [],
        }
        for move in MOVES:
            results[self.move_result(move)].append(move)
        return results

    def move_unit(self, direction):
        if self.unit is None:
            return
        unit = self.unit.action(direction)
        if unit.footprint in self.footprints:
            raise ValueError('Illegal move: ' + direction)
        if self.is_unit_valid(unit):
            self.unit = unit
            self.footprints.add(unit.footprint)
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
