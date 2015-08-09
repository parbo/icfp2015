#!/usr/bin/env python

import astar
import copy
import game
import hx
import itertools
import math
import operator
import solver

def draw(g, unit, reachable=None):
    rows = []
    print "_"*g.board.width*2
    for row in range(g.board.height):
        rows.append(['|*' if c else '| ' for c in g.board.cells[row]])
    if reachable:
        for r in reachable:
            col, row = r
            rows[row][col] = '|.'
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
            moves = gameobj.moves_unit_wu(u)
            ok_moves = moves[game.MOVE_OK]
            return [new_u for d, new_u in ok_moves]
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
    def compute_possible(self, g, bw, bh):
        if g.unit in self.computed_units:
            processed = self.computed_units[g.unit]
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
            self.computed_units[g.unit] = processed
        if self.verbosity == 6:
            print "************************"
            print "num possible:", len(processed)
            for u in sorted(processed, key=lambda x: x.pivot):
                draw(g, u)
                print "************************"
        return processed

    def compute_lockable(self, g, possible):
        lockable = set()
        for unit in possible:
            if g.is_unit_valid(unit):
                if g.any_locking_move(unit):
                    lockable.add(unit)
        if self.verbosity > 0:
            print "lockables:", len(lockable)
        return lockable

    def compute_scores(self, g, lockable, bw, bh):
        fbh = float(bh)
        fbw = float(bw)
        ftot = float(bw*bh)
        maxjaggedness = ftot / 2
        scores = {}
        filled_cells = set()
        gb = g.board
        for row in range(gb.height):
            for col in range(gb.width):
                if gb.cells[row][col]:
                    filled_cells.add((col, row))
        for unit in lockable:
            if self.verbosity == 5:
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
            elems = 0
            filled_cells_unit = set(filled_cells)
            last_filled = False
            changes_before = 0
            for row in range(bh):
                for col in range(bw):
                    f = (col, row) in filled_cells_unit
                    if f != last_filled:
                        changes_before += 1
                    last_filled = f
            filled_cells_unit.update(set(unit.members))
            holes = 0
            for col in range(bw):
                ceil = ceiling[col]
                for row in range(bh):
                    f = (col, row) in filled_cells_unit
                    if f:
                        elems += 1
                    elif row >= ceil:
                        holes += 1
            last_filled = False
            changes = 0
            for row in range(bh):
                for col in range(bw):
                    f = (col, row) in filled_cells_unit
                    if f != last_filled:
                        changes += 1
                    last_filled = f
            felems = float(elems)
            # We want to reduce changes
            connectedness = (changes_before - changes)
            filledness = (sum_height - holes) / felems
            evenness = (maxjaggedness - jaggedness) / maxjaggedness
#                score = g.calc_unit_score(unit, filled)
            avghscore = (bh - average_height) / fbh
            heightscore = (bh - max_height) / fbh
            downness = sum([y for x, y in unit.members]) / (len(unit.members) * fbh)
#            reachability = sum([1 for m in unit.members if m in self.reachable]) / float(len(unit.members))
            total_score = 10 * filled + avghscore + heightscore + filledness + evenness + downness + connectedness #+ reachability
            if self.verbosity > 3:
                print "score:", total_score, "parts:", filled, avghscore, heightscore, filledness, evenness, downness, connectedness #, reachability
            scores[unit] = total_score
        return scores

    def find_moves(self, g, scores):
        moves = None
        for unit, score in reversed(sorted(scores.iteritems(), key=operator.itemgetter(1))):
            if self.verbosity > 0:
                print "score:", score
            # Skip known unreachable
            if (g.unit, unit) in self.unreachable:
                if self.verbosity > 1:
                    print "skipping unreachable!"
                continue
            # Calculate the path
            moves = find_path(g, unit)
            if moves:
                if self.verbosity > 1:
                    draw(g, unit)
                break
            else:
                self.unreachable.add((g.unit, unit))
                if self.verbosity > 1:
                    draw(g, unit)
        return moves

    def solve(self, g, verbosity):
        self.verbosity = verbosity
        commands = []
        cmds = {game.CMD_E: 'b',
                game.CMD_W: 'p',
                game.CMD_SE: 'l',
                game.CMD_SW: 'a',
                game.CMD_CW: 'd',
                game.CMD_CCW: 'k'}
        bw, bh = g.size
        self.computed_units = {}
        self.unreachable = set()
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
            possible = self.compute_possible(g, bw, bh)
            # Compute lockable units
            lockable = self.compute_lockable(g, possible)
            # Compute scores for all lockables, 100 at a time
            # Take from bottom up.
            # Reachability is used when computing scores
            # self.reachable = g.board.reachable_cells(g.unit.members[0], 1)
            sorted_lockable = list(reversed(sorted(lockable, key=lambda x: x.north_border)))
            moves = None
            for ix in range(0, len(sorted_lockable), 100):
                scores = self.compute_scores(g, sorted_lockable[ix:ix+100], bw, bh)
                # Go through them in order of best score
                moves = self.find_moves(g, scores)
                if moves:
                    break
            # Do the moves
            if not moves:
                break
            if verbosity > 2:
                print moves
            for m in moves:
                g.move_unit(m)
                if g.ls_old > 0:
                    self.unreachable = set()
                if verbosity > 6:
                    draw(g, None)
                commands.append(cmds[m])
            # lock unit if necessary
            if g.unit:
                lock_moves = g.moves()[game.MOVE_LOCK]
                if lock_moves:
                    m = lock_moves[0]
                    g.move_unit(m)
                    if g.ls_old > 0:
                        self.unreachable = set()
                    commands.append(cmds[m])
        if verbosity > 0:
            print "Final score:", g.score
        return commands

if __name__ == '__main__':
    s = CleverSolver()
    s.run()
