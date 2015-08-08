#!/usr/bin/env python

import game
import operator
import solver

def score(g):
    # Award being far down
    downness = 0
    if g.unit:
        downness = sum([y for x, y in g.unit.members])
    return g.score + downness / (1 + g.score)

def do_solve(g, m, s):
    if len(s) > 1000:
        return
    moves = g.moves()
    non_lock = moves[game.MOVE_OK]
    lock = moves[game.MOVE_LOCK]
    candidates = non_lock + lock
    preference = {"SE": 1, "SW": 2, "E": 3, "W": 4, "CW": 5, "CCW": 6}
    if not candidates:
        s[tuple(m)] = score(g)
    else:
        for move in sorted(candidates, key=lambda x: preference[x]):
            new_g = g.clone()
            new_g.move_unit(move)
            new_m = m[:]
            new_m.append(move)
            if move in non_lock:
                do_solve(new_g, new_m, s)
            else:
                s[tuple(new_m)] = score(new_g)

class SearchSolver(solver.BaseSolver):
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
            do_solve(g, moves, scores)
            # Take the best one
            best = max(scores.iteritems(), key=operator.itemgetter(1))
            best_moves = best[0]
            if not best_moves:
                break
            for b in best_moves:
                g.move_unit(b)
            commands.extend([cmds[x] for x in best_moves])
        return commands

if __name__ == '__main__':
    s = SearchSolver()
    s.run()
