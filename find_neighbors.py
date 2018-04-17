import sys
from copy import deepcopy
from kd import sqd, find_nearest
from parser import parse_files, create_big_tree, create_tree

THRESHOLD = 100

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

    if sqd(hr.min, hr.max) < THRESHOLD and has_neighbors(kd, kd.dom_elt.filename):
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
        if distance_squared < THRESHOLD:
            return [(distance_squared, node)]

    return quick(node.left) + quick(node.right)

def naive(neurons, trees):
    neighbors = []
    for i, neuron in enumerate(neurons):
        print('searching around', len(list(neuron.neurites())), 'points in tree', i)
        # Iterate through every point in the neuron
        for neurite in neuron.neurites():
            #print('searching around point', neurite)

            closest_distance = float('inf')
            closest_point = None

            # Iterate through trees since we have separate kd-trees per neuron
            for j, tree in enumerate(trees):
                # Dont search yourself
                if i == j: continue
                #print('searching opposing tree', j)

                n = find_nearest(1, tree, neurite)

                if n.dist_sqd < closest_distance:
                    closest_distance = n.dist_sqd
                    closest_point = n.nearest

                if closest_distance < THRESHOLD:
                    break

            neighbors.append((neurite, closest_point, closest_distance))


    return list(map(lambda x: x[:2], filter(lambda x: x[2] < THRESHOLD, neighbors)))

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

    tree = create_big_tree(neurons)
    print('big tree created')
    results = quick(tree.n)
    print(len(results), 'probable neighbors found')
    resultnodelists = [aslist(r[1]) for r in results]
    resultnames = [getname(x[1]) for x in results]

    things = something(tree.n, tree.bounds)
    print(len(things), 'things found')
    thingnodelists = [aslist(r[1]) for r in things]
    thingnames = [getname(x[1]) for x in things]

    trees = [create_tree(list(neuron.neurites())) for neuron in neurons]
    print(len(trees), 'small trees created')
    naiveresults = naive(neurons, trees)
    print(len(naiveresults), 'actual neighbors found')
    print(naiveresults)

