#!/usr/bin/env python3

import math,time,sys,cProfile

def readNodes(graph,filename):
    f = open(filename,"r")
    arr = f.read().split("\n")
    for line in arr:
        n = line.split(" ")
        if(len(n) < 3): break
        graph[n[0]] = {
            "name": None,
            "edges": {},
            "coords":{"x": float(n[1]), "y": float(n[2])},
            "gcost":None
        }
    f.close()

def readEdges(graph,filename):
    f = open(filename,"r")
    arr = f.read().split("\n")
    for line in arr:
        n = line.split(" ")
        if(len(n) < 2): break
        graph[n[0]]["edges"][n[1]] = {
            "weight": math.sqrt(
                (float(graph[n[1]]['coords']["x"]) - graph[n[0]]['coords']["x"])**2 +
                (float(graph[n[1]]['coords']["y"]) - graph[n[0]]["coords"]['y'])**2
            )
        }
        graph[n[1]]["edges"][n[0]] = {
            "weight": math.sqrt(
                (float(graph[n[1]]['coords']["x"]) - graph[n[0]]['coords']["x"])**2 +
                (float(graph[n[1]]['coords']["y"]) - graph[n[0]]["coords"]['y'])**2
            )
        }
    f.close()

def readNames(graph,filename):
    names = {}
    f = open(filename,"r")
    arr = f.read().split("\n")
    for line in arr:
        comp = line.split(" ")
        if len(comp) > 1:
            graph[comp[0]]["name"] = " ".join(comp[1:])
            names[" " .join(comp[1:])] = comp[0]
    f.close()
    return names

def addHCost(graph,end):
    for node in graph:
        graph[node]['hcost'] = hCostHard(node,end,graph)

def hCostHard(start,end,graph):
    return math.sqrt(
        (float(graph[end]['coords']["x"]) - graph[start]['coords']["x"])**2 +
        (float(graph[end]['coords']["y"]) - graph[start]["coords"]['y'])**2
    )

def findLowest(q,graph):
    mc = 0xFFFFFFFFFF
    mindex = 0
    for index,n in enumerate(q):
        node = graph[n['node']]
        if node["gcost"] and node["gcost"] < mc:
            mc = node["gcost"]
            mindex = index
    return mindex


def astar(start, end, graph):
    visited = set()
    q = [{"node":start,"cost":0,"path":[]}]
    checked = 0
    max_q = 1
    graph[start]["gcost"] = 0
    while q:
        if len(q) > max_q:
            max_q = len(q)
        curr = q.pop(findLowest(q,graph))
        v = curr['node']
        c = curr['cost']
        path = curr['path']
        checked += 1
        if v not in visited:
            # updateEdges(graph,c,v)
            visited.add(v)
            if v == end:
                return path + [end],max_q,c,checked
            path = path + [v]
            for n in graph[v]["edges"]:
                if n not in visited:
                    q.append({'node':n,'cost':c+graph[v]['edges'][n]['weight'],'path':path})
    return None,max_q,checked


def main():
    rr = {}
    readNodes(rr,"romNodes.txt")
    readEdges(rr,"romEdges.txt")
    names = readNames(rr,"romFullNames.txt")

    start_time = time.time()

    if len(sys.argv) > 2:
        print(str(len(rr)))
        start = sys.argv[1] # names[sys.argv[1]]
        end = sys.argv[2]
        addHCost(rr,end)
        res = astar(start,end,rr)
        print(str(res[0]))
        print(str(len(res[0])))
        print(str(time.time() - start_time))
    else:
        print("len(sys.argv) < 2")

cProfile.run('main()')
