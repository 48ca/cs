#!/usr/bin/env python3
# Name: James Houghton
# Date: 9-10-15
# Period: 3rd - Gabor

import urllib.request,sys,time,re

def allAdjacentTo(important, words):
    adj = set()
    for i in range(len(important)):
        pattern_string = important[:i]+"[^"+important[i]+"]"+important[i+1:]+"(?=[ ])"
        pattern = re.compile(pattern_string)
        results = pattern.findall(words)
        adj.update(results)
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
    words_b = urllib.request.urlopen(link).read().split()
    words = [word.decode() for word in words_b]
    print("Download finished     ")
    return words
def mostNeighbors(w_dict,max_length):
    count = 0
    index = max_length
    words = set()
    while count<3:
        if index in w_dict:
            words.update(w_dict[index].keys())
            count += len(w_dict[index].keys())
        index -= 1
    return words

words_dict = {}
words_dict_by_size = {}

link = "https://academics.tjhsst.edu/compsci/ai/web2015/words.txt"
words = downloadWords(link)

word_string = ""
for word in words:
    word_string += word+" "

old_time = time.time()
highest_length = 0
for index, word in enumerate(words):
    words_dict[word] = allAdjacentTo(word,word_string)
    length = len(words_dict[word])
    if length not in words_dict_by_size: words_dict_by_size[length] = {}
    highest_length = max(length,highest_length)
    words_dict_by_size[length][word] = words_dict[word]
    if index%20 == 1: showProgress(index,len(words))

print("Generating graph: 100% in "+str(time.time() - old_time)+"s")
print("Words: "+str(len(words)))
print("Edges: "+str(numberOfEdges(words_dict)))
print("Words with most neighbors: "+str(mostNeighbors(words_dict_by_size,highest_length)))

######### COMPONENTS ##########

components,largest = findComponents(words_dict)
total_components = 0
for i in range(largest+1):
    if i in components:
        print("Components with length "+str(i)+": "+str(len(components[i])))
        total_components += len(components[i])
print("Largest component is "+str(largest)+" words long")
print("Total components: "+str(total_components))
if len(sys.argv) > 1:
    print("-------------------------")
    for word in sys.argv[1:]:
        if word in words_dict: print("Adjacent to "+word+": "+str(words_dict[word]))
        else: print("\033[91m"+word+" not found\033[0m")
