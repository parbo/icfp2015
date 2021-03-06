#!/usr/bin/env python

import copy
import hx
import json
import math

CELL_EMPTY = ''
CELL_FILLED = 'F'
CELL_UNIT = 'U'

CMD_E = 0
CMD_W = 1
CMD_SE = 2
CMD_SW = 3
CMD_NE = 4
CMD_NW = 5
CMD_CW = 6
CMD_CCW = 7

CMDS = (
    CMD_E,
    CMD_W,
    CMD_SE,
    CMD_SW,
    CMD_CW,
    CMD_CCW
)

OPPOSITE = {
    CMD_E: CMD_W,
    CMD_W: CMD_E,
    CMD_SE: CMD_NW,
    CMD_SW: CMD_NE,
    CMD_NE: CMD_SW,
    CMD_NW: CMD_SE,
    CMD_CW: CMD_CCW,
    CMD_CCW: CMD_CW
}

TURN = {CMD_CW: hx.TURN_CW,
        CMD_CCW: hx.TURN_CCW,
}

MOVE = {CMD_W: hx.DIRECTION_W,
        CMD_E: hx.DIRECTION_E,
        CMD_SW: hx.DIRECTION_SW,
        CMD_SE: hx.DIRECTION_SE,
        CMD_NW: hx.DIRECTION_NW,
        CMD_NE: hx.DIRECTION_NE,
}

MOVES = CMDS

MOVE_OK = 0
MOVE_LOCK = 1
MOVE_ERROR = 2

class CircleCache(object):
    def __init__(self):
        self._cache = {}

    def get(self, center, radius):
        try:
            return self._cache[(center, radius)]
        except KeyError as e:
            circle = hx.offset_circle(center, radius)
            self._cache[(center, radius)] = circle
            return circle

CIRCLES = CircleCache()

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

    @property
    def filled_cells(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.filled_cell(col, row):
                    yield (col, row)

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

    def close_to_cell(self, cell, distance):
        cells = [cell]
        for radius in range(1, distance + 1):
            cells.extend(CIRCLES.get(cell, radius))
        return cells

    def close_to_filled(self, distance, include_filled=True):
        cells = set()
        filled = set(self.filled_cells)
        for cell in filled:
            cells.update(set(self.close_to_cell(cell, distance)))
        if include_filled:
            return cells
        else:
            return cells - filled

    def is_within_board(self, cell):
        col, row = cell
        return (0 <= col < self.width) and (0 <= row < self.height)

    def reachable_cells(self, from_cell, distance):
        reached = set([])
        q = [from_cell]
        c2f = self.close_to_filled(distance)
        while q:
            cell = q.pop()
            reached.add(cell)
            neighbors = hx.offset_circle(cell, 1)
            for n in neighbors:
                if not self.is_within_board(n):
                    continue
                if n in c2f:
                    continue
                if n in reached:
                    continue
                q.append(n)
        return reached

class BoardWithUnit(object):
    def __init__(self, board, unit):
        self.board = board
        self.unit = unit

    def filled_cell(self, col, row):
        if self.board.filled_cell(col, row):
            return True
        return (col, row) in self.unit.members

    def filled_row(self, row):
        for col in range(self.board.width):
            if not self.filled_cell(col, row):
                return False
        return True

    @property
    def ceiling(self):
        w = self.board.width
        unit_ceiling = w * [self.board.height]
        for col, row in self.unit.members:
            unit_ceiling[col] = min(unit_ceiling[col], row)
        return [min(unit_ceiling[col], self.board.ceiling[col]) for col in range(w)]

class Unit(object):
    unit_cache = {}
    action_cache = {}

    @staticmethod
    def make_footprint(pivot, members):
        return tuple(sorted(members) + [pivot])

    @staticmethod
    def get_or_create_unit(pivot, members):
        footprint = Unit.make_footprint(pivot, members)
        try:
            return Unit.unit_cache[footprint]
        except KeyError:
            pass
        unit = Unit(pivot, members, footprint)
        Unit.unit_cache[footprint] = unit
        return unit

    def __init__(self, pivot, members, footprint):
        self.pivot = pivot
        self.members = members
        self.footprint = footprint
        self.hash = None

    def __contains__(self, cell):
        return cell in self.members

    # def __eq__(self, other):
    #     return id(self) == id(other)

    # def __ne__(self, other):
    #     return not self.__eq__(other)

    # def __hash__(self):
    #     if self.hash is None:
    #         self.hash = hash(self.footprint)
    #     return self.hash

    def __str__(self):
        return "(%s, %s)"%(self.pivot, self.members)

    def to_position(self, cell, rotation=0):
        vector = hx.offset_vector(self.pivot, cell)
        members = [hx.offset_translate(member, vector) for member in self.members]
        unit = Unit.get_or_create_unit(cell, members)
        if rotation > 0:
            unit = unit.rotate(hx.TURN_CW, rotation)
        elif rotation < 0:
            unit = unit.rotate(hx.TURN_CCW, -rotation)
        return unit

    def to_position_nw(self, cell, rotation=0):
        vector = hx.offset_vector(self.nw_corner, cell)
        pivot = hx.offset_translate(self.pivot, vector)
        members = [hx.offset_translate(member, vector) for member in self.members]
        unit = Unit.get_or_create_unit(pivot, members)
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
        return Unit.get_or_create_unit(pivot, members)

    def rotate(self, direction, steps=1):
        members = self.members
        for step in range(steps):
            members = hx.offset_rotate_list(self.pivot, members, direction)
        return Unit.get_or_create_unit(self.pivot, members)

    def action(self, cmd):
        try:
            return Unit.action_cache[(self, cmd)]
        except KeyError:
            pass
        if cmd < CMD_CW:
            unit = self.move(MOVE[cmd])
        else:
            unit = self.rotate(TURN[cmd])
        Unit.action_cache[(self, cmd)] = unit
        return unit

    def move_to_reach(self, other, moves):
        for move in moves:
            unit = self.action(move)
            if unit == other:
                return move
        return None

    def abs_rotation_distance(self, other):
        v0 = hx.offset_vector(self.pivot, self.members[0])
        v1 = hx.offset_vector(other.pivot, other.members[0])
        return hx.abs_rotation_distance(v0, v1)

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
    def nw_corner(self):
        return (self.west_border, self.north_border)

    # @property
    # def reach(self):
    #     """
    #     Return a new Unit which contains all cells that can be touched by executing
    #     moves on this unit.
    #     """
    #     touched = set()
    #     for move in MOVES:
    #         unit = self.action(move)
    #         touched.update(set(unit.members))
    #     return Unit.get_or_create_unit(self.pivot, list(touched))

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
        b = self.board
        return 0 <= x < b.width and 0 <= y < b.height and not b.filled_cell(x, y)

    def move_unit_result(self, unit, direction):
        unit = unit.action(direction)
        if unit.footprint in self.footprints:
            return MOVE_ERROR
        elif self.is_unit_valid(unit):
            return MOVE_OK
        else:
            return MOVE_LOCK

    def moves_unit(self, unit, moves):
         results = {MOVE_OK: [],
                    MOVE_LOCK: [],
                    MOVE_ERROR: [],
         }
         for move in moves:
             results[self.move_unit_result(unit, move)].append(move)
         return results

    def move_unit_result_wu(self, unit, direction, footprints):
        unit = unit.action(direction)
        if unit.footprint in footprints:
            return (MOVE_ERROR, unit)
        elif self.is_unit_valid(unit):
            return (MOVE_OK, unit)
        else:
            return (MOVE_LOCK, unit)

    def moves_unit_wu(self, unit, moves, allow_move_to_self):
         results = {MOVE_OK: [],
                    MOVE_LOCK: [],
                    MOVE_ERROR: [],
         }
         if allow_move_to_self:
             footprints = self.footprints - set([self.unit.footprint])
         else:
             footprints = self.footprints
         for move in moves:
             r, u = self.move_unit_result_wu(unit, move, footprints)
             results[r].append((move, u))
         return results

    def any_locking_move(self, unit):
        return any((x == MOVE_LOCK for x in (self.move_unit_result(unit, move) for move in MOVES)))

    def moves(self):
        return self.moves_unit(self.unit, MOVES)

    def move_unit(self, direction):
        if self.unit is None:
            return
        unit = self.unit.action(direction)
        if unit.footprint in self.footprints:
            raise ValueError('Illegal move: %d'%direction)
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
            self.score = self.score + self.calc_unit_score(self.unit, ls)
            self.ls_old = ls
            self.next_unit()

    def calc_unit_score(self, unit, cleared_lines):
        points = len(unit.members) + 100 * (1 + cleared_lines) * cleared_lines / 2
        line_bonus = 0
        if self.ls_old > 1:
            line_bonus = math.floor((self.ls_old - 1) * points / 10)
        return points + line_bonus

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
        self.units = [Unit.get_or_create_unit(jc2t(u["pivot"]), [jc2t(m) for m in u["members"]]) for u in problem["units"]]
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
