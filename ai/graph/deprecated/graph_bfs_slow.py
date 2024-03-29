#!/usr/bin/env python3

# Name: James Houghton
# Date: 9-10-15
# Period: 3rd - Gabor

import urllib.request,sys,time,re
from collections import deque

def getNeighbors(important,words,visited=set()):
    adj = set()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(important)):
        for l in alphabet:
            word = important[:i] + l + important[i+1:]
            if word in words and word not in visited and word != important:
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
def downloadWords(link):
    sys.stdout.write("Downloading words...\r")
    sys.stdout.flush()
    words = [word.decode() for word in urllib.request.urlopen(link).read().split()]
    print("Download finished     ")
    return words
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

def findPath(word,level_dict,w_dict):
    level = level_dict[word]["level"]
    path = [word] 
    word_to_compare = word
    while level_dict[word_to_compare]["level"] > 0:
        for w in w_dict[word_to_compare]:
            if w in level_dict and level_dict[w]["level"] < level:
                word_to_compare = w
                path = [w] + path
                level = level_dict[w]["level"]
                break
    # print(word + str(path))
    return path
    
def bfs3(word,words_dict,search=None):
    bfs_dict = {word:{"path":[word],"level":0}}
    level = 0
    visited_set = set()
    current_list = [word]
    size = len(words_dict)
    path = [word]
    while len(visited_set) < size:
        new_dict = {n:{"path":bfs_dict[word]["path"] + [n],"level":level} for n in words_dict[word] for word in current_list if n in visited_set}
        if search in current_list:
            return bfs_dict[word]
        visited_set.update(current_list)
        current_list = [n for w in current_list for n in words_dict[w] if n not in visited_set]
        print(current_list)
        level += 1
    init_level = 0
    biggest_word = word
    for w in bfs_dict:
        if bfs_dict[w]["level"] > init_level:
            init_level = bfs_dict[w]["level"]
            biggest_word = w
        return biggest_word,bfs_dict[biggest_word]["path"]
    return None,None

def bfs2(word,words_dict,search=None):
    q = deque()
    bfs_dict = {word:{"path":[word],"level":0}}
    q.append(word)
    level = 0
    while q:
        w = q.popleft()
        for n in words_dict[w]:
            if n in bfs_dict and level > bfs_dict[n]["level"]+1:
                level = bfs_dict[n]["level"]+1
        for n in words_dict[w]:
            if n not in bfs_dict:
                bfs_dict[n] = {"level":level+1,"path":[]}
                bfs_dict[n]["path"] = findPath(n,bfs_dict,words_dict)
                q.append(n)
        level += 1

##########

    if search == None:
        init_level = 0
        biggest_word = word
        for w in bfs_dict:
            if bfs_dict[w]["level"] > init_level:
                init_level = bfs_dict[w]["level"]
                biggest_word = w
        return biggest_word,bfs_dict[biggest_word]["path"]
    else:
        try:
            return search,bfs_dict[search]["path"]
        except KeyError:
            return None,None

words_dict = {}
words_dict_by_size = {}

link = "https://academics.tjhsst.edu/compsci/ai/web2015/words.txt"
words = downloadWords(link)
word_set = set(words)

old_time = time.time()
highest_length = 0
for index, word in enumerate(words):
    words_dict[word] = getNeighbors(word,word_set)
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

######### BREADTH FIRST SEARCH #########

    ##### DIAMETER CALCULATION #####

index = 0
diam = 0
p = []
for w in words_dict:
    n,path = bfs2(w,words_dict)
    if(len(path) > diam):
        diam = len(path)
        p = path
    index += 1
    sys.stdout.write("Calculating diameter: " + str(100*index/len(words_dict)) + "%        \r")
    sys.stdout.flush()
sys.stdout.write("                                                                          \r");
print("Diameter: " + str(diam-1))
print("Path: " + str(p))

if len(sys.argv) == 2:
    print("-------------------------")
    for word in sys.argv[1:]:
        if word in words_dict:
            bfs,path = bfs2(word,words_dict)
            print("Furthest from " + word + ": "+str(bfs))
            print("Path: " + str(path))
            print("Distance: " + str(len(path)-1))
        else: print("\033[91m"+word+" not found\033[0m")
elif len(sys.argv) > 2:
    print("-------------------------")
    word = sys.argv[1];
    if word in words_dict:
        against = sys.argv[2];
        bfs,path = bfs2(word,words_dict,against)
        if bfs == None or path == None:
            print("\033[91mPath from "+word+" to " + against + " not found\033[0m")
        else:
            print("Shortest path from "+word + " to " + against + ": "+str(path))
            print("Distance: "+str(len(path)-1))
    else: print("\033[91m"+word+" not found\033[0m")
