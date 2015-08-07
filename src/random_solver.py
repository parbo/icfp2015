#!/usr/bin/env python

import coords
import game
import json
import random
import sys

if __name__=="__main__":
    problem = game.Problem.load(sys.argv[1])
    solutions = []
    for seed_index, seed in enumerate(problem.source_seeds):
        random.seed(seed)
        g = problem.make_game(seed_index)
        commands = []
        dirs = [coords.DIRECTION_SE, coords.DIRECTION_SW]
        cmds = ['a', 'l']
        while True:
            ix = random.randint(0, 1)
            g.move_unit(dirs[ix])
            if g.unit is None:
                break
            commands.append(cmds[ix])
        solution = {
            "problemId": problem.id,
            "seed": seed,
            "solution": ''.join(commands)
            }
        solutions.append(solution)
    print json.dumps(solutions)
