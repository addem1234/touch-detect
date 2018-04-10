import sys
from kd import sqd
from parser import parse_files, create_big_tree

THRESHOLD = 10

def has_neighbors(node, name):
    if not node:
        return False

    this_name = node.dom_elt.filename

    if this_name != name:
        return True
    else:
        return has_neighbors(node.left, this_name) or has_neighbors(node.right, this_name)

def find_connected(node):
    if not node:
        return []

    if node.left and node.right:
        distance_squared = sqd(
            node.left.dom_elt.coords,
            node.right.dom_elt.coords
        )
        if has_neighbors(node, node.dom_elt.filename) and distance_squared < THRESHOLD:
            print(distance_squared)
            print(node)

            return [(distance_squared, node)]

    return find_connected(node.left) + find_connected(node.right)


if __name__ == '__main__':
    neurons = parse_files(sys.argv[1:])
    print(len(neurons), 'files parsed')
    tree = create_big_tree(neurons)
    print('tree created')

    results = find_connected(tree.n)

    print(len(results), 'probable neighbors found')


