#!/usr/bin/env python3

import sys, cProfile, time
from math import sqrt

grid_len = 81
possible = set()
# validDict = {}
posWithIndex = {}
full_groups = {"row":[],"col":[],"sq":[]}
aGroups = [{i+k for i in range(0,9)} for k in range(0,81,9)] # Columns
aGroups += [{i for i in range(0+k,81,9)} for k in range(0,9)] # Rows
aGroups += [{row*9+col+i+k for i in range(0,3) for k in range(0,27,9)} for col in range(0,9,3) for row in range(0,9,3)] # Squares
tbf = 0

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
    return full_groups['col'][colv[pos]]
def nir(pos):
    return full_groups['row'][rowv[pos]]
def nis(pos):
    return full_groups['sq'][sqv[pos]]

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

def selectCell(validDict):
    global possible
    if possible:
        return min(possible, key=lambda p: len(validDict[p]))
    return -1

def remove(index, c, validDict):
    for pos in posWithIndex[index]:
        if pos in validDict and c in validDict[pos]:
            validDict[pos].remove(c)

def deduct(grid,validDict):
    global possible,aGroups
    added = {}
    pg = 1
    deductions = 0
    while pg > 0:
        not_possible = set()
        pg = 0
        for pos in possible:
            tmp = validDict[pos]
            if len(tmp) == 1:
                pg += 1
                r = next(iter(tmp))
                grid = grid[:pos] + r + grid[pos+1:]
                remove(pos,r,validDict)
                not_possible.add(pos)
                added[pos] = validDict[pos]

        possible -= not_possible
        not_possible = set()

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
                # if pos in validDict: added[pos] = validDict[pos]
                remove(pos,r,validDict)
                not_possible.add(pos)
                added[pos] = validDict[pos]

        deductions += pg
        possible -= not_possible

    return grid,deductions,added

def bruteForce(grid,validDict):
    global possible, tbf

    grid,deductions,added = deduct(grid,validDict)
    guesses = 0
    pos = selectCell(validDict)

    if pos < 0: return grid,guesses,deductions
    vn = validDict[pos].copy()
    for c in vn:
        tbf += 1
        cd = {k:validDict[k].copy() for k in validDict}
        guesses += 1

        remove(pos,c,cd)
        possible.remove(pos)
        bf,g,deductions = bruteForce(grid[:pos] + c + grid[pos+1:],cd)
        guesses += g
        if bf != "": return bf,guesses,deductions
        possible.add(pos)
    possible.update(added)
    return "",guesses,deductions

def prevalidate(grid,pv):
    
    global possible
    possible = {pos for pos in range(grid_len) if grid[pos] == "."}

    full_groups['col'] = []
    full_groups['row'] = []
    full_groups['sq'] = []
    for x in range(9):
        tmp = set(notInCol(grid,x,pv[:]))
        full_groups['col'].append(tmp)
    for y in range(9):
        tmp = set(notInRow(grid,y*9,pv[:]))
        full_groups['row'].append(tmp)
    for y in range(3):
        for x in range(3):
            tmp = set(notInSquare(grid,x*3+9*(y*3),pv[:]))
            full_groups['sq'].append(tmp)

    validDict = {}

    for i in possible:
        validDict[i] = validNext(i)
        posWithIndex[i] = set()
        for grp in aGroups:
            if i in grp:
                for pos in grp:
                    posWithIndex[i].add(pos)
        posWithIndex[i] -= {str(i)}

    grid,deductions,added = deduct(grid,validDict)
    return grid,deductions,validDict

def all(lowest,highest):
    tguesses = 0
    tdeductions = 0
    tct = 0
    filename = "all_solutions.txt"
    open(filename,"w").close()
    for i in range(lowest,highest):
        try:
            oldgrid = readGrid("sudoku128.txt",i)
            start_time = time.time()
            grid,deductions,validDict = prevalidate(oldgrid,possibleValues[:])
            bf,guesses,tempd = bruteForce(grid,validDict)
            deductions += tempd
            tguesses += guesses
            tdeductions += deductions
            ct = time.time() - start_time
            tct += ct
            if not validate(bf):
                raise RuntimeError('Algorithm produced an invalid board ({})'.format(i+1))
            else:
                string = "{0:0=3d} {1}\n{2:0=3d} {3}\n{4}".format(i+1, oldgrid, i+1,bf,
                    "Time: {0:0.15f}s --- Guesses (Deductions): {1} ({2})\n".format(ct,guesses,deductions))
                print(string)
        except KeyboardInterrupt:
            print("\nStopped at {0:0=3d}".format(i+1))
            return
    print("Total guesses: " + str(tguesses))
    print("Total deductions: " + str(tdeductions))
    print("Total calculation time: {} seconds".format(tct))

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
        bf,guesses,deductions = bruteForce(grid,validDict)
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "!!!! Invalid")
        print("Guesses: " + str(guesses) + " (Prefilled " + str(pg)+")")
        print("Deductions: " + str(deductions))
    print("Time: " + str(time.time() - start) + " seconds")
main()
# cProfile.run("main()")
