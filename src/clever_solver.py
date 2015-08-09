#!/usr/bin/env python

import astar
import copy
import game
import hx
import operator
import solver

def draw(g, unit):
    rows = []
    for row in range(g.board.height):
        rows.append(['|*' if c else '| ' for c in g.board.cells[row]])
    if unit:
        for m in unit.members:
            col, row = m
            rows[row][col] = '|@'
    if g.unit:
        for m in g.unit.members:
            col, row = m
            rows[row][col] = '|s'
    for rowix, row in enumerate(rows):
        padding = '' if rowix % 2 == 0 else ' '
        print padding + ''.join(row)

def find_path(gameobj, goal):
    def g(n1, n2):
        return 1
    def nf(g):
        def neighbours(u):
            nb = []
            for d in game.CMDS:
                new_u = u.action(d)
                col, row = new_u.pivot
                if gameobj.is_unit_valid(new_u):
                    nb.append(new_u)
            return nb
        return neighbours
    def hf(goal):
        def h(n):
            gc, gr = goal.pivot
            nc, nr = n.pivot
            return hx.distance(hx.to_hex(gc, gr), hx.to_hex(nc, nr))
        return h
    f, p = astar.astar(gameobj.unit, goal, g, hf(goal), nf(None))
    moves = [p[i].move_to_reach(p[i + 1]) for i in range(len(p) - 1)]
    return moves


class CleverSolver(solver.BaseSolver):
    def solve(self, g, verbosity):
        commands = []
        cmds = {game.CMD_E: 'b',
                game.CMD_W: 'p',
                game.CMD_SE: 'l',
                game.CMD_SW: 'a',
                game.CMD_CW: 'd',
                game.CMD_CCW: 'k'}
        bw, bh = g.size
        fbh = float(bh)
        fbw = float(bw)
        ftot = float(bw*bh)
        maxjaggedness = ftot / 2
        computed_units = {}
        while True:
            if verbosity > 0:
                print g.num_units, g.max_units
            if verbosity > 2:
                draw(g, None)
            scores = {}
            moves = []
            if g.unit is None:
                break
            # Compute possible units
            if g.unit in computed_units:
                processed = computed_units[g.unit]
            else:
                processed = set()
                for s in range(6):
                    unit = g.unit.rotate(hx.TURN_CW, s)
                    for row in range(bh):
                        for col in range(bw):
                            new_unit = unit.to_position_nw((col, row))
                            ok = True
                            for x, y in new_unit.members:
                                if x < 0 or x >= bw or y < 0 or y >= bh:
                                    ok = False
                                    break
                            if not ok or new_unit in processed:
                                continue
                            processed.add(new_unit)
                computed_units[g.unit] = processed
            if verbosity == 6:
                print "************************"
                print "num possible:", len(processed)
                for u in sorted(processed, key=lambda x: x.pivot):
                    draw(g, u)
                    print "************************"
            # Compute lockable units
            lockable = set()
            #reachable = g.board.reachable_cells(g.unit.members[0])
            for unit in processed:
                # if not all([m in reachable for m in unit.members]):
                #     continue
                if g.is_unit_valid(unit):
                    moves = g.moves_unit(unit)
                    if len(moves[game.MOVE_LOCK]) > 0:
                        lockable.add(unit)
            if verbosity > 0:
                print "lockables:", len(lockable)
            # Compute scores for all lockables
            scores = {}
            for unit in lockable:
                if verbosity == 5:
                    draw(g, unit)
                board = game.BoardWithUnit(g.board, unit)
                filled = 0
                for row in range(bh):
                    if board.filled_row(row):
                        filled += 1
                ceiling = board.ceiling
                heights = [bh - ceiling[col] for col in range(bw)]
                max_height = max(heights)
                sum_height = float(sum(heights))
                average_height = sum_height / fbw
                jaggedness = 0
                for col in range(bw - 1):
                    jaggedness += abs(heights[col] - heights[col])
                holes = 0
                for col in range(bw):
                    for row in range(ceiling[col], bh):
                        if not board.filled_cell(col, row):
                            holes += 1
                last_filled = False
                changes = 0
                elems = 0
                for row in range(bh):
                    for col in range(bw):
                        f = board.filled_cell(col, row)
                        if f:
                            elems += 1
                        if f != last_filled:
                            changes += 1
                        last_filled = f
                felems = float(elems)
                connectedness = (ftot - changes) / ftot
                filledness = (sum_height - holes) / felems
                evenness = (maxjaggedness - jaggedness) / maxjaggedness
#                score = g.calc_unit_score(unit, filled)
                avghscore = (bh - average_height) / fbh
                heightscore = (bh - max_height) / fbh
                downness = sum([y for x, y in unit.members]) / (len(unit.members) * fbh)
                if verbosity > 3:
                    print filled, avghscore, heightscore, filledness, evenness, downness, connectedness
                scores[unit] = filled + avghscore + heightscore + filledness + evenness + downness + connectedness

            # Go through them in order of best score
            moves = None
            for unit, score in reversed(sorted(scores.iteritems(), key=operator.itemgetter(1))):
                if verbosity > 0:
                    print "score:", score
                # Calculate the path
                moves = find_path(g, unit)
                if moves:
                    break
                else:
                    if verbosity > 1:
                        draw(g, unit)
            if not moves:
                break
            for m in moves:
                g.move_unit(m)
                commands.append(cmds[m])
            # lock unit if necessary
            if g.unit:
                lock_moves = g.moves()[game.MOVE_LOCK]
                if lock_moves:
                    m = lock_moves[0]
                    g.move_unit(m)
                    commands.append(cmds[m])
        if verbosity > 0:
            print "Final score:", g.score
        return commands

if __name__ == '__main__':
    s = CleverSolver()
    s.run()
