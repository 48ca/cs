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
def inRow(grid, value, y):
    for x in range(9):
        if grid[x+y*9] == value:
            return True
    return False

def inCol(grid, value, x):
    for y in range(9):
        if grid[x+y*9] == value:
            return True
    return False

def notInRow(grid, pos):
    ret = possibleValues[:]
    y = pos//9
    for x in range(9):
        if grid[x+y*9] in possibleValues:
            ret.remove(grid[x+y*9])
    return ret

def notInCol(grid, pos):
    ret = possibleValues[:]
    x = pos%9
    for y in range(9):
        if grid[x+y*9] in possibleValues:
            ret.remove(grid[x+y*9])
    return ret
def notInSquare(grid,pos):
    ret = possibleValues[:]
    
    # Find index of top-right corner
    pos = pos - pos%3
    pos = 27*(pos//27) + pos%9

    for y in range(pos,pos+27,9):
        for x in range(0,3):
            if grid[x+y] in ret: ret.remove(grid[x+y])
    
    return ret

def validNext(grid):
    pos = grid.find('.')
    valid = list(set(notInRow(grid,pos)) & set(notInCol(grid,pos)) & set(notInSquare(grid,pos)))
    return valid

def bruteForce(grid):
    pos = grid.find('.')
    if pos < 0: return grid
    # print("\t\t\t" + str(validNext(grid)) + " "+str(pos))
    for c in validNext(grid):
        bf = bruteForce(grid[:pos] + c + grid[pos+1:])
        if bf != "": return bf
    return ""

def all():
    for i in range(128):
        grid = readGrid("sudoku128.txt",i)
        start_time = time.time()
        print(str(i) + " " + str(grid) + " " + str(bruteForce(grid)) + " " + str(time.time() - start_time))
def main():
    global possibleValues
    possibleValues = ['1','2','3','4','5','6','7','8','9']
    if len(sys.argv) < 2:
        all()
    else:
        grid = readGrid("sudoku128.txt",int(sys.argv[1]))
        printGrid(grid)
        printGrid(bruteForce(grid))
main()
# cProfile.run("main()")
