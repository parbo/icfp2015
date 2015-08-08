import astar
import game
import hx

def test_hex():
    def g(n1, n2):
        return 1
    def nf(g):
        def neighbours(n):
            nb = []
            for d in [hx.DIRECTION_E, hx.DIRECTION_W, hx.DIRECTION_SE, hx.DIRECTION_SW]:
                new_n = hx.hex_add(n, d)
                col, row = hx.to_offset(new_n)
                if 0 <= col < 10 and 0 <= row < 10:
                    nb.append(new_n)
            print hx.to_offset(n), [hx.to_offset(x) for x in nb]
            return nb
        return neighbours
    def hf(goal):
        def h(n):
            return hx.distance(goal, n)
        return h
    start = hx.to_hex(0, 0)
    goal = hx.to_hex(6, 7)
    f, p = astar.astar(start, goal, g, hf(goal), nf(None))
    print f, [hx.to_offset(x) for x in p]

def test_units():
    def g(n1, n2):
        return 1
    def nf(g):
        def neighbours(u):
            nb = []
            for d in ["E", "W", "SE", "SW", "CW", "CCW"]:
                new_u = u.action(d)
                col, row = new_u.pivot
                if 0 <= col < 10 and 0 <= row < 10:
                    nb.append(new_u)
            print u.pivot, u.members, [(x.pivot, x.members) for x in nb]
            return nb
        return neighbours
    def hf(goal):
        def h(n):
            gc, gr = goal.pivot
            nc, nr = n.pivot
            return hx.distance(hx.to_hex(gc, gr), hx.to_hex(nc, nr))
        return h
    start = game.Unit((0, 0), [(0, 0), (1, 0)])
    goal = game.Unit((1, 6), [(1, 6), (1, 7)])
    f, p = astar.astar(start, goal, g, hf(goal), nf(None))
    moves = [p[i].move_to_reach(p[i + 1]) for i in range(len(p) - 1)]
    print f, moves

if __name__=="__main__":
    test_hex()
    test_units()
