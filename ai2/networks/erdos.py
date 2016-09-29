#!/usr/bin/env python2

import numpy as np

from random import random
from node import Node

PREF = "ERDOS :: "

def main(ax, NODE_COUNT=50000, Z=2):
    TOTAL_EDGES = NODE_COUNT * Z / 2

    nodes = [Node(i) for i in range(NODE_COUNT)]
    nodes[0].add_node(nodes[1])
    nodes[1].add_node(nodes[0])

    # Done initializing nodes

    for i in range(TOTAL_EDGES):
        i1 = int(random()*NODE_COUNT)
        i2 = int(random()*NODE_COUNT)
        while i2 == i1: i2 = int(random()*NODE_COUNT)
        nodes[i1].add_node(nodes[i2])
        nodes[i2].add_node(nodes[i1])
    tot = np.sum([n.deg for n in nodes])

    # Gather data

    ZM = 0
    d = {i:0 for i in range(NODE_COUNT)}
    for n in nodes:
        # deg = len(n.nodes)
        deg = n.deg
        d[deg]+=1
        if deg > ZM: ZM = deg
    print(PREF + "Maximum degree: {}".format(ZM))
    ZM += 1

    ys = []
    for i in range(ZM):
        ys.append(float(d[i]))

    ind = np.arange(ZM)
    width = .35

    rects = ax.scatter(ind, ys, color='r')

    ax.set_ylabel('Nodes')
    ax.set_ylim(bottom=0.)
    ax.set_xlabel('Degree')

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, a = plt.subplots()
    main(a)
    plt.show()
