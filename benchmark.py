from time import time
import numpy as np
from math import pi, cos, sin, sqrt
from random import seed, random, sample, choice
from parser import parse_files
from algorithm import find_neighbors, find_neighbors_alternate

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
    seed('Just to keep things consistent')
    neurons = []

    # 47% of neurons in size
    neurons.extend(big_sample(msn_d1, 0.475*density*size**3))
    print('msn_d1 neurons added', len(neurons), 'total')

    # 47% of neurons in size
    neurons.extend(big_sample(msn_d2, 0.475*density*size**3))
    print('msn_d2 neurons added', len(neurons), 'total')

    # 1% of neurons in size
    neurons.extend(big_sample(fs_pv, 0.01*density*size**3))
    print('fs_pv neurons added', len(neurons), 'total')

    for n in neurons:
        x, y, z = [ random() * size - size for _ in range(3) ]
        for nn in n: nn.translate(x, y, z)
    print(len(neurons), 'neurons translated')

    # rotate and translate randomly
    for n in neurons:
        axis = random_axis(n)
        theta = random()*2*pi
        transform = rotation_matrix(axis, theta)
        for nn in n: nn.transform(transform)
    print(len(neurons), 'neurons rotated')

    tbefore = time()
    pairs = algorithm(neurons, radius)
    tafter = time()

    print(len(pairs), 'pairs found in', tafter - tbefore, ' seconds.')

if __name__ == '__main__':
    # works ok
    # run_benchmark(1, 100, 1, find_neighbors)
    # run_benchmark(1, 200, 1, find_neighbors)
    # run_benchmark(1, 400, 1, find_neighbors)
    # run_benchmark(1, 800, 1, find_neighbors)

    # out of memory
    # run_benchmark(1, 1600, 1, find_neighbors)
    # run_benchmark(1, 3200, 1, find_neighbors)

    # works ok
    # run_benchmark(1, 100, 1, find_neighbors)
    # run_benchmark(2, 100, 1, find_neighbors)

    # out of memory
    # run_benchmark(4, 100, 1, find_neighbors)
    # run_benchmark(8, 100, 1, find_neighbors)
    # run_benchmark(16, 100, 1, find_neighbors)
    # run_benchmark(32, 100, 1, find_neighbors)

    run_benchmark(1, 100, .5, find_neighbors)
    run_benchmark(1, 100, 1, find_neighbors)
    run_benchmark(1, 100, 2, find_neighbors)
    run_benchmark(1, 100, 3, find_neighbors)
    run_benchmark(1, 100, 4, find_neighbors)
    run_benchmark(1, 100, 5, find_neighbors)

    # way too slow
    # run_benchmark(1, 200, 5, find_neighbors_alternate)
