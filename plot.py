import sys
from random import choice

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np

from parser import parse_files

def plot(trees):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for x, y, z, r, c in trees:
        ax.scatter(x, y, z, s=r, c=c)

    plt.tight_layout()
    #plt.savefig('plot.png', bbox_inches='tight', dpi=500)
    plt.show()

if __name__ == '__main__':
    trees = []
    for neuron in parse_files(sys.argv[1:]):
        x, y, z, r = zip(*[ (*n.coords, n.r) for n in neuron.neurites() ])
        color = choice(list(matplotlib.colors.CSS4_COLORS.keys()))
        trees.append((x, y, z, r, color))

    print('plotting', len(trees), 'trees')
    plot(trees)
