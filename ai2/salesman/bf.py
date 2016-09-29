#!/usr/bin/env python3

import sys

def readdata():
    raw = open("mdata.txt","r").read().split("\n")
    n = int(raw[0])
    ret = {}
    for l1,d1 in enumerate(raw[1:]):
        if(d1 == ""): continue
        ret[l1] = {}
        d1 = d1.split(" ")
        for l2,d2 in enumerate(raw[1:]):
            if(d2 == ""): continue
            if l1 == l2: continue
            d2 = d2.split(" ")
            ret[l1][l2] = ((float(d1[0])-float(d2[0]))**2 + (float(d1[1])-float(d2[1]))**2)**.5
    return ret,n

def dist(l,d,n,dep):
    td = 0
    for i in range(dep-1):
        td += d[int(l[i])][int(l[i+1])]
    return td
        
global mind, minr
mind = float('inf')
minr = []

def findlowest(l,d,c,n,dep):
    global mind
    di = dist(l,d,n,dep)
    if di > mind: return
    for ci in c:
        findlowest(l + [ci],d,c - {ci},n,dep+1)
    if not c:
        if di < mind:
            mind = di
            minr = l
            print("{} : {}".format(l,mind))
def first():
    d,n = readdata()
    for i in range(0,n):
        findlowest([i],d,set(range(0,n)) - {i},n,1)
        print(i)

def main():
    first()
    return
main()
