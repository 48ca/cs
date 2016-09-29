#!/usr/bin/env python3

import math,time,sys

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
    f = open(filename,"r")
    arr = f.read().split("\n")
    for line in arr:
        if(len(line) > 0):
            graph[line[0]]["name"] = line
    f.close()

def hCost(start,end,graph):
    return math.sqrt(
        (float(graph[end]['coords']["x"]) - graph[start]['coords']["x"])**2 +
        (float(graph[end]['coords']["y"]) - graph[start]["coords"]['y'])**2
    )

def findLowest(graph,end):
    retNode = None
    d = 999999999
    for node in graph:
        if graph[node]["gcost"] == None: continue
        fcost = hCost(node,end,graph) + graph[node]["gcost"]
        if fcost < d:
            d = fcost
            retNode = node
    return retNode

def indexOf(node,q):
    for index, n in enumerate(q):
        if q[index] == n:
            return index

def updateEdges(graph, node):
    count = 0
    for n in graph[node]["edges"]:
        d = hCost(n,node,graph)
        if(graph[n]["gcost"] == None or graph[n]["gcost"] > d):
            graph[n]["gcost"] = d
            count += 1
    return count

def astar(start, end, graph):
    visited = set()
    q = [(0,start,[])]
    checked = 0
    max_q = 1
    graph[start]["gcost"] = 0
    while q:
        if len(q) > max_q:
            max_q = len(q)
        (cost, v, path) = q.pop(indexOf(findLowest(graph,end),q))
        checked += 1
        if v not in visited:
            visited.add(v)
            if v == end:
                return path + [end],max_q,cost,checked
            path = path + [v]
            for n in graph[v]["edges"]:
                updateEdges(graph,v)
                if n not in visited:
                    q.append((cost+graph[v]["edges"][n]["weight"],n,path))
    return [],max_q,0,checked



rr = {}
readNodes(rr,"romNodes.txt")
readEdges(rr,"romEdges.txt")
readNames(rr,"romFullNames.txt")

start_time = time.time()

if len(sys.argv) > 2:
    res = astar(sys.argv[1],sys.argv[2],rr)
    print(str(res))
    print(str(time.time() - start_time))
else:
    print("len(sys.argv) < 2")
