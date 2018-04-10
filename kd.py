#originally taken from https://rosettacode.org/wiki/K-d_tree#Python

from random import seed, random
from time import clock
from operator import itemgetter
from collections import namedtuple
from math import sqrt
from copy import deepcopy


def sqd(p1, p2):
    return sum((c1 - c2) ** 2 for c1, c2 in zip(p1, p2))


class KdNode(object):
    __slots__ = ("dom_elt", "split", "left", "right")

    def __init__(self, dom_elt, split, left, right):
        self.dom_elt = dom_elt
        self.split = split
        self.left = left
        self.right = right

    def __repr__(self):
        return '<KDNode {}, {}, {}, {}>'.format(self.dom_elt, self.split, self.left, self.right)


class Orthotope(object):
    __slots__ = ("min", "max")

    def __init__(self, mi, ma):
        self.min, self.max = mi, ma

    def __repr__(self):
        return 'Orthotope({}, {})'.format(self.min, self.max)


class KdTree(object):
    __slots__ = ("n", "bounds")

    def __init__(self, pts, bounds):
        def nk2(split, exset):
            if not exset:
                return None
            exset.sort(key=itemgetter(split))
            m = len(exset) // 2
            d = exset[m]
            while m + 1 < len(exset) and exset[m + 1][split] == d[split]:
                m += 1

            s2 = (split + 1) % len(d)  # cycle coordinates
            return KdNode(d, split, nk2(s2, exset[:m]),
                                    nk2(s2, exset[m + 1:]))
        self.n = nk2(0, pts)
        self.bounds = bounds

T3 = namedtuple("T3", "nearest dist_sqd nodes_visited")


def find_nearest(k, t, p):
    def nn(kd, target, hr, max_dist_sqd):
        if kd is None:
            return T3([0.0] * k, float("inf"), 0)

        nodes_visited = 1
        s = kd.split
        pivot = kd.dom_elt
        left_hr = deepcopy(hr)
        right_hr = deepcopy(hr)
        left_hr.max[s] = pivot[s]
        right_hr.min[s] = pivot[s]

        if target[s] <= pivot[s]:
            nearer_kd, nearer_hr = kd.left, left_hr
            further_kd, further_hr = kd.right, right_hr
        else:
            nearer_kd, nearer_hr = kd.right, right_hr
            further_kd, further_hr = kd.left, left_hr

        n1 = nn(nearer_kd, target, nearer_hr, max_dist_sqd)
        nearest = n1.nearest
        dist_sqd = n1.dist_sqd
        nodes_visited += n1.nodes_visited

        if dist_sqd < max_dist_sqd:
            max_dist_sqd = dist_sqd
        d = (pivot[s] - target[s]) ** 2
        if d > max_dist_sqd:
            return T3(nearest, dist_sqd, nodes_visited)
        d = sqd(pivot, target)
        if d < dist_sqd:
            nearest = pivot
            dist_sqd = d
            max_dist_sqd = dist_sqd

        n2 = nn(further_kd, target, further_hr, max_dist_sqd)
        nodes_visited += n2.nodes_visited
        if n2.dist_sqd < dist_sqd:
            nearest = n2.nearest
            dist_sqd = n2.dist_sqd

        return T3(nearest, dist_sqd, nodes_visited)

    return nn(t.n, p, t.bounds, float("inf"))


def show_nearest(k, heading, kd, p):
    print(heading + ":")
    print("Point:           ", p)
    t0 = clock()
    n = find_nearest(k, kd, p)
    t1 = clock()
    print('Search time:', t1-t0)
    print("Nearest neighbor:", n.nearest)
    print("Distance:        ", sqrt(n.dist_sqd))
    print("Nodes visited:   ", n.nodes_visited, "\n")


if __name__ == "__main__":

    P = lambda *coords: list(coords)

    kd1 = KdTree([
            DataPoint('test', 2, 3),
            DataPoint('test1', 5, 4),
            DataPoint('test2', 9, 6),
            DataPoint('test3', 4, 7),
            DataPoint('test4', 8, 1),
            DataPoint('test5', 7, 2)
        ],
        Orthotope(P(0, 0), P(10, 10))
    )

    show_nearest(2, "Wikipedia example data", kd1, P(9, 2))
