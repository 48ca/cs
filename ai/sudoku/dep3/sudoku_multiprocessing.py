#!/usr/bin/env python3

import sys, cProfile, time
from multiprocessing import Pool
from math import sqrt
from queue import Queue

q = Queue()

grid_len = 81
# possible = set()
# validDict = {}
vdPos = {}
groups = {"row":[],"col":[],"sq":[]}
aGroups = [{i+k for i in range(0,9)} for k in range(0,81,9)] # Columns
aGroups += [{i for i in range(0+k,81,9)} for k in range(0,9)] # Rows
aGroups += [{row*9+col+i+k for i in range(0,3) for k in range(0,27,9)} for col in range(0,9,3) for row in range(0,9,3)] # Squares

def readGrid(filename,index):
    return open(filename).read().split()[index]

def generateGrid(string):
    n = int(sqrt(len(string)))
    return [string[i:i+n] for i in range(0,len(string),n)],n

def printGrid(grid_string):
    grid,size = generateGrid(grid_string)
    if size == 0: print("Invalid grid")
    for rin,row in enumerate(grid):
        for index, x in enumerate(row):
            sys.stdout.write( x + " " )
            if (index+1)%3 == 0 and index < 8:
                sys.stdout.write( "| " )
        print()
        if (rin+1)%3 == 0 and rin < 8:
            print("----------------------")

def notInRow(grid, pos,ret):
    y = pos//9
    for x in range(9):
        if grid[x+y*9] in ret:
            ret.remove(grid[x+y*9])
    return ret

def notInCol(grid, pos, ret):
    x = pos%9
    for y in range(9):
        if grid[x+y*9] in ret:
            ret.remove(grid[x+y*9])
    return ret
def notInSquare(grid,pos, ret):
    # Find index of top-left corner
    pos = pos - pos%3
    pos = 27*(pos//27) + pos%9

    for y in range(pos,pos+27,9):
        for x in range(0,3):
            if grid[x+y] in ret: ret.remove(grid[x+y])
    
    return ret

def validate(grid):
    for x in range(9):
        for y in range(9):
            check = notInCol(grid,x+y*9,possibleValues[:])
            if(
                check == notInRow(grid,x+y*9,possibleValues[:])
                and check == notInSquare(grid,x+y*9,possibleValues[:])
                and check  == []
            ):
                continue
            return False
    return True

def nic(pos):
    return groups['col'][colv[pos]]
def nir(pos):
    return groups['row'][rowv[pos]]
def nis(pos):
    return groups['sq'][sqv[pos]]

def intersect(s1,s2,s3):
    return s1 & s2 & s3

def validNext(pos):
    return intersect(nir(pos), nic(pos), nis(pos))

colv = {}
rowv = {}
sqv  = {}

def genv():
    global sqv,rowv,colv
    for i in range(81):
        colv[i] = i%9
        rowv[i] = i//9
        tmp = i - i%3
        tmp = tmp - tmp%27 + tmp%9
        sqv[i] = 3*(tmp//27) + (tmp%9)//3

def selectCell(grid,validDict,possible):
    ml = 10
    mi = -1
    for pos in possible:
        tmp = validDict[pos]
        tl = len(tmp)
        if tl < ml:
            ml = tl
            mi = pos
    return mi

def remove(index, c, validDict):
    s = {c}
    for pos in vdPos[index]:
        if pos in validDict:
            validDict[pos] -= s

def deduct(grid,validDict,possible):
    global aGroups
    added = {}
    pg = 1
    tpg = 0
    while pg > 0:
        np = set()
        pg = 0
        for pos in possible:
            tmp = validDict[pos]
            if len(tmp) == 1:
                pg += 1
                r = next(iter(tmp))
                grid = grid[:pos] + r + grid[pos+1:]
                remove(pos,r,validDict)
                np.add(pos)
                del validDict[pos]
                added[pos] = r


        # Main speedup
        for grp in aGroups:
            indexd = {}
            for pos in grp:
                if grid[pos] != '.': continue
                lp = validDict[pos]
                for possibility in lp:
                    if possibility in indexd:
                        indexd[possibility] = -1
                    else:
                        indexd[possibility] = pos
            for possibility in indexd:
                if indexd[possibility] == -1: continue
                pos = indexd[possibility] 
                pg += 1
                r = possibility
                grid = grid[:pos] + r + grid[pos+1:]
                remove(pos,r,validDict)
                np.add(pos)
                added[pos] = r

        tpg += pg
        possible -= np

    return grid,tpg,added

def undeduct(grid,added,possible):
    for pos in added:
        possible.add(pos)

def bruteForce(grid,validDict,possible):
    grid,tpg,added = deduct(grid,validDict,possible)
    guesses = 0
    pos = selectCell(grid,validDict,possible)

    if pos < 0: return grid,guesses
    vn = validDict[pos].copy()
    for c in vn:
        var = {k:validDict[k].copy() for k in validDict}
        guesses += 1

        remove(pos,c,var)
        possible.remove(pos)
        bf,g = bruteForce(grid[:pos] + c + grid[pos+1:],var,possible)
        guesses += g
        if bf != "": return bf,guesses
        possible.add(pos)
    undeduct(grid,added,possible)
    return "",guesses

def prevalidate(grid,pv):
    
    possible = {pos for pos in range(grid_len) if grid[pos] == "."}

    groups['col'] = []
    groups['row'] = []
    groups['sq'] = []
    for x in range(9):
        tmp = set(notInCol(grid,x,pv[:]))
        groups['col'].append(tmp)
    for y in range(9):
        tmp = set(notInRow(grid,y*9,pv[:]))
        groups['row'].append(tmp)
    for y in range(3):
        for x in range(3):
            tmp = set(notInSquare(grid,x*3+9*(y*3),pv[:]))
            groups['sq'].append(tmp)

    validDict = {}

    for i in possible:
        validDict[i] = validNext(i)
        vdPos[i] = set()
        for grp in aGroups:
            if i in grp:
                for pos in grp:
                    vdPos[i].add(pos)
        vdPos[i] -= {str(i)}

    grid,tpg,added = deduct(grid,validDict,possible)

    return grid,tpg,validDict,possible

def solve(i):
        oldgrid = readGrid("sudoku128.txt",i)
        start_time = time.time()
        grid,pg,validDict,possible = prevalidate(oldgrid,possibleValues[:])
        bf,guesses = bruteForce(grid,validDict,possible)
        if not validate(bf):
            raise RuntimeError('Algorithm produced an invalid board ({})'.format(i+1))
        else:
            print("{0:0=3d} {1}\n{2:0=3d} {3}\n{4}".format(i+1, oldgrid, i+1,bf,
                "Time: {0:0.15f}s --- Guesses (prefilled): {1} ({2})\n".format(time.time()-start_time,guesses,pg)))

def worker(item):
    q.put(solve(item))

def all(lowest,highest):
    filename = "all_solutions.txt"
    open(filename,"w").close()
    pool = Pool(processes=4)
    for i in range(lowest,highest):
        try:
            res = pool.apply_async(worker, [i])
            print(res.get(timeout=4))
        except KeyboardInterrupt:
            print("\nStopped at {0:0=3d}".format(i+1))
            return

def main():

    start = time.time()

    global possibleValues
    possibleValues = ['1','2','3','4','5','6','7','8','9']
    genv()
    if len(sys.argv) < 2:
        all(0,128)
    elif len(sys.argv) == 3:
        all(int(sys.argv[1])-1,int(sys.argv[2]))
    else:
        grid = readGrid("sudoku128.txt",int(sys.argv[1]) - 1) # 1-based input
        printGrid(grid)
        print()
        grid,pg,validDict = prevalidate(grid,possibleValues[:])
        start_time = time.time()
        bf,guesses = bruteForce(grid,validDict)
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "!!!! Invalid")
        print("Guesses: " + str(guesses) + " (Prefilled " + str(pg)+")")
    print("Time: " + str(time.time() - start) + " seconds")
if __name__ == "__main__":
    main()
# cProfile.run("main()")
