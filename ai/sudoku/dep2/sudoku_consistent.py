#!/usr/bin/env python3

import sys, cProfile, time
from math import sqrt

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

def validNext(grid):
    pos = grid.find('.')
    valid = notInRow(grid,pos,notInCol(grid,pos,notInSquare(grid,pos,possibleValues[:])))
    return valid

def bruteForce(grid,start_time=None):
    pos = grid.find('.')
    if pos < 0: return grid
    # print("\t\t\t" + str(validNext(grid)) + " "+str(pos))
    for c in validNext(grid):
        bf = bruteForce(grid[:pos] + c + grid[pos+1:],start_time)
        if bf != "": return bf

        # if start_time is not None and time.time() - start_time > 10:
        #    return grid

    return ""

def all():
    filename = "all_solutions.txt"
    open(filename,"w").close()
    for i in range(128):
        try:
            grid = readGrid("sudoku128.txt",i)
            start_time = time.time()
            bf = bruteForce(grid,start_time)
            valid = "VALID" if validate(bf) else "INVALID"
            string = "{0:0=3d}".format(i) + " " + str(grid) + " " + str(bf) + " " + str(time.time() - start_time) + " " + valid
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
    if len(sys.argv) < 2:
        all()
    else:
        grid = readGrid("sudoku128.txt",int(sys.argv[1]) - 1) # 1-based input
        printGrid(grid)
        start_time = time.time()
        bf = bruteForce(grid)
        print()
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "Invalid")
        print("Time: " + str(time.time() - start_time))
main()
# cProfile.run("main()")
