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
            dirs = ['SE', 'SW']
            cmds = ['l', 'a']
            while True:
                ix = random.randint(0, 1)
                g.move_unit(dirs[ix])
                commands.append(cmds[ix])
                if g.unit is None:
                    break
            solution = {
                "problemId": problem.id,
                "seed": seed,
                "solution": ''.join(commands)
            }
            solutions.append(solution)
    print json.dumps(solutions)
