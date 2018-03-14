import sys
from collections import namedtuple

class Neurite(namedtuple('Neurite', ('id', 'type', 'x', 'y', 'z', 'r', 'parent', 'children'))):

    @property
    def position(self):
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
        # A custom __repr__ so that we dont get infinete recursion because of both parent and children
        return 'Neurite(id={id}, type={type}, x={x}, y={y}, z={z}, children={children})'.format(**self._asdict())

def main(filename):
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


if __name__ == '__main__':
    n = main(sys.argv[1])
    print(n)
