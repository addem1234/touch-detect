import sys
from time import time
from itertools import chain
from parser import parse_files

from scipy.spatial import cKDTree

DEFAULT_RADIUS = 5

def create_big_cKDTree(neurons):
    data = list(chain(*neurons))
    return data, cKDTree(data, copy_data=True)

# this one should be quicker as it creates one big tree
# might get stack overflow issues with a lot of data
def find_neighbors(neurons, radius=DEFAULT_RADIUS):
    print(sum([len(n) for n in neurons]), end=', ')
    tbefore = time()
    data, tree = create_big_cKDTree(neurons)
    print(time()-tbefore, end=', ')

    tbefore = time()
    res = tree.query_pairs(radius)
    print(time()-tbefore, end=', ')

    tbefore = time()
    valid_pairs = set()
    for source, neighbors in zip(data, res):
        for target in [ data[k] for k in neighbors ]:
            # we need to filter out neighbors that belong to the same neuron
            if source.name == target.name:
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

    print(time()-tbefore, end=', ')

    return valid_pairs

# this one should be quicker as it creates one big tree
# might get stack overflow issues with a lot of data
def find_neighbors_all_balls(neurons, radius=DEFAULT_RADIUS):
    print(sum([len(n) for n in neurons]), end=', ')
    tbefore = time()
    data, tree = create_big_cKDTree(neurons)
    print(time()-tbefore, end=', ')

    tbefore = time()
    res = tree.query_ball_tree(tree, radius)
    print(time()-tbefore, end=', ')

    tbefore = time()
    valid_pairs = set()
    for source, neighbors in zip(data, res):
        for target in [ data[k] for k in neighbors ]:
            # we need to filter out neighbors that belong to the same neuron
            if source.name == target.name:
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

    print(time()-tbefore, end=', ')

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
