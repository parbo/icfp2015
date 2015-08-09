#!/usr/bin/env python

import astar
import copy
import game
import hx
import operator
import solver

def find_path(game, goal):
    def g(n1, n2):
        return 1
    def nf(g):
        def neighbours(u):
            nb = []
            for d in ["E", "W", "SE", "SW", "CW", "CCW"]:
                new_u = u.action(d)
                col, row = new_u.pivot
                if game.is_unit_valid(new_u):
                    nb.append(new_u)
            return nb
        return neighbours
    def hf(goal):
        def h(n):
            gc, gr = goal.pivot
            nc, nr = n.pivot
            return hx.distance(hx.to_hex(gc, gr), hx.to_hex(nc, nr))
        return h
    f, p = astar.astar(game.unit, goal, g, hf(goal), nf(None))
    moves = [p[i].move_to_reach(p[i + 1]) for i in range(len(p) - 1)]
    return moves


class CleverSolver(solver.BaseSolver):
    def solve(self, g):
        commands = []
        cmds = {'E': 'b',
                'W': 'p',
                'SE': 'l',
                'SW': 'a',
                'CW': 'd',
                'CCW': 'k'}
        while True:
            scores = {}
            moves = []
            if g.unit is None:
                break
            lockable = set()
            for s in range(5):
                unit = g.unit.rotate(s)
                x, y = unit.west_border, unit.north_border
                px, py = unit.pivot
                ox, oy = px-x, py-y
                h, w = g.size
                for row in range(h):
                    for col in range(w):
                        new_unit = unit.to_position((oy + row, ox + col))
                        if g.is_unit_valid(new_unit):
                            moves = g.moves_unit(new_unit)
                            if len(moves[game.MOVE_LOCK]) > 0:
                                lockable.add(new_unit)
            # Compute scores for all lockables
            scores = {}
            for unit in lockable:
                # There should be a cheaper way to calculate this
                board = copy.deepcopy(g.board)
                board.lock(unit.members)
                filled = 0
                for row in range(board.height):
                    if board.filled_row(row):
                        filled += 1
                scores[unit] = g.calc_score(unit, filled)
            # Go through them in order of best score
            moves = None
            for unit, score in sorted(scores.iteritems(), key=operator.itemgetter(1)):
                # Calculate the path
                moves = find_path(g, unit)
                if moves:
                    break
            if not moves:
                break
            for m in moves:
                g.move_unit(m)
                commands.append(cmds[m])
            # lock unit
            lock_moves = g.moves()[game.MOVE_LOCK]
            if lock_moves:
                m = lock_moves[0]
                g.move_unit(m)
                commands.append(cmds[m])
        return commands

if __name__ == '__main__':
    s = CleverSolver()
    s.run()
