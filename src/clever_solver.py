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
        bw, bh = g.size
        while True:
            scores = {}
            moves = []
            if g.unit is None:
                break
            lockable = set()
            processed = set()
            for s in range(6):
                unit = g.unit.rotate(hx.TURN_CW, s)
                x, y = unit.west_border, unit.north_border
                px, py = unit.pivot
                ox, oy = px-x, py-y
                for row in range(bh):
                    for col in range(bw):
                        new_unit = unit.to_position((ox + col, oy + row))
                        if new_unit in processed:
                            continue
                        processed.add(new_unit)
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
                for row in range(bh):
                    if board.filled_row(row):
                        filled += 1
                heights = [bh - board.ceiling[col] for col in range(bw)]
                max_height = max(heights)
                average_height = sum(heights) / float(bw)
                score = g.calc_unit_score(unit, filled)
                avghscore = (bh - average_height)
                heightscore = (bh - max_height)
                scores[unit] = score + avghscore + heightscore

            # Go through them in order of best score
            moves = None
            for unit, score in reversed(sorted(scores.iteritems(), key=operator.itemgetter(1))):
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
