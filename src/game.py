#!/usr/bin/env python

import coords

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

    def filled_row(self, row):
        return all(self.cells[row])

    def clear_row(self, row):
        for row in range(row, 0, -1):
            self.cells[row] = self.cells[row - 1]
        self.cells[0] = self.create_empty_row()

    def position(self, origin, direction):
        """
        Calculates a new position given a current position and the direction of movement.
        Raises LookupError if the new position is invalid.
        """
        row, col = coords.move(origin, direction)
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
        pivot = coords.move(self.pivot, direction)
        members = [coords.move(member, direction) for member in self.members]
        return Unit(pivot, members)

class Game(object):
    def __init__(self, board, unit):
        self.board = board
        self.unit = unit

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

    def move_unit(self, direction):
        if self.unit is None:
            return
        self.unit = self.unit.move(direction)

if __name__ == '__main__':
    board = Board(10, 10, [(1, 1)])
    print board
    print board.view()
