import sys

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

from parser import parse

def plot(xs, ys, zs, rs):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(xs, ys, zs, s=rs)

    plt.show()

if __name__ == '__main__':
    xs, ys, zs, rs = [], [], [], []
    for filename in sys.argv[1:]:
        n, tree = parse(filename)

        x, y, z, r = zip(*[ (*n.data.coords, n.data.data.r) for n in tree.inorder() ])

        xs.extend(x)
        ys.extend(y)
        zs.extend(z)
        rs.extend(r)

    print(len(xs), len(ys), len(zs), len(rs))
    plot(xs, ys, zs, rs)
