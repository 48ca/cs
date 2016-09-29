import time
import sys

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
            return search,bfs_dict[search],visited_set - {furthest_word}, checked
        current_list = next_list
    if search != None:
        return None,None,visited_set,checked
    return furthest_word,bfs_dict[furthest_word],visited_set - {furthest_word}, checked

def diam(words_dict):
    index = 0
    diam = 0
    c = 0
    p = []
    visited = set()
    start_time = time.time()
    cs = "\033[95mDiameter:\033[0m "
    leng = len(words_dict)
    for w in words_dict:
        if w in visited: continue
        n,path,visited,checked = bfs(w,words_dict)
        if(len(path)-1 > diam):
            diam = len(path)-1
            p = path
        index += 1
        c += checked
        sys.stdout.write(cs + "Calculating diameter: " + str(100*index/leng) + "%        \r")
        sys.stdout.flush()
    sys.stdout.write("                                                                \r");
    print(cs + "Diameter: " + str(diam))

def hdiam(words_dict):
    index = 0
    diam = 0
    c = 0
    p = []
    visited = set()
    start_time = time.time()
    cs = "\033[1;95mHeuristic Diameter:\033[0m "
    w = list(words_dict.keys())[0]
    hit = 0
    index = 0
    f_diam = 0
    f_path = []
    c = 0
    limit = 25
    leng = len(words_dict)
    for w in words_dict:
        if index > limit: break
        w,path,visited,checked = bfs(w,words_dict)
        # c = checked
        w,path,visited,checked = bfs(w,words_dict)
        diam = len(path)-1
        index += 1
        if diam > f_diam:
            f_diam = diam
            f_path = path
        c += checked
    print(cs + "Diameter: " + str(f_diam) + "                    ")
    print(cs + "Path: " + str(f_path))
    print(cs + "Time: " + str(time.time() - start_time) + "s")
    print(cs + "Iterations: " + str(limit))
    print(cs + "Vertices checked: "+str(c))
