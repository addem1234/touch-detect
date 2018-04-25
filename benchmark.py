from time import time
import numpy as np
from uuid import uuid4
from math import pi, cos, sin, sqrt
from random import seed, random, sample, choice
from memory_profiler import memory_usage
from parser import parse_files
from algorithm import find_neighbors, find_neighbors_all_balls

msn_d1 = [list(n.neurites()) for n in parse_files(['neurons/msn_d1-20170919-reg5'])]
print(len(msn_d1), 'files parsed from msn_d1')

msn_d2 = [list(n.neurites()) for n in parse_files(['neurons/msn_d2-20170919-reg5'])]
print(len(msn_d2), 'files parsed from msn_d2')

fs_pv = [list(n.neurites()) for n in parse_files(['neurons/fs_pv-20170919-reg5'])]
print(len(fs_pv), 'files parsed from fs_pv')

def big_sample(n, k):
    for _ in range(int(k)): yield choice(n)

# grab a pair of neurons to create an axis to rotate around
def random_axis(neurites):
    x, y = sample(neurites, 2)
    return tuple([a - b for a, b in zip(x, y)])

def rotation_matrix(axis, theta):
    """
    Source: https://stackoverflow.com/questions/6802577/rotation-of-3d-vector?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    Author: unutbu
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/sqrt(np.dot(axis, axis))
    a = cos(theta/2.0)
    b, c, d = -axis*sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

# size is length of side of cube in mm
# density is # neurons in cube with side size
# radius is max distance between neighbors in microns
def run_benchmark(size, density, radius, algorithm):
    neurons = []

    # 47% of neurons in size
    neurons.extend(big_sample(msn_d1, 0.475*density*size**3))
    # print('msn_d1 neurons added', len(neurons), 'total')

    # 47% of neurons in size
    neurons.extend(big_sample(msn_d2, 0.475*density*size**3))
    # print('msn_d2 neurons added', len(neurons), 'total')

    # 1% of neurons in size
    neurons.extend(big_sample(fs_pv, 0.01*density*size**3))
    # print('fs_pv neurons added', len(neurons), 'total')

    for n in neurons:
        x, y, z = [ random() * size - size for _ in range(3) ]
        for nn in n: nn.translate(x, y, z)
    # print(len(neurons), 'neurons translated')

    # rotate and translate randomly
    for n in neurons:
        axis = random_axis(n)
        theta = random()*2*pi
        transform = rotation_matrix(axis, theta)
        for nn in n: nn.transform(transform)
    # print(len(neurons), 'neurons rotated')

    for n in neurons:
        for nn in n: nn.name = uuid4()
    # print(len(neurons), 'neurons renamed')

    for i in range(10):
        print(algorithm.__name__, size, density, radius, sep=', ', end=', ')
        tbefore = time()
        ramsamples = memory_usage((algorithm, (neurons, radius))) # logs points, constructions, query_pairs, filtering
        print(time()-tbefore, min(ramsamples), max(ramsamples), sep=', ')

if __name__ == '__main__':
    print('algorithm'. 'size', 'density', 'radius', 'points', 'consctruction time', 'size', 'query_pairs', 'filtering', 'total', 'min memory', 'max memory', sep=', ')
    for seeed in range(3):
        for alg in [find_neighbors, find_neighbors_all_balls]:
            seed(seeed)
            # print(seeed, alg.__name__, 'varying distance')
            for i in [n/10 for n in range(5, 55, 5)]:
                run_benchmark(1, 250, i, alg)

            # print(seeed, alg.__name__, 'varying density')
            for i in range(100, 1000, 100):
                run_benchmark(1, i, 1, alg)

            # print(seeed, alg.__name__, 'varying sise')
            for i in range(5):
                run_benchmark(i, 250, 1, alg)
