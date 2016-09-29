#!/usr/bin/env python2

import numpy as np
import sys

from diameter import hdiam

PREF = "BARABASI-ALBERT :: "

def main(NODE_COUNT=50000,Z=2):
    degs = np.zeros(NODE_COUNT)
    nodes = [[] for i in range(NODE_COUNT)]
    for i in range(3):
        degs[i] = 2
    nodes[0] = [1,2]
    nodes[1] = [0,2]
    nodes[2] = [0,1]

    # Done initializing nodes

    for n in np.arange(3,NODE_COUNT):
        # ra = [nodes[int(random()*NODE_COUNT)] for i in range(Z)]
        inds = np.random.choice(NODE_COUNT, Z, p=(degs/np.sum(degs)))
        nodes[inds[0]].append(int(inds[1]))
        nodes[inds[1]].append(int(inds[0]))
        for i in inds:
            degs[i] += 1
        nodes[n] += [int(inds[1]),int(inds[0])]
        degs[n] += Z
        sys.stdout.write(PREF + "Connecting: {:.2f}%           \r".format(100.0*n/NODE_COUNT))
        sys.stdout.flush()
    print(PREF + "Done                     ")

    # Gather data

    ZM = 0
    d = np.zeros(NODE_COUNT)
    for n in np.arange(NODE_COUNT):
        degi = degs[n]
        d[degi]+=1
        if degi > ZM: ZM = degi
    # print(PREF + "Maximum degree: {}".format(ZM))
    ZM += 1
    for i in np.arange(2,ZM):
        if d[i] > 0:
            print("{},{}".format(np.log(i),np.log(d[i])))
    for i in np.arange(ZM):
        print("{},{}".format(i,d[i]))

    hdiam({i:nodes[i] for i in range(NODE_COUNT)})

main(40000)
