#!/usr/bin/env python3
# Name: James Houghton
# Date: 9-10-15
# Period: 3rd - Gabor

import sys,time
import urllib.request
import re

def countDiff(word1, word2):
    cnt = 0
    for i in range(6):
        if(word1[i] != word2[i]): cnt+=1
        if(cnt > 1): return -1 # Quick exit if limit exceeded
    return cnt
def allAdjacentTo(important, words):
    adj = []
    for word in words:
        if(countDiff(important,word) == 1): adj.append(word)
    return adj
def numberOfEdges(w_dict):
    visited = set()
    edges = 0
    for key in w_dict:
        visited.add(key)
        for word in w_dict[key]:
            if word not in visited: edges += 1
    return edges
def showProgress(current,total):
    sys.stdout.write ("Generating graph: "+str(float(current)/float(total)*100) +"%            \r")
    sys.stdout.flush()
def findComponents(w_dict):
    visited = set()
    print(str(visited))
    components = {}
    for word in w_dict:
        comp,visited = generateComponent(word,w_dict,visited)
        components[str(len(comp))] = comp
    print(str(len(components)))
def generateComponent(key,w_dict,visited):
    if len(w_dict[key]) == 0:
        return ([key],visited)
    else:
        component = [key if key not in visited else None]
        for val in w_dict[key]:
            if val not in visited:
                visited.add(val)
                component.append(generateComponent(val,w_dict,visited))
        return (component,visited)

words_dict = {}
link = "https://academics.tjhsst.edu/compsci/ai/web2015/words.txt"
words_b = urllib.request.urlopen(link).read().split()
words = [word.decode() for word in words_b]
old_time = time.time()
for index, word in enumerate(words):
    words_dict[word] = allAdjacentTo(word,words)
    if index%10 == 1: showProgress(index,len(words))
print ("Generating graph: 100% in "+str(time.time() - old_time)+"s")
print("Words: "+str(len(words)))
print("Edges: "+str(numberOfEdges(words_dict)))
print("Words with most neighbors: ")
print(str(findComponents(words_dict)))
if len(sys.argv) > 1:
    for word in sys.argv[1:]:
        if word in words_dict: print("Adjacent to "+word+": "+str(words_dict[word]))
        else: print("\033[91m"+word+" not found\033[0m")
