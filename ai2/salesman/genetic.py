#!/usr/bin/env python3

from multiprocessing import Pool
import sys, time, random, itertools

PROFILE = False
CV2 = False
THREADING = False
PRINT_GENERATIONS = False

POP_FACTOR = 1
OVERRIDE_POP = 10

if CV2:
    import cv2
    import numpy as np

n = 0
pop = 0
wait_key_delay = 300

width = 500
height = 500
maxlat = 0
minlat = float('inf')
maxlon = 0
minlon = float('inf')
latw = 0
lonw = 0

attempts = 0

def readdata():
    raw = open("tsp0734.txt","r").read().split("\n")
    # raw = open("data.txt","r").read().split("\n")
    global n, pop
    global maxlat,minlat,maxlon,minlon,latw,lonw
    n = int(raw[0])
    pop = int(n * POP_FACTOR)
    if OVERRIDE_POP: pop = OVERRIDE_POP
    ret = {}
    for l1,d1 in enumerate(raw[1:]):
        if(d1 == ""): continue
        ret[l1] = {}
        d1 = d1.split(" ")
        ret[l1]['data'] = [float(d) for d in d1]
        maxlat = max(float(d1[0]),maxlat)
        minlat = min(float(d1[0]),minlat)
        maxlon = max(float(d1[1]),maxlon)
        minlon = min(float(d1[1]),minlon)
        for l2,d2 in enumerate(raw[1:]):
            if(d2 == ""): continue
            if l1 == l2: continue
            d2 = d2.split(" ")
            ret[l1][l2] = ((float(d1[0])-float(d2[0]))**2 + (float(d1[1])-float(d2[1]))**2)**.5
    maxlat += 100
    minlat -= 100
    maxlon += 100
    minlon -= 100
    latw = maxlat - minlat
    lonw = maxlon - minlon
    return ret

def dist(l,d):
    td = 0
    for i in range(n-1):
        td += d[int(l[i])][int(l[i+1])]
    td += d[l[n-1]][l[0]]
    return td

global mind, minr
mind = float('inf')
minr = []

def swap(g,i,j):
    g[i],g[j] = g[j],g[i]
    return g

def swap_and_return_dist(g,i,j,d):
    if i == j:
        return g,0
    if i > j:i,j=j,i
    g[i],g[j] = g[j],g[i]
    if j-i == 1:
        return g,d[g[i-1]][g[i]] + d[g[j]][g[j+1-n]] - d[g[i-1]][g[j]] - d[g[i]][g[j+1-n]]
    if i == 0 and j == n-1:
        return g,d[g[0]][g[1]]+d[g[j-1]][g[j]]-d[g[j-1]][g[0]]-d[g[j]][g[1]]
    return g,d[g[i-1]][g[i]] + d[g[j]][g[j+1-n]] - d[g[i-1]][g[j]] - d[g[i]][g[j+1-n]] + d[g[i]][g[i+1-n]] + d[g[j-1]][g[j]] - d[g[i]][g[j-1]] - d[g[j]][g[i+1-n]]

def display(mg,d,thd,num,mind,name="child"):
    onedex = mg.index(0)
    tmg = [mg[onedex-i]+1 for i in range(len(mg))]
    if tmg[-1] < tmg[1]:
        rmg = mg[::-1]
        onedex = rmg.index(0)
        tmg = [rmg[onedex-i]+1 for i in range(len(mg))]
    if name=="best": print("New best: {} {}".format(mind,tmg))
    if CV2:
        img = np.zeros((height,width,3), np.uint8)
        img[:,:] = (255,255,255)
        for i in range(-1,n-1):
            w1 = int(width * (d[mg[i]]['data'][0] - minlat) / latw)
            h1 = int(height * (d[mg[i]]['data'][1] - minlon) / lonw)
            w2 = int(width * (d[mg[i+1]]['data'][0] - minlat) / latw)
            h2 = int(height * (d[mg[i+1]]['data'][1] - minlon) / lonw)
            cv2.line(img,(h1,w1),(h2,w2),(255,0,0),1)
        for i in range(-1,n-1): # Prevent line over circle
            w1 = int(width * (d[mg[i]]['data'][0] - minlat) / latw)
            h1 = int(height * (d[mg[i]]['data'][1] - minlon) / lonw)
            cv2.circle(img,(h1,w1),2,(0,0,0), -1)
        cv2.putText(img,"Distance {} Attempts: {}".format(mind,attempts),(20,20),cv2.FONT_HERSHEY_PLAIN,1,0)
        cv2.imshow(name,img)
        cv2.waitKey(wait_key_delay) # 500
        cv2.imwrite(name+".png",img)

def select(pmap,sp):
    sk = [0]
    for i,e in enumerate(sp):
        sk.append(1.0/pmap[e] + sk[i])
    ma = sk[-1]
    a = random.random()*ma
    b = random.random()*ma
    c = 0
    d = 0
    c1 = False
    c2 = False
    for i,si in enumerate(sk):
        if a < si and not c1:
            c = i
            c1 = True
        elif b < si and not c2:
            d = i
            c2 = True
        if c1 and c2:
            break
    return sp[c-1],sp[d-1]

def cross(x,y):
    pivot = int(random.random()*n)
    p1 = x[:pivot]
    p2 = y[pivot:]
    # print(len(set(range(n)) - set(x)))
    # print(len(set(range(n)) - set(y)))
    ch = list(p1 + p2)
    toadd = set(range(n)) - set(ch)
    # print(toadd)
    # print(len(toadd))
    seen = set()
    torem = [i for i,x in enumerate(ch) if x in seen or seen.add(x)]
    # print(torem)
    for i in y:
        if not toadd: break
        if i in toadd:
            ch[torem[0]] = i
            toadd -= {i}
            del torem[0]
        # print(i)
    # print()
    # print(len(set(range(n)) - set(ch)))
    ch.reverse()
    return tuple(ch)

def mutate(x,d=None):
    z = int(random.random()*n)
    y = int(random.random()*n)
    while y == z:
        y = int(random.random()*n)
    x[z],x[y] = x[y],x[z]
     #x,dis = swap_and_return_dist(x,y,z,d)
    return tuple(x)# ,dis

def untangle(g,i,j,d):
    ng = g[:i] + g[i:j][::-1] + g[j:]
    ddist = d[ng[i-1]][ng[i]] + d[ng[j-1]][ng[j]] - d[g[i-1]][g[i]] - d[g[j-1]][g[j]]
    return ng, ddist

def untangleneg(g,i,j,d):
    ng = [g[i]] + g[:j][::-1] + g[j:i]
    ddist = d[ng[i-1]][ng[i]] + d[ng[j-1]][ng[j]] - d[g[i-1]][g[i]] - d[g[j-1]][g[j]]
    return ng, ddist

def only_one_untangle(g,dist,d):
    md = dist
    mg = g
    """
    for j in range(1,n-1):
        ng,nd = untangleneg(g,-1,j,d)
        if nd+dist < md:
            md = nd+dist
            mg = ng
    """
    for i in range(1,n-2):
        for j in range(i+1,n-1):
            ng,nd = untangle(g,i,j,d)
            if nd+dist < md:
                md = nd+dist
                mg = ng
    return mg,md

def runtangle(g,dist,d):
    md = dist
    mg = g
    for k in range(5000):
        i = int(random.random() * n)
        j = int(random.random() * n)
        if i>j:i,j=j,i
        ng,nd = untangle(g,i,j,d)
        if nd+dist < md:
            md = nd+dist
            mg = ng
    return mg,md

def fully_untangle(graph,d):
    dis = dist(graph,d)
    ng, nd = only_one_untangle(graph,0,d)
    dis += nd
    while nd < -0.00000001:
        # ng, nd = only_one_untangle(ng,0,d)
        ng, nd = runtangle(ng,0,d)
        # print(ng)
        dis += nd
    return ng,dis

def main(i):
    print("Initializing...")
    st = time.time()
    d = readdata()
    # print(d[0][1])
    population = []
    for i in range(pop):
        avail = list(range(n))
        random.shuffle(avail)
        while avail in population:
            random.shuffle(avail)
        avail,nd = fully_untangle(avail,d)
        print("({:02d}/{:02d}) {}".format(i+1,pop,nd))
        population.append(avail)
    child_population = population[:]
    graph = list(range(n))
    print(graph)
    # graph = only_one_untangle(graph,dist(graph,d),d)
    mg = graph
    mind = dist(mg,d)
    display(mg,d,i,0,mind,"best")
    display(mg,d,i,0,mind,"child")
    num = 0
    global CV2
    try:
        print("Finished initialization in {} seconds".format(time.time()-st))
        print("Starting computation")
        print(population)
        st = time.time()
        # display(mg,d,i,num,mind,"best") -- display calls
        # display(mg,d,i,num,mind,"child") -- display calls
        generations = 0
        epochs = 0
        while True:
            generations += 1
            population = child_population
            child_population = []
            pmap = {}
            for p in population:
                pmap[tuple(p)] = dist(p,d)
            sk = sorted(list(pmap.keys()),key=lambda d: pmap[d])
            if not PRINT_GENERATIONS and generations % 10 == 0:
                epochs += 1
                print("Epoch      {0:06d} : {1:7.5f} {2:7.5f}".format(epochs,pmap[sk[0]],pmap[sk[-1]]))
            else:
                print("Generation {0:06d} : {1:5.5f} {2:5.5f}".format(generations,pmap[sk[0]],pmap[sk[-1]]))
            if pmap[sk[0]] < mind:
                mind = pmap[sk[0]]
                mg = sk[0]
            # print(pmap[tuple(sk[0])], pmap[tuple(sk[-1])])
            while len(child_population) < pop:
                x,y = select(pmap,sk)
                while x == y:
                    x,y = select(pmap,sk)
                z = cross(x,y)
                # """
                io = 0
                while z in child_population:
                    io += 1
                    z = cross(x,y)
                    if io > 1000:
                        print(x)
                        print(y)
                        # print(sk)
                        return
                if random.random() < .3:
                    # z,nd = mutate(list(z),d) # nd is delta dist
                    z = mutate(list(z)) # nd is delta dist
                """
                while z in child_population:
                    z = cross(x,y)
                """
                # print(x,y)
                nd = dist(z,d)
                if(nd) < pmap[sk[-1]]:
                    # print(nd,pmap[sk[-1]])
                    child_population.append(z)
                    """
                    del pmap[sk[-1]]
                    pmap[z] = nd
                    sk = sorted(list(pmap.keys()),key=lambda d: pmap[d])
                    """

    except KeyboardInterrupt:
        print("EXITING: {} {} {} {}".format(mind,i,num,mg))
        print("{}".format(time.time() - st))
    return

if PROFILE:
    import cProfile
    cProfile.run('main(0)')
    sys.exit()

if CV2 or not THREADING: main(0)
else:
    pool = Pool(3)
    try:
        pool.map(main,range(3))
    except:
        pool.terminate()
        pool.join()
