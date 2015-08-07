#!/usr/bin/env python

DIRECTION_E = 0
DIRECTION_W = 1
DIRECTION_SE = 2
DIRECTION_SW = 3

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
        if (0 < new_col < self.width) and (0 < new_row < self.height):
            return (new_col, new_row)
        raise LookupError('Invalid position: (%d, %d)' % (new_col, new_row))

    def create_empty_row(self):
        return self.width * [False]

if __name__ == '__main__':
    board = Board(10, 10, [(1, 1)])
    print board
    print board.view()
