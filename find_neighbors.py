import sys
from parser import parse_files

from scipy.spatial import cKDTree

THRESHOLD = 5

def create_cKDTree(neurites):
    return cKDTree(neurites, copy_data=True)

if __name__ == '__main__':
    # create a list of our internal representation
    neurons = [ list(n.neurites()) for n in parse_files(sys.argv[1:]) ]

    print(len(neurons), 'files parsed')

    # create a list of kd-trees
    trees = [ create_cKDTree(neurites) for neurites in neurons ]

    # use the kd-trees to find all the pairs at most THRESHOLD apart
    pairs = []
    for i, source in enumerate(trees):
        for j, target in enumerate(trees):
            if i == j: continue

            # around every point in source
            # center a sphere with radius THRESHOLD,
            # find the points in target which fall inside this sphere
            res = source.query_ball_tree(target, THRESHOLD)
            pairs.push(i, j, res)

    print('Found all pairs')

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

    print(len(valid_pairs), 'valid pairs found')
    for n1, n2 in sorted(list(valid_pairs), key=lambda n: (n[0].filename, n[0].id)):
        # a lot of these will be very similar and we sould try to group them together
        # or perhaps select only the closest pair
        print(
            n1.id, n2.id,
            n1.x, n2.x,
            n1.y, n2.y,
            n1.z, n2.z,
            sep='\t')
