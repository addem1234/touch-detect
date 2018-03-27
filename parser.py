import sys, os, os.path
from itertools import chain
from collections import namedtuple

from kd import DataPoint, Orthotope, KdTree, find_nearest

class Neurite(namedtuple('Neurite', ('id', 'type', 'x', 'y', 'z', 'r', 'parent', 'children'))):
    @property
    def coords(self):
        return (self.x, self.y, self.z)

    @property
    def type_string(self):
        types = {
            0: 'undefined',
            1: 'soma',
            2: 'axon',
            3: 'dendrite',
            4: 'apical dendrite',
        }

        return types.get(self.type, 'custom')

    def __repr__(self):
        return 'Neurite(id={id})'.format(**self._asdict())
        # A custom __repr__ so that we dont get infinete recursion because of both parent and children
        return 'Neurite(id={id}, type={type}, x={x}, y={y}, z={z}, children={children})'.format(**self._asdict())

    #__iter__ from https://stackoverflow.com/questions/6914803/python-iterator-through-tree-with-list-of-children
    # user wberry 2018-03-25
    def __iter__(self):
        "implement the iterator protocol"
        for v in chain(*map(iter, self.children)):
          yield v
        yield self

def parse(filename):
    items = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue

            line = line.split()

            n = Neurite(
                id=int(line[0]),
                type=int(line[1]),
                x=float(line[2]),
                y=float(line[3]),
                z=float(line[4]),
                r=float(line[5]),
                parent=items.get(int(line[6]), None),
                children=[]
            )

            if n.parent:
                n.parent.children.append(n)

            items[n.id] = n

    return items[1]

def parse_files(files):
    neurons = []
    for file in files:
        if file.endswith('.swc'):
            neurons.append(parse(file))
        elif os.path.isdir(file):
            neurons.extend(parse_files([os.path.join(file, filename) for filename in os.listdir(file)]))

    return neurons

def create_tree(neuron):
    neurites = list(neuron)

    minP = list(map(min, map(lambda n: n.coords, zip(*neurites))))
    maxP = list(map(max, map(lambda n: n.coords, zip(*neurites))))

    return KdTree(neurites, Orthotope(minP, maxP))

if __name__ == '__main__':
    neurons = parse_files(sys.argv[1:])[:2]
    print(len(neurons), 'files parsed')
    trees = [create_tree(neuron) for neuron in neurons]
    print(len(trees), 'trees created')

    closest_points = []
    for i, neuron in enumerate(neurons):
        print('searching around', len(list(neuron)), 'points in tree', i)
        for neurite in neuron:
            #print('searching around point', point)

            closest_distance = float('inf')
            closest_point = None

            # Iterate through trees since we have separate kd-trees per neuron
            for j, tree in enumerate(trees):
                # Dont search yourself
                if i == j: continue
                #print('searching opposing tree', j)

                n = find_nearest(1, tree, neurite.coords)

                if n.dist_sqd < closest_distance:
                    closest_distance = n.dist_sqd
                    closest_point = n.nearest

            closest_points.append((point, closest_point, closest_distance))


    print([x[2] for x in filter(lambda x: x[2] < 10, closest_points)])
