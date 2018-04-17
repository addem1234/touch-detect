import sys, os, os.path, math
from itertools import chain
import numpy as np

class Neurite(object):
    __slots__ = ('id', 'type', 'x', 'y', 'z', 'r', 'parent', 'children', 'filename')

    def __init__(self, id, type, x, y, z, r, parent, children, filename):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.parent = parent
        self.children = children
        self.filename = filename

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
        #return 'Neurite(id={id})'.format(**self._asdict())
        # A custom __repr__ so that we dont get infinete recursion because of both parent and children
        slots = {k: self.__getattribute__(k) for k in self.__slots__}
        slots['type'] = self.type_string
        return 'Neurite(id={id}, type={type}, x={x}, y={y}, z={z}, filename={filename})'.format(**slots)

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

    def apply_transform(axis, theta):
        self.x, self.y, self.z = np.dot(rotation_matrix(axis, theta), self.coords)
        for child in self.children:
            child.apply_transform(transform)

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
                filename=filename
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


def rotation_matrix(axis, theta):
    """
    Source: https://stackoverflow.com/questions/6802577/rotation-of-3d-vector?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    Author: unutbu
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

