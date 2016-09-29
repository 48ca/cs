#!/usr/bin/env python2

import numpy as np
import sys

from random import random
from node import Node, EPSILON

PREF = "BARABASI-ALBERT :: "

def main(ax, NODE_COUNT=50000,Z=2):
    nodes = [Node(i) for i in range(NODE_COUNT)]

    degs = np.zeros(NODE_COUNT)
    for i in range(3):
        for j in range(3): # Node does overlap detection
            nodes[i].add_node(nodes[j])
        degs[i] = nodes[i].deg

    # Done initializing nodes

    for n in nodes:
        # ra = [nodes[int(random()*NODE_COUNT)] for i in range(Z)]
        rai = np.random.choice(NODE_COUNT, Z, p=(degs/np.sum(degs)))
        ra = [nodes[i] for i in rai]
        n.add_nodes(ra)
        for nta in ra:
            nta.add_node(n)
        degs[n.id] = n.deg
        sys.stdout.write(PREF + "Connecting: {:.2f}%           \r".format(100.0*n.id/NODE_COUNT))
        sys.stdout.flush()
    print(PREF + "Done                     ")

    # Gather data

    tot = np.sum(degs)

    ZM = 0
    d = {i:0 for i in range(NODE_COUNT)}
    for n in nodes:
        deg = len(n.nodes)
        d[deg]+=1
        if deg > ZM: ZM = deg
    print(PREF + "Maximum degree: {}".format(ZM))
    ZM += 1

    ind = np.arange(ZM)
    ys = []
    dont_use = set()
    for i in range(ZM):
        tmp = float(d[i])
        if tmp < EPSILON: dont_use.add(i)
        else: ys.append(tmp)

    ind = list(set(range(ZM)) - dont_use)
    # ind = np.log(np.array(ind))
    ys = np.log(np.array(ys))

    # ax.set_yscale("log", nonposy='clip')
    # ax.set_xscale("log", nonposy='clip')
    points = ax.scatter(ind, ys, color='r')

    ax.set_ylabel('Nodes')
    ax.set_xlabel('Degree')

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, a = plt.subplots()
    main(a,50000)
    plt.show()
