import sys
from time import time
from itertools import chain
from parser import parse_files

from scipy.spatial import cKDTree

DEFAULT_RADIUS = 5

def create_cKDTree(neurites):
    return cKDTree(neurites, copy_data=True)

def create_big_cKDTree(neurons):
    data = list(chain(*neurons))
    return data, cKDTree(data, copy_data=True)

# this uses separate trees and finds neighbors for each pair
def find_neighbors_balls(neurons, radius=DEFAULT_RADIUS):
    # create a list of kd-trees
    tbefore = time()
    trees = [ create_cKDTree(neurites) for neurites in neurons ]
    tafter = time()
    print('tree construction time', tafter-tbefore)
    print(sum([len(n) for n in neurons]), 'points in total')

    tbefore = time()
    # use the kd-trees to find all the pairs at most radius apart
    #pairs = []
    valid_pairs = set()
    N = len(trees)
    for i, source in enumerate(trees):
        for j, target in enumerate(trees):
            print('\rprogress: {}/{}, {}/{}, {}\t'.format(i, N, j, N, time()-tbefore), end='')
            if i == j: continue

            # around every point in source
            # center a sphere with radius,
            # find the points in target which fall inside this sphere
            res = source.query_ball_tree(target, radius)

            #pairs.append((i, j, res))

            # res will be of the same length as its number of data points
            # so we can zip them together
            for source_n, neighbors in zip(neurons[i], res):
                for target in [ neurons[j][k] for k in neighbors ]:
                    if source_n.type_s == 'axon' and target.type_s in ['dendrite', 'soma']:
                        valid_pairs.add((source_n, target))
                    elif source_n.type_s == 'dendrite' and target.type_s == 'axon':

                        # doing this one backwards might make it
                        # easier to recreate a directed graph in the future
                        # maybe it should be the other way around, though?
                        # does things go from axon to dendrite or dendrite to axon?
                        valid_pairs.add((target, source_n))
                    elif source_n.type_s == 'soma' and target.type_s == 'axon':
                        valid_pairs.add((target, source_n))

    tafter = time()
    print('pair search time', tafter-tbefore)

    # print('Found all pairs')

    # tbefore = time()
    # filter out valid pairs
    # for i, j, res in pairs:

    # tafter = time()
    # print('filter time', tafter-tbefore)

    return valid_pairs

# this one should be quicker as it creates one big tree
# might get stack overflow issues with a lot of data
def find_neighbors(neurons, radius=DEFAULT_RADIUS):
    tbefore = time()
    data, tree = create_big_cKDTree(neurons)
    tafter = time()
    print('tree construction time', tafter-tbefore)
    print(sum([len(n) for n in neurons]), 'points in total')

    tbefore = time()
    res = tree.query_pairs(radius)
    tafter = time()
    print('query_pairs time', tafter-tbefore)

    tbefore = time()
    valid_pairs = set()
    for source, neighbors in zip(data, res):
        for target in [ data[k] for k in neighbors]:
            # we need to filter out neighbors that belong to the same neuron
            if source.filename == target.filename:
                continue

            if source.type_s == 'axon' and target.type_s == 'dendrite':
                valid_pairs.add((source, target))
            elif source.type_s == 'dendrite' and target.type_s == 'axon':

                # doing this one backwards might make it
                # easier to recreate a directed graph in the future
                # maybe it should be the other way around, though?
                # does things go from axon to dendrite or dendrite to axon?
                valid_pairs.add((target, source))
            elif source.type_s == 'soma' and target.type_s == 'axon':
                valid_pairs.add((target, source))

    tafter = time()
    print('filtering time', tafter-tbefore)

    return valid_pairs

# this one should be quicker as it creates one big tree
# might get stack overflow issues with a lot of data
def find_neighbors_all_balls(neurons, radius=DEFAULT_RADIUS):
    tbefore = time()
    data, tree = create_big_cKDTree(neurons)
    tafter = time()
    print('tree construction time', tafter-tbefore)
    print(sum([len(n) for n in neurons]), 'points in total')

    tbefore = time()
    res = tree.query_ball_tree(tree, radius)
    tafter = time()
    print('query_ball_tree time', tafter-tbefore)

    tbefore = time()
    valid_pairs = set()
    for source, neighbors in zip(data, res):
        for target in [ data[k] for k in neighbors]:
            # we need to filter out neighbors that belong to the same neuron
            if source.filename == target.filename:
                continue

            if source.type_s == 'axon' and target.type_s == 'dendrite':
                valid_pairs.add((source, target))
            elif source.type_s == 'dendrite' and target.type_s == 'axon':

                # doing this one backwards might make it
                # easier to recreate a directed graph in the future
                # maybe it should be the other way around, though?
                # does things go from axon to dendrite or dendrite to axon?
                valid_pairs.add((target, source))
            elif source.type_s == 'soma' and target.type_s == 'axon':
                valid_pairs.add((target, source))

    tafter = time()
    print('filtering time', tafter-tbefore)

    return valid_pairs

if __name__ == '__main__':
    neurons = [ list(n.neurites()) for n in parse_files(sys.argv[1:]) ]

    print(len(neurons), 'files parsed')

    valid_pairs = find_neighbors(neurons)

    print(len(valid_pairs), 'valid pairs found')
    # for n1, n2 in sorted(list(valid_pairs), key=lambda n: (n[0].filename, n[0].id)):
    #     # a lot of these will be very similar and we sould try to
    #     # group them together or select only the closest pair
    #     print(
    #         n1.id, n2.id,
    #         n1.x, n2.x,
    #         n1.y, n2.y,
    #         n1.z, n2.z,
    #         sep='\t'
    #     )
