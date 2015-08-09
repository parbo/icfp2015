#!/usr/bin/env python

import argparse
import game
import hx
import json
import multiprocessing as mp
import random
import traceback

def pickle_helper(arg):
    solver, problem, seed, seed_index, verbosity = arg
    return solver.runSeed(problem, seed, seed_index, verbosity)

class BaseSolver(object):
    def runSeed(self, problem, seed, seed_index, verbosity):
        random.seed(seed)
        g = problem.make_game(seed_index)
        try:
            commands = self.solve(g, verbosity)
        except Exception as e:
            if verbosity > 0:
                traceback.print_exc(e)
                commands = list('error')
        solution = {
            "problemId": problem.id,
            "seed": seed,
            "solution": ''.join(commands)
        }
        return solution

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', dest='files', action='append', required=True)
        parser.add_argument('-p', dest='power', action='append')
        parser.add_argument('-t', dest='time', action='store', type=int, default=999999)
        parser.add_argument('-m', dest='memory', action='store', type=int)
        parser.add_argument('-c', dest='cores', action='store', type=int, default=1)
        parser.add_argument('-v', dest='verbosity', action='store', type=int, default=0)
        args = parser.parse_args()

        solutions = []
        for f in args.files:
            problem = game.Problem.load(f)
            params = [(self, problem, seed, seed_index, args.verbosity) for seed_index, seed in enumerate(problem.source_seeds)]
            p = mp.Pool(args.cores)
            s = p.map_async(pickle_helper, params).get(args.time)
            solutions.extend(s)
        print json.dumps(solutions)
