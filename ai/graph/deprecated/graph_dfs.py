#!/usr/bin/env python3
# Name: James Houghton
# Date: 9-10-15
# Period: 3rd - Gabor

import urllib.request,sys,time,re

def allAdjacentTo(important,words):
    adj = set()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(important)):
        for l in alphabet:
            word = important[:i] + l + important[i+1:]
            if word in words and word != important:
                adj.add(word)
    return adj
def numberOfEdges(w_dict):
    visited = set()
    edges = 0
    for key in w_dict:
        visited.add(key)
        for word in w_dict[key]:
            if word not in visited:
                edges += 1
    return edges
def showProgress(current,total):
        sys.stdout.write ("Generating graph: "+str(float(current)/float(total)*100) +"%            \r")
        sys.stdout.flush()
def findComponents(w_dict):
    visited = set()
    components = {}
    highest_key = 0
    for word in w_dict:
        if word in visited: continue
        comp,visited = generateComponent(word,w_dict,visited)
        key = len(comp)
        highest_key = key if key > highest_key else highest_key
        if key in components:
            components[key].append(comp)
        else:
            components[key] = [comp]
    return components,highest_key
def generateComponent(key,w_dict,visited):
    component = [key]
    visited.add(key)
    for val in w_dict[key]:
        if val not in visited:
            to_add,visited = generateComponent(val,w_dict,visited)
            component += to_add
    return component,visited
def dfs(key,against,w_dict,visited,path):
    visited.add(key)
    if key == against:
        return path,True
    for val in w_dict[key]:
        if val not in visited:
            p = path + [val]
            p,b = dfs(val,against,w_dict,visited,p)
            if b:
                return p,b
    return path,False
def downloadWords(link):
    sys.stdout.write("Downloading words...\r")
    sys.stdout.flush()
    return [word.decode() for word in urllib.request.urlopen(link).read().split()]
def mostNeighbors(w_dict,max_length,num):
    count = 0
    index = max_length
    words = []
    while count<num:
        if index in w_dict:
            words += [key for key in w_dict[index].keys()]
            count += len(w_dict[index].keys())
        index -= 1
    return words

words_dict = {}
words_dict_by_size = {}

link = "https://academics.tjhsst.edu/compsci/ai/web2015/words.txt"
words = downloadWords(link)
word_set = set(words)

old_time = time.time()
highest_length = 0
for index, word in enumerate(words):
    words_dict[word] = allAdjacentTo(word,word_set)
    length = len(words_dict[word])
    if length not in words_dict_by_size: words_dict_by_size[length] = {}
    highest_length = max(length,highest_length)
    words_dict_by_size[length][word] = words_dict[word]
    if index%200 == 1: showProgress(index,len(words))

print("Generating graph: 100% in "+str(time.time() - old_time)+"s")
print("Words: "+str(len(words)))
print("Edges: "+str(numberOfEdges(words_dict)))
print("Words with most neighbors: "+str(mostNeighbors(words_dict_by_size,highest_length,3)))
for i in range(highest_length+1):
    if i in words_dict_by_size:
        print("Nodes with "+str(i)+" neighbors: "+str(len(words_dict_by_size[i])))
    else:
        print("Nodes with "+str(i)+" neighbors: 0")

######### COMPONENTS #########

components,largest = findComponents(words_dict)
total_components = 0
for i in range(largest+1):
    if i in components:
        print("Components with length "+str(i)+": "+str(len(components[i])))
        total_components += len(components[i])
print("Largest component: "+str(largest)+" words long")
print("Total components: "+str(total_components))

######### DEPTH FIRST SEARCH #########

if len(sys.argv) > 2:
    print("-------------------------")
    word = sys.argv[1]
    against = sys.argv[2]
    if word in words_dict and against in words_dict:
        p,b = dfs(word,against,words_dict,set(),[word])
        if b:
            print("Path from " +against+ " to "+word+": "+str(p))
        else:
            print("No path from " +against+ " to "+word)
    else: print("\033[91m"+word+" or "+against+" not found\033[0m")
