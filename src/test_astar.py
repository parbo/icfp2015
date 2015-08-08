import astar
import hx


if __name__=="__main__":
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
            return hx.hex_dist(goal, n)
        return h
    start = hx.to_hex(0, 0)
    goal = hx.to_hex(6, 7)
    f, p = astar.astar(start, goal, g, hf(goal), nf(None))
    print f, p
