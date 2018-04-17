import sys
from collections import defaultdict
from copy import deepcopy
from kd import sqd, find_nearest, T3
from parser import parse_files, create_big_tree, create_tree

THRESHOLD = 5

def has_neighbors(node, name):
    if not node:
        return False

    this_name = node.dom_elt.filename

    if this_name != name:
        return True
    else:
        return has_neighbors(node.left, this_name) or has_neighbors(node.right, this_name)

def child_bounds(kd, hr):
    s = kd.split
    pivot = kd.dom_elt
    left_hr = deepcopy(hr)
    right_hr = deepcopy(hr)
    left_hr.max[s] = pivot[s]
    right_hr.min[s] = pivot[s]

    return left_hr, right_hr

def something(kd, hr):
    res = []

    if not kd:
        return res

    if sqd(hr.min, hr.max) < THRESHOLD**2 and has_neighbors(kd, kd.dom_elt.filename):
        res = [(sqd(hr.min, hr.max), kd)]

    left_hr, right_hr = child_bounds(kd, hr)

    return res + something(kd.left, left_hr) + something(kd.right, right_hr)

def quick(node):
    if not node:
        return []

    if not has_neighbors(node, node.dom_elt.filename):
        return []

    if node.left and node.right:
        distance_squared = sqd(
            node.left.dom_elt.coords,
            node.right.dom_elt.coords)
        if distance_squared < THRESHOLD**2:
            return [(distance_squared, node)]

    return quick(node.left) + quick(node.right)

def naive(neurons, trees):
    neighbors = defaultdict(dict)
    ni = len(neurons)
    nj = len(trees)
    for i, neuron in enumerate(neurons):
        nk = len(list(neuron.neurites()))
        # print('searching around', nk, 'points in tree', i)
        # Iterate through every point in the neuron
        # If this could be binary searched somehow?
        points_searched = 0
        for k, neurite in enumerate(neuron.neurites()):

            if neurite in neighbors:
                continue

            min_sqd = float('inf') # closest distance squared
            closest_neurite = None

            # Iterate through trees since we have separate kd-trees per neuron
            for j, tree in enumerate(trees):
                # Dont search yourself
                if i == j: continue

                print('\rtree: {}/{}, point: {}/{}, opposing tree: {}/{}'.format(i + 1, ni, k + 1, nk, j + 1, nj), end='')

                n = find_nearest(1, tree, neurite)

                if n.dist_sqd < min_sqd:
                    min_sqd = n.dist_sqd
                    closest_neurite = n.nearest

            if not (closest_neurite) in neighbors and min_sqd < THRESHOLD**2:
                neighbors[neurite] = (closest_neurite, min_sqd)
                neighbors[closest_neurite] = (neurite, min_sqd)

            points_searched += 1

        print() # to add an end to the self replacing line @83 aka print('\r...', end='')
        print('searched', points_searched, 'points in tree', i)

    # n2[0] is a neuron, n2[1] is distance, see line 93 aka neighbors[closest_neurite] = (neurite, min_sqd)
    # hash magic to deduplicate list, result is list of type [(n1, n2, d)]
    return {(hash(n1) + hash(n2[0])): (n1, n2[0], n2[1]) for n1, n2 in neighbors.items() }.values()

def aslist(kd):
    if not kd:
        return []

    return [kd.dom_elt] + aslist(kd.left) + aslist(kd.right)

def getname(kd):
    return set([n.filename for n in aslist(kd)])

def dedup(nodess):
    pass

if __name__ == '__main__':
    neurons = parse_files(sys.argv[1:])
    print(len(neurons), 'files parsed')

    # tree = create_big_tree(neurons)
    # print('big tree created')
    # results = quick(tree.n)
    # print(len(results), 'probable neighbors found')
    # resultnodelists = [aslist(r[1]) for r in results]
    # resultnames = [getname(x[1]) for x in results]

    # things = something(tree.n, tree.bounds)
    # print(len(things), 'things found')
    # thingnodelists = [aslist(r[1]) for r in things]
    # thingnames = [getname(x[1]) for x in things]

    trees = [create_tree(list(neuron.neurites())) for neuron in neurons]
    print(len(trees), 'small trees created')
    naiveresults = naive(neurons, trees)
    print(len(naiveresults), 'actual neighbors found')
    for n1, n2, d in sorted(naiveresults, key=lambda n: (n[0].idname, n[0].id)):
        print(
            n1.idname, n2.idname,
            n1.id, n2.id,
            d,
            n1.x, n2.x,
            n1.y, n2.y,
            n1.z, n2.z,
            sep='\t')

