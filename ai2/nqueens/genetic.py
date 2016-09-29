#!/usr/bin/env python3
import sys
import cProfile
import itertools
import random
import time
    

def main():
    global n
    n = 55

    pop = int(n)
    # hf = pop//2

    def printboard(qs,conf):
        out = "   "
        for i in range(n):
            out += str(i) + " "
        out += "\n"
        out += (2*n+4) * "-" + "\n"
        for i in range(n):
            out += str(i) + "| "
            for ind,q in enumerate(qs):
                if ord(q) != i:
                    out+=". "
                else:
                    if((ind,ord(q)) in conf):
                        out += "\x1b[0;31mQ\x1b[0m "
                    else:
                        out += "Q "
            out += "|\n"
        out += (2*n+4) * "-" + "\n  "
        for i in range(n):
            out += str(i) + " "
        print(out)
        return

    def conflicts(sqs):
        global n
        qs = [(i,ord(sqs[i])) for i in range(n)]

        # qs = ['44', '33', '41', '34', '32', '35', '42', '49', '15', '13','39', '48', '18', '11', '36', '38',   '3', '43',   '2', '54','1', '10', '16', '40', '45', '21',   '6',   '0', '23', '26','31', '50',  '7', '47',   '8', '51',   '5', '29', '20', '52','12',   '4','28', '53', '46', '22', '37', '30', '27', '25',  '14', '17', '19',  '9', '24',   '6', '21']

        # qs = [(i,int(qs[i])) for i in range(n)]

        cons = 0
        fcons = set()
        for c1,r1 in qs:
            for c2,r2 in qs:
                # if r2 == 6: print(c1, r1, c2, r2)
                if c2 == c1 and r2 == r1: continue
                if c2 == c1 or r2 == r1 or (c2-c1)**2 == (r2-r1)**2:
                    cons += 1
                    fcons.add((c2,r2))
        # print(cons)
        # asd
        return cons,fcons

    def fitness(sqs):
        return -conflicts(sqs)[0]

    queens = [chr(i) for i in range(n)]
    population = []
    for i in range(pop):
        tp = []
        avail = list(range(n))
        random.shuffle(avail)
        tp = [chr(k) for k in avail]
        population.append(tp)
            
    # population = list(itertools.permutations(queens))
    random.shuffle(population)
    sp = [list(p) for p in population[:pop]]
    pmap = {}
    smap = {}
    for p in sp:
        f = fitness(p)
        # print("{} {}".format(p,f))
        pmap[str(p)] = f
        smap[str(p)] = p
    print("Finished")

    def select(p,pm,sm):
        s = [0]
        for i,n in enumerate(p):
            s.append(s[i]+(-pm[str(n)])**3)
        # print(s)
        a = s[len(p)]*random.random()
        b = s[len(p)]*random.random()
        c = 0
        d = 0
        for i,si in enumerate(s):
            if a < si and c < 0:
                c = i
            if b < si and d < 0:
                d = i
        # print(a,b)
        return sm[p[c]],sm[p[d]]

    def old_mutate(z):
        p = int(n*random.random())
        c = chr(int(n*random.random()))
        return z[:p] + c + z[p+1:]

    def mutate(z):
        p = int((n-1)*random.random())
        c = int((n-1)*random.random())
        # z[p],z[c] = z[c],z[p]
        if p>c:
            p,c = c,p
        # print("1: {} {}".format(z,z.__class__))
        z2 = z[:p]
        z2 += z[c]
        z2 += z[p+1:c]
        z2 += z[p]
        z2 += z[c+1:]
        # print("2: {}".format(z2))
        # print(z)
        return z2

    def cross(x,y):
        """
        r = random.random()*100
        if r < 2.5: pivot = hf-2
        elif r < 15: pivot = hf-1
        elif r < 85: pivot = hf
        elif r < 97.5: pivot = hf+1
        else: pivot = hf+2
        """
        pivot = int(random.random()*n)
        # pivot = 0
        # print(x,y,pivot)
        z = x[:pivot]
        sp = set(z)
        for id,i in enumerate(y[pivot:]):
            if i in sp:
                z.append(y[n-id])
            else:
                z.append(i)
        # print(z)
        if random.random() < .3: 
            z = mutate(z)
            # z = old_mutate(z)
        return z

    def replace(l,m,m2,z):
        k = min(m,key=lambda y:m[y])
        md = m[k]
        f = fitness(z)
        if f > md:
            print("MIN: {} {}".format(f,md))
            if f == 0:
                print("Time: {}".format(time.time() - st))
                print("Board: " + str([str(ord(zi)) for zi in z]))
                print("Fitness: {}".format(f))
                print("Size: {}".format(n))
                print("Iterations: {}".format(iterations))
                return True
            del m[str(k)]
            del m2[str(k)]
            m[str(z)] = f
            m2[str(z)] = z
            # print(f)
            # print(k)
            # print(l)
            """
            l.remove(k)
            l.append(z)
            """
        return False
    st = time.time()
    iterations = 0
    while True:
        iterations += 1
        sp = sorted(list(pmap.keys()))
        x,y = select(sp,pmap,smap)
        # print(x,y)
        z = cross(x,y)
        while str(z) in sp:
            z = cross(x,y)
        b = replace(sp,pmap,smap,z)
        if b: return
        # print("{} {}".format(z,fitness(z)))
        for i in pmap:
            # print(i,pmap[i])
            if pmap[i] == 0:
                print("Time: {}".format(time.time() - st))
                z = i
                print("Board: " + str([str(ord(zi)) for zi in z]))
                print("Fitness: {}".format(pmap[i]))
                print("Size: {}".format(n))
                print("Iterations: {}".format(iterations))
                return i
    return
main()
# cProfile.run("main()")
