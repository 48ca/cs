#!/usr/bin/env python3

import sys, cProfile, time, copy
from math import sqrt

grid_len = 81
groups = {"row":[],"col":[],"sq":[]}
aGroups = [{i+k for i in range(0,9)} for k in range(0,81,9)] # Columns
aGroups.extend([{i for i in range(0+k,81,9)} for k in range(0,9)]) # Rows
aGroups.extend([{row*9+col+i+k for i in range(0,3) for k in range(0,27,9)} for col in range(0,9,3) for row in range(0,9,3)]) # Squares

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

def nic(grid,pos):
    return groups['col'][colv[pos]]
def nir(grid,pos):
    return groups['row'][rowv[pos]]
def nis(grid,pos):
    return groups['sq'][sqv[pos]]

def intersect(s1,s2,s3):
    return s1 & s2 & s3

def validNext(grid,pos):
    return intersect(nir(grid,pos), nic(grid,pos), nis(grid,pos))

colv = {}
rowv = {}
sqv  = {}

def genv():
    for i in range(81):
        colv[i] = i%9
        rowv[i] = i//9
        tmp = i - i%3
        tmp = tmp - tmp%27 + tmp%9
        sqv[i] = 3*(tmp//27) + (tmp%9)//3

def findPossible(grid,possible):
    # global possible
    # possible = {pos for pos in range(grid_len) if grid[pos] == "."}
    return possible.copy()

def selectCell(grid,possible):
    ml = 10
    mi = -1
    for pos in findPossible(grid,possible):
        tmp = validNext(grid,pos)
        tl = len(tmp)
        if tl < ml:
            ml = tl
            mi = pos
    return mi

def remove(index, c, possible):
    """
    cg = groups['col'][colv[index]]
    if cg is not None and c in cg: cg.remove(c)
    cr = groups['row'][rowv[index]]
    if cr is not None and c in cr: cr.remove(c)
    cs = groups['sq'][sqv[index]]
    if cs is not None and c in cs: cs.remove(c)
    # if index in possible: possible.remove(index)
    """
    if index in possible: del possible[index]
    for pos in possible:
        possible[pos] -= {index}
    for grp in aGroups:
        for pos in grp:
            if index in grp:
                if pos in possible:
                    possible[pos] -= {index}
    return index

def add(index, c):
    """
    groups['sq'][sqv[index]].add(c)
    groups['col'][colv[index]].add(c)
    groups['row'][rowv[index]].add(c)
    """
    possible[index] = c
    for pos in range(index//9,9+index//9):
        if pos in possible:
            possible[pos] += {c}
    for pos in range(index%9,index%9 + 81, 9):
        if pos in possible:
            possible[pos] += {c}
    sqi = groups['sq'][sqv[index]]
    for pos in range(sqi,sqi+3):
        for h in range(0,3):
            if sqi + 9*h in possible:
                possible[sqi + 9*h] += {c}
    return index
    
def deduct(grid,possible):
    global aGroups
    added = {}
    pg = 1
    tpg = 0
    possible = possible.copy()
    while pg > 0:
        np = set()
        pg = 0
        for pos in findPossible(grid,possible):
            tmp = validNext(grid,pos)
            if len(tmp) == 1:
                pg += 1
                r = list(tmp)[0]
                grid = grid[:pos] + r + grid[pos+1:]
                np.add(remove(pos,r,possible))
                added[pos] = r
        for grp in aGroups:
            for pos in grp:
                if grid[pos] != '.': continue
                lp = validNext(grid,pos)
                # print(str(pos) + " ::: " + str(lp))
                tmp = lp
                for x in grp - {pos}:
                    tmp.update(validNext(grid,x))
                    # print(tmp)
                # l = [validNext(grid,x) for x in grp - pos]
                inter = lp - tmp&lp
                if len(inter) == 1:
                    pg += 1
                    r = list(inter)[0]
                    # print("Adding " + r + " at " + str(pos))
                    grid = grid[:pos] + r + grid[pos+1:]
                    np.add(remove(pos,r,possible))
                    added[pos] = r
        # printGrid(grid)
        # print()
        tpg += pg
        for key in np:
            if key in possible:
                del possible[key]

    return grid,tpg,added,possible

def undeduct(grid,added):
    global possible
    for pos in added:
        add(pos,added[pos])
        # possible[pos] = validNext(grid,pos)

def bruteForce(grid,possible,start_time=None):
    grid,tpg,added,new_possible = deduct(grid,possible)
    guesses = tpg
    # pos = grid.find('.')
    pos = selectCell(grid,possible)

    if pos < 0: return grid,guesses
    # print("\t\t\t" + str(validNext(grid)) + " "+str(pos))
    vn = validNext(grid,pos)
    for c in vn:
        index = pos
        guesses += 1

        remove(index,c,possible)
        # del possible[index]
        bf,g = bruteForce(grid[:pos] + c + grid[pos+1:],possible,start_time)
        guesses += g
        if bf != "": return bf,guesses
        add(index,c)
    undeduct(grid,added)
    return "",guesses

def prevalidate(grid,pv):
    
    groups['col'] = []
    groups['row'] = []
    groups['sq'] = []
    for x in range(9):
        tmp = set(notInCol(grid,x,pv[:]))
        groups['col'].append(tmp)
    for y in range(9):
        tmp = set(notInRow(grid,y*9,pv[:]))
        # print(str(y) + str(tmp))
        groups['row'].append(tmp)
    for y in range(3):
        for x in range(3):
            tmp = set(notInSquare(grid,x*3+9*(y*3),pv[:]))
            # print(tmp)
            groups['sq'].append(tmp)

    possible = {pos:validNext(grid,pos) for pos in range(grid_len) if grid[pos] == "."}
    grid,tpg,added,possible = deduct(grid,possible)
    return grid,tpg,possible

def all(lowest,highest):
    filename = "all_solutions.txt"
    open(filename,"w").close()
    for i in range(lowest,highest):
        try:
            ogrid = readGrid("sudoku128.txt",i)
            start_time = time.time()
            grid,pg,possible = prevalidate(ogrid,possibleValues[:])
            bf,guesses = bruteForce(grid,possible,start_time)
            valid = "VALID" if validate(bf) else "INVALID"
            string = str(i+1) + " " + ogrid + "\n" + str(i+1) + " " + grid + "\n" + str(i+1) + " " + bf + "\n" + "Time: " + str(time.time()-start_time) + " --- Guesses (prefilled): " + str(guesses) + " ("+str(pg)+") " + valid + "\n"
            print(string)
            f = open(filename,"a")
            f.write(string+"\n")
            f.close()
        except KeyboardInterrupt:
            print("\nStopped at {0:0=3d}".format(i))
            return

def main():
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
        grid,pg,possible = prevalidate(grid,possibleValues[:])
        print("Finished prefill")
        start_time = time.time()
        bf,guesses = bruteForce(grid,possible)
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "!!!! Invalid")
        print("Time: " + str(time.time() - start_time))
        print("Guesses: " + str(guesses) + " (Prefilled " + str(pg)+")")
main()
# cProfile.run("main()")
