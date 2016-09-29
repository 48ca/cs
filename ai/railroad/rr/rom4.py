#!/usr/bin/env python3

import math,time,sys,cProfile
from math import pi, acos, sin, cos

heuristic_cache = {}

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
            "gcost":None,
            "hcost":None,
            "fcost":None
        }
    f.close()

def readEdges(graph,filename):
    f = open(filename,"r")
    arr = f.read().split("\n")
    for line in arr:
        n = line.split(" ")
        if(len(n) < 2): break
        tmp = heuristic(n[0],n[1],graph,True)
        print(tmp)
        graph[n[0]]["edges"][n[1]] = {
            "weight": tmp
        }
        graph[n[1]]["edges"][n[0]] = {
            "weight": tmp
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
        graph[node]['hcost'] = heuristic(node,end,graph)
def heuristic(start,end,graph,ignore = False):
    if start not in heuristic_cache:
        x1 = graph[start]['coords']['y'] * pi/180.0
        y1 = graph[start]['coords']['x'] * pi/180.0
        x2 = graph[end]['coords']['y'] * pi/180.0
        y2 = graph[end]['coords']['x'] * pi/180.0
        diff = abs(x2-x1)
        if(diff == 0 and y1 == y2): res = 0
        else:
            R = 3958.76
            res = acos( sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(diff)) * R
        if not ignore:
            heuristic_cache[start] = res
        else:
            return res
    return heuristic_cache[start]

def findLowest(q,graph):
    mc = 0xFFFFFFFFFF
    mindex = 0
    lowest = []
    for index,n in enumerate(q):
        node = graph[n['node']]
        if node["fcost"] and node["fcost"] <= mc:
            if mc == node['fcost']:
                lowest.append((node,index))
            else:
                mc = node["fcost"]
                lowest = [(node,index)]
    minh = 0xFFFFFFFFFF
    for node in lowest:
        if(node[0]['hcost'] < minh):
            minh = node[0]['hcost']
            mindex = node[1]
    # print(str(mindex) + "\t" + str(graph[q[mindex]["node"]]["fcost"]) + "\t" + str(graph[q[0]["node"]]["fcost"]))
    # print(str((graph[q[mindex]["node"]]["fcost"]) > (graph[q[0]["node"]]["fcost"])))
    return mindex

def updateEdges(graph,cost,end,vertex,visited,count):
    to_update = []
    for v in graph[vertex]['edges']:
        graph[v]['hcost'] = heuristic(v,end,graph)
        new_cost = graph[v]['hcost'] + cost
        if graph[v]['gcost']!=None and graph[v]['gcost'] > new_cost:
            graph[v]['gcost'] = new_cost
            graph[v]['fcost'] = new_cost + heuristic(v,end,graph)
            to_update.append(v)
    for v in to_update:
        if v not in visited:
            count += 1
            count += updateEdges(graph,graph[vertex]['edges'][v]['weight'],end,v,visited,count)
    return count

def astar(start, end, graph):
    q = [{"node":start,"cost":0,"path":[]}]
    checked = 0
    cost_so_far = {start:0}
    max_q = 1
    heuristic_cache = {start:heuristic(start,end,graph)}
    visited = set() # re-add visited
    graph[start]["gcost"] = 0
    while q:
        if len(q) > max_q:
            max_q = len(q)
        curr = q.pop(findLowest(q,graph))
        # curr = q.pop(0)
        v = curr['node']
        visited.add(v)
        c = curr['cost']
        path = curr['path']
        checked += 1
        updateEdges(graph,c,end,v,visited,0)
        if v == end:
            return path + [end],max_q,c,checked
        path = path + [v]
        for n in graph[v]["edges"]:
            if n in visited: continue
            # if graph[n]['gcost'] > c:
            new_cost = cost_so_far[v] + graph[v]['edges'][n]['weight']
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                graph[n]['fcost'] = new_cost + heuristic(n,end,graph)
                graph[n]['gcost'] = new_cost
                q.append({'node':n,'cost':new_cost,'path':path})
    return [],max_q,0,checked
read_time = time.time()
rr = {}
readNodes(rr,"romNodes.txt")
readEdges(rr,"romEdges.txt")
names = readNames(rr,"romFullNames.txt")
read_time = time.time() - read_time

def main():

    if len(sys.argv) > 2:
        start = names[sys.argv[1]] if sys.argv[1] in names else sys.argv[1]
        end = names[sys.argv[2]] if sys.argv[2] in names else sys.argv[2]
        if(start not in rr or end not in rr):
            print("Cannot find", sys.argv[1] + " (" + start + ")" , "or", sys.argv[2] + " (" + end + ")")
            return 
        # addHCost(rr,end)
        start_time = time.time()
        res = astar(start,end,rr)


        if(len(res[0]) > 0):
            sys.stdout.write("Cost: [0")
            for index in range(len(res[0])-1):
                sys.stdout.write(", " + str(rr[res[0][index]]['edges'][res[0][index+1]]['weight']))
            print("]")

        for index,n in enumerate(res[0]):
            if rr[n]['name']:
                res[0][index] = "\033[94m" + rr[n]['name'] + "\033[0m"
        if(len(res[0]) > 0):
            sys.stdout.write("Path: [" + str(res[0][0]))
            for n in res[0][1:]:
                sys.stdout.write(", " + str(n))
            print("]")
        # print("Path: "+str(res[0]))
        print("Distance: "+str(len(res[0])))
        print("Cost: "+str(res[2]))
        print("Max queue: "+str(res[1]))
        print("Read time: "+str(read_time))
        print("Time: "+str(time.time() - start_time))
    else:
        print("len(sys.argv) < 2")
# cProfile.run('main()')
main()
