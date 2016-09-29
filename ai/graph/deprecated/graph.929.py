#!/usr/bin/env python3

# Name: James Houghton
# Date: 9-10-15
# Period: 3rd - Gabor

import urllib.request,sys,time,re,string
from collections import deque

def getNeighbors(important,words,visited=set()):
    adj = set()
    alphabet = string.ascii_lowercase
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
    sys.stdout.write("                    \r")
    sys.stdout.flush()
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

def dfs(key,against,w_dict,visited,path,c):
    visited.add(key)
    if key == against:
        return path,True,c
    for val in w_dict[key]:
        if val not in visited:
            p = path + [val]
            c += 1
            p,b,c = dfs(val,against,w_dict,visited,p,c)
            if b:
                return p,b,c
    return path,False,c

def dfs_id(key,against,w_dict,visited,path,mi,level=0):
    visited.add(key)
    if key == against:
        return path
    if level >= mi:
        return None
    for val in w_dict[key]:
        # print("Max level: " + str(mi) + " :: Level: " + str(level+1) + " :: " + str(val))
        if val not in visited:
            p = dfs_id(val,against,w_dict,visited.copy(),path+[val],mi,level+1)
            if p != None:
                return p
    return None

def bfs(word,words_dict,search=None):
    bfs_dict = {word:[word]}
    visited_set = set([word])
    current_list = [word]
    checked = 0
    while current_list:
        furthest_word = current_list[0]
        next_list = []
        for word in current_list:
            for n in words_dict[word]:
                if n in visited_set: continue
                checked+=1
                visited_set.add(n)
                bfs_dict[n] = bfs_dict[word] + [n]
                next_list.append(n)
        if search in bfs_dict:
            return search,bfs_dict[search],visited_set - set(furthest_word), checked
        current_list = next_list
    if search != None:
        return None,None,visited_set,checked
    return furthest_word,bfs_dict[furthest_word],visited_set - set(furthest_word), checked

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
    # if index%200 == 1: showProgress(index,len(words))

cs = "\033[90mNeighbors:\033[0m "

# print(cs + "Generating graph: 100% in "+str(time.time() - old_time)+"s")
print(cs + "Words: "+str(len(words)))
print(cs + "Edges: "+str(numberOfEdges(words_dict)))
print(cs + "Words with most neighbors: "+str(mostNeighbors(words_dict_by_size,highest_length,3)))
# for i in range(highest_length+1):
#     if i in words_dict_by_size:
#         print("Nodes with "+str(i)+" neighbors: "+str(len(words_dict_by_size[i])))
#     else:
#         print("Nodes with "+str(i)+" neighbors: 0")

######### COMPONENTS #########

components,largest = findComponents(words_dict)
total_components = 0
for i in range(largest+1):
    if i in components:
        total_components += len(components[i])
    # print("Components with length "+str(i)+": "+str(len(components[i])))

cs = "\033[91mComponents:\033[0m "
print("-------------------------")
print(cs + "Largest component: "+str(largest)+" words long")
print(cs + "Total components: "+str(total_components))

######### BREADTH FIRST SEARCH #########

start_time = time.time()
cs = "\033[93mBreadth First Search:\033[0m "

if len(sys.argv) == 2:
    print("-------------------------")
    for word in sys.argv[1:]:
        if word in words_dict:
            bfs_r,path,n,c = bfs(word,words_dict)
            print(cs +"Furthest from " + word + ": "+str(bfs_r))
            print(cs + "Path: " + str(path))
            print(cs + "Distance: " + str(len(path)-1))
            print(cs + "Vertices checked: "+str(c))
            print(cs + "Time: "+str(time.time() - start_time)+"s")
        else: print(cs + "\033[91m"+word+" not found\033[0m")
elif len(sys.argv) > 2:
    print("-------------------------")
    word = sys.argv[1];
    if word in words_dict:
        against = sys.argv[2];
        bfs_r,path,n,c = bfs(word,words_dict,against)
        if bfs_r == None or path == None:
            print("\033[93mBreadth First Search:\033[0m \033[91m No path from "+word+" to " + against + "\033[0m")
        else:
            print("\033[93mBreadth First Search:\033[0m Shortest path from "+word + " to " + against + ": "+str(path))
            print("\033[93mBreadth First Search:\033[0m Distance: "+str(len(path)-1))
            print("\033[93mBreadth First Search:\033[0m Vertices checked: "+str(c))
            print("\033[93mBreadth First Search:\033[0m Time: "+str(time.time() - start_time)+"s")
    else: print("\033[93mBreadth First Search:\033[0m \033[91m"+word+" not found\033[0m")

######### DIAMETER CALCULATION #########

print("-------------------------")
index = 0
diam = 0
c = 0
p = []
visited = set()
start_time = time.time()
cs = "\033[95mDiameter:\033[0m "
for w in words_dict:
    if w in visited: continue
    n,path,visited,checked = bfs(w,words_dict)
    if(len(path)-1 > diam):
        diam = len(path)-1
        p = path
    index += 1
    c += checked
    sys.stdout.write(cs + "Calculating diameter: " + str(100*index/len(words_dict)) + "%        \r")
    sys.stdout.flush()
sys.stdout.write("                                                                \r");
print(cs + "Diameter: " + str(diam))
print(cs + "Path: " + str(p))
print(cs + "Time: " + str(time.time() - start_time) + "s")
print(cs + "Vertices checked: "+str(c))

######### DEPTH FIRST SEARCH #########

if len(sys.argv) > 2:
    start_time = time.time()
    cs = "\033[92mDepth First Search:\033[0m "
    print("-------------------------")
    word = sys.argv[1]
    against = sys.argv[2]
    if word in words_dict and against in words_dict:
        p,b,c = dfs(word,against,words_dict,set(),[word],0)
        if b:
            print(cs + "Path from " +against+ " to "+word+": "+str(p))
            # print(cs + "Path from " + against+" to "+word+": [Suppressed]")
            print(cs + "Vertices checked: "+str(c))
            print(cs + "Time: " + str(time.time() - start_time)+"s")
        else:
            print(cs + "\033[91mNo path from " +word+ " to "+against+"\033[0m")
    else: print(cs + "\033[91m"+word+" or "+against+" not found in the dictionary\033[0m")

    print("-------------------------")
    cs = "\033[94mIterative Deepening:\033[0m "
    word = sys.argv[1]
    against = sys.argv[2]
    length = len(words_dict)
    try:
        print(cs + "\033[1mPress ^C to skip this search.\033[0m")
        i = 0
        while i <= diam:
            if word in words_dict and against in words_dict:
                p = dfs_id(word,against,words_dict,set(word),[word],i)
                if p != None:
                    print(cs + "Path from " +word+ " to "+against+": "+str(p))
                    print(cs + "Distance: "+str(len(p)-1))
                    break
            print(cs + "Finished level " + str(i))
            i += 1
        if i > diam:
            print(cs + "\033[91mNo path from "+word+" to "+against+"\033[0m")
    except KeyboardInterrupt:
        print("\n\033[94mIterative Deepening:\033[0m Stopping search...")

######### DIJKSTRA #########

def genCombos(word):
    combos = []
    for i in range(len(word)):
        for j in range(i+1,len(word)):
            tmp = word[:i] + word[j] + word[i+1:j] + word[i] + word[j+1:]
            if tmp!=word: combos.append(tmp)
    return combos

def updateDict(w_dict):
    new_dict = {}
    for w in w_dict:
        combos = genCombos(w)
        new_dict[w] = {x:1 for x in w_dict[w]}
        new_dict[w].update({x:5 for x in combos if x in w_dict})
    return new_dict

def findLowest(q):
    index = 0
    min_cost = 9999999
    for i in range(len(q)):
        cost, v, path = q[i]
        if cost < min_cost:
            index = i
    return index

def dijk(w_dict, start, end):
    visited = set()
    q = [(0,start,[])]
    checked = 0
    max_q = 1
    while q:
        if len(q) > max_q:
            max_q = len(q)
        (cost, v, path) = q.pop(0)
        checked += 1
        if v not in visited:
            visited.add(v)
            if v == end:
                return path + [end],max_q,cost,checked
            path = path + [v]
            for n in w_dict[v]:
                if n not in visited:
                    q.append((cost+w_dict[v][n],n,path))
    return [],max_q,0,checked

if len(sys.argv) > 2:
    print("-------------------------")
    cs = "\033[96mDijkstra:\033[0m "
    d_dict = updateDict(words_dict)
    start_time = time.time()
    p,ml,cost,c = dijk(d_dict,sys.argv[1],sys.argv[2])
    if len(p) == 0:
        print(cs + "Path: \033[91mNo path from "+sys.argv[1]+" to "+sys.argv[2]+"\033[0m")
    else:
        print(cs + "Path: "+str(p))
        print(cs + "Cost: "+str(cost))
    print(cs + "Vertices checked: "+str(c))
    print(cs + "Max length of queue: "+str(ml))
    print(cs + "Time: "+str(time.time()-start_time)+"s")
    
