#!/usr/bin/env python

import argparse
import game
import hx
import json
import random

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='files', action='append', required=True)
    parser.add_argument('-p', dest='power', action='append')
    parser.add_argument('-t', dest='time', action='store', type=int)
    parser.add_argument('-m', dest='memory', action='store', type=int)
    parser.add_argument('-c', dest='cores', action='store', type=int)
    args = parser.parse_args()

    solutions = []
    for f in args.files:
        problem = game.Problem.load(f)
        for seed_index, seed in enumerate(problem.source_seeds):
            random.seed(seed)
            g = problem.make_game(seed_index)
            commands = []
            cmds = {'E': 'b',
                    'W': 'p',
                    'SE': 'l',
                    'SW': 'a',
                    'CW': 'd',
                    'CCW': 'k'}
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
            solution = {
                "problemId": problem.id,
                "seed": seed,
                "solution": ''.join(commands)
            }
            solutions.append(solution)
    print json.dumps(solutions)
