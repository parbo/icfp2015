#!/usr/bin/env python

import game
import random
import solver

class RandomSolver(solver.BaseSolver):
    def solve(self, g, verbosity):
        commands = []
        cmds = {game.CMD_E: 'b',
                game.CMD_W: 'p',
                game.CMD_SE: 'l',
                game.CMD_SW: 'a',
                game.CMD_CW: 'd',
                game.CMD_CCW: 'k'}
        while True:
            moves = g.moves()
            non_lock = moves[game.MOVE_OK]
            lock = moves[game.MOVE_LOCK]
            candidates = non_lock if non_lock else lock
            if candidates:
                move = random.choice(candidates)
                g.move_unit(move)
                commands.append(cmds[move])
            else:
                break
            if g.unit is None:
                break
        return commands

if __name__ == '__main__':
    s = RandomSolver()
    s.run()
