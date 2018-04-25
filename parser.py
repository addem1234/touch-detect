import sys, os, os.path, math
from itertools import chain
import numpy as np

class Neurite(object):
    __slots__ = ('id', 'type', 'x', 'y', 'z', 'r', 'parent', 'children', 'name')

    def __init__(self, id, type, x, y, z, r, parent, children, name):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.parent = parent
        self.children = children
        self.name = name

    @property
    def coords(self):
        return (self.x, self.y, self.z)


    @property
    def type_s(self):
        types = {
            0: 'undefined',
            1: 'soma',
            2: 'axon',
            3: 'dendrite',
            4: 'apical dendrite',
        }

        return types.get(self.type, 'custom')

    def __repr__(self):
        #return 'Neurite(id={id})'.format(**self._asdict())
        # A custom __repr__ so that we dont get infinete recursion because of both parent and children
        slots = {k: self.__getattribute__(k) for k in self.__slots__}
        slots['type'] = self.type_s
        return 'Neurite(id={id}, type={type}, x={x}, y={y}, z={z}, name={name})'.format(**slots)

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, i):
        return self.coords[i]

    def __iter__(self):
        for i in range(len(self.coords)):
            yield self.coords[i]

    #__iter__ from https://stackoverflow.com/questions/6914803/python-iterator-through-tree-with-list-of-children
    # user wberry 2018-03-25
    def neurites(self):
        yield self
        for v in chain(*map(Neurite.neurites, self.children)):
          yield v

    def transform(self, transform):
        self.x, self.y, self.z = np.dot(transform, self.coords)


    def translate(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z


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
                children=[],
                name=filename
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
