import sys
from collections import namedtuple

import kdtree

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

class Item(object):
    def __init__(self, x, y, z, data):
        self.coords = (x, y, z)
        self.data = data

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]

    def __repr__(self):
        return 'Item(({}), {})'.format(self.coords, self.data)

def parse(filename):
    items = {}
    tree = kdtree.create(dimensions=3)
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

            tree.add(Item(*n.coords, n))

    tree = tree.rebalance()
    return items[1], tree


if __name__ == '__main__':
    neurons = []
    trees = []
    for filename in sys.argv[1:]:
        n, tree = parse(filename)

        neurons.append(n)
        trees.append(tree)

    print('files parsed')

    closest_points = []
    for i, tree in enumerate(trees):
        print('searching tree', i)
        for point in tree.inorder():
            closest_distance = 1e6
            closest_point = None

            # Iterate through trees since we have separate kd-trees per neuron
            for j, inner_tree in enumerate(trees):
                # Dont search yourself
                if i == j:
                    continue

                found_point, distance = inner_tree.search_nn(point.data.coords)

                if distance < closest_distance:
                    closest_distance = distance
                    closest_point = found_point

            closest_points.append((point, closest_point, closest_distance))


    print([x[2] for x in filter(lambda x: x[2] < 100, closest_points)])
