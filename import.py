import sys
from collections import namedtuple

Neurite = namedtuple('Neurite', ['id', 'type', 'x', 'y', 'z', 'r', 'parent'])

def main(filename):
    items = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue

            line = line.split()

            n = Neurite(
                int(line[0]),
                int(line[1]),
                float(line[2]),
                float(line[3]),
                float(line[4]),
                float(line[5]),
                items.get(int(line[6]), None)
            )

            items[n.id] = n

    return items


if __name__ == '__main__':
    n = main(sys.argv[1])
    print(n)
