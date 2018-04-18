import sys
from itertools import chain
from parser import parse_files

from scipy.spatial import cKDTree

DEFAULT_RADIUS = 5

def create_cKDTree(neurites):
    return cKDTree(neurites, copy_data=True)

def create_bin_cKDTree(neurons):
    data = list(chain(*neurons))
    return data, cKDTree(data, copy_data=True)

# this uses separate trees and finds neighbors for each pair
def find_neighbors(neurons, radius=DEFAULT_RADIUS):
    # create a list of kd-trees
    trees = [ create_cKDTree(neurites) for neurites in neurons ]

    # use the kd-trees to find all the pairs at most radius apart
    pairs = []
    for i, source in enumerate(trees):
        for j, target in enumerate(trees):
            if i == j: continue

            # around every point in source
            # center a sphere with radius,
            # find the points in target which fall inside this sphere
            res = source.query_ball_tree(target, radius)
            pairs.append((i, j, res))

    # print('Found all pairs')

    # filter out valid pairs
    valid_pairs = set()
    for i, j, res in pairs:
        # res will be of the same length as its number of data points
        # so we can zip them together
        for source, neighbors in zip(neurons[i], res):
            for target in [ neurons[j][k] for k in neighbors ]:
                if source.type == 2 and target.type == 3:
                    # source is axon, target is dendrite
                    valid_pairs.add((source, target))
                elif source.type == 3 and target.type == 2:
                    # source is dendrite, target is axon

                    # doing this one backwards might make it
                    # easier to recreate a directed graph in the future
                    # maybe it should be the other way around, though?
                    valid_pairs.add((target, source))

    return valid_pairs

# this one should be quicker as it creates one big tree
# might get stack overflow issues with a lot of data?
def find_neighbors(neurons, radius=DEFAULT_RADIUS):
    data, tree = create_bin_cKDTree(neurons)

    res = tree.query_pairs(radius)

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

    return valid_pairs

if __name__ == '__main__':
    neurons = [ list(n.neurites()) for n in parse_files(sys.argv[1:]) ]

    print(len(neurons), 'files parsed')

    valid_pairs = find_neighbors(neurons)

    print(len(valid_pairs), 'valid pairs found')
    for n1, n2 in sorted(list(valid_pairs), key=lambda n: (n[0].filename, n[0].id)):
        # a lot of these will be very similar and we sould try to
        # group them together or select only the closest pair
        print(
            n1.id, n2.id,
            n1.x, n2.x,
            n1.y, n2.y,
            n1.z, n2.z,
            sep='\t'
        )
