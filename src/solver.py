#!/usr/bin/env python

import argparse
import game
import hx
import json
import random
import traceback

class BaseSolver(object):
    def run(self):
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
                try:
                    commands = self.solve(g)
                except Exception as e:
                    #traceback.print_exc(e)
                    commands = list('error')
                solution = {
                    "problemId": problem.id,
                    "seed": seed,
                    "solution": ''.join(commands)
                }
                solutions.append(solution)
        print json.dumps(solutions)
