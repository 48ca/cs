#!/usr/bin/env python3

import sys, time, os, cProfile
from math import sqrt
from multiprocessing import Pool, current_process, cpu_count

grid_len = 81
possible = set()
posWithIndex = {}
full_groups = {"row":[],"col":[],"sq":[]}
aGroups = [{i+k for i in range(0,9)} for k in range(0,81,9)] # Columns
aGroups += [{i for i in range(0+k,81,9)} for k in range(0,9)] # Rows
aGroups += [{row*9+col+i+k for i in range(0,3) for k in range(0,27,9)}
for row in range(0,9,3) for col in range(0,9,3)] # Squares
row_arith = {pos:pos//9 for pos in range(81)}
col_arith = {pos:pos%9 for pos in range(81)}
sq_arith = {pos:3*(pos//27)+(pos%9)//3 for pos in range(81)}
possibleValues = {'1','2','3','4','5','6','7','8','9'}

def readGrid(fa,index):
    return fa[index]

def generateGrid(string):
    n = int(sqrt(len(string)))
    return [string[i:i+n] for i in range(0,len(string),n)],n

def printGrid(grid_string):
    grid,size = generateGrid(grid_string)
    if size == 0: print("Invalid grid")
    for rin,row in enumerate(grid):
        for index, x in enumerate(row):
            if x == ".": x = " "
            sys.stdout.write( x + " " )
            if (index+1)%3 == 0 and index < 8:
                sys.stdout.write( "| " )
        print()
        if (rin+1)%3 == 0 and rin < 8:
            print("----------------------")

def validate(grid):
    if grid == None: return False
    for group in aGroups:
        seen = set()
        for pos in group:
            if grid[pos] in seen: return False
            seen.add(grid[pos])
    return True

def validNext(grid,pos):
    row_n = row_arith[pos]
    col_n = col_arith[pos]
    sq_n = sq_arith[pos]
    row_int = {grid[number] for number in aGroups[row_n]}
    col_int = {grid[number] for number in aGroups[9+col_n]}
    sq_int = {grid[number] for number in aGroups[18+sq_n]}
    return possibleValues - (row_int | col_int | sq_int)

colv = {}
rowv = {}
sqv  = {}

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
                not_possible.add(pos)
                added[pos] = validDict[pos]

        deductions += pg
        possible -= not_possible

    return grid,deductions,added

def bruteForce(grid,validDict):
    global possible

    grid,deductions,added = deduct(grid,validDict)
    guesses = 0
    pos = selectCell(validDict)

    if pos < 0: return grid,guesses,deductions
    for c in validDict[pos]:
        cd = {k:validDict[k].copy() for k in validDict}
        guesses += 1

        remove(pos,c,cd)
        possible.remove(pos)
        bf,g,deductions = bruteForce(grid[:pos] + c + grid[pos+1:],cd)
        guesses += g
        if bf != None: return bf,guesses,deductions
        possible.add(pos)
    possible.update(added)
    return None,guesses,deductions

def prevalidate(grid):
    
    global possible
    possible = {pos for pos in range(grid_len) if grid[pos] == "."}

    validDict = {}

    for i in possible:
        validDict[i] = validNext(grid,i)
        posWithIndex[i] = set()
        for grp in aGroups:
            if i in grp:
                for pos in grp:
                    posWithIndex[i].add(pos)
        posWithIndex[i] -= {str(i)}

    grid,deductions,added = deduct(grid,validDict)
    return grid,deductions,validDict

def worker(grids,numbers,offset):
    ret = []
    try:
        for i in grids:
            oldgrid = grids[i - i%offset]
            start_time = time.time()
            grid,deductions,validDict = prevalidate(oldgrid)
            bf,guesses,tempd = bruteForce(grid,validDict)
            ct = time.time() - start_time
            ret.append([bf,tempd,guesses,deductions,ct,i+1])
        return ret
    except KeyboardInterrupt:
        print("\nStopping {}".format(current_process()))

def all(lowest,highest):
    global puzzle_fn
    tguesses = 0
    tdeductions = 0
    tct = 0
    num_proc = cpu_count()
    filename = puzzle_fn.split(".")[0]+"Solutions.txt"
    if __name__ == "__main__":
        try:
            pool = Pool(processes=num_proc)
            tasks = []
            offset = 1
            sys.stdout.write("Answering: Initializing\r")
            sys.stdout.flush()
            for i in range(lowest,highest,offset):
                    grids = {k:readGrid(fa,k) for k in range(i,i+offset)}
                    tasks.append(pool.apply_async(worker,[grids,i,offset]))
            answers = {}
            solve_time = time.time()
            hardest = {}
            for i,res in enumerate(tasks):
                arr = res.get(timeout=100)
                for result in arr:
                    tdeductions += result[1]
                    tguesses += result[2]
                    tdeductions += result[3]
                    tct += result[4]
                    hardest[result[4]] = [result[5], result[2], result[3]]
                    sys.stdout.write("Answering: {0:10.6f}%  {1:5d}/{2:0=05d}\r".format(100.0 * i / (highest-lowest), i+lowest, highest))
                    sys.stdout.flush()
                    answers[result[5]] = result[0]
            f = open(filename,"w")
            for index, result in enumerate(sorted(answers)):
                if answers[result] == None: raise RuntimeError("Puzzle not solved ({})".format(lowest+index+1))
                f.write(answers[result] + "\n")
            f.close()
            print("Results written to {}".format(filename))
            print("Total puzzles solved: "+str(highest) + "                 ")
            print("Total guesses: " + str(tguesses))
            print("Total deductions: " + str(tdeductions))
            print("Total calculation time: {} seconds".format(tct))
            print("Total solve time: {} seconds".format(time.time() - solve_time))
            print("Approximate serial solve time: {} seconds".format(num_proc*(time.time() - solve_time)))
            hardest_times = sorted(hardest.keys(),reverse=True)
            print("Hardest puzzles:")
            for ht in hardest_times[0:10]:
                print("\t{0:5d}: {1:16.14f}s ({2} guesses)".format(hardest[ht][0],ht,hardest[ht][1]))
            f = open(filename,"r")
            fsolns = f.read().split("\n")
            f.close()
            f = open(puzzle_fn,"r")
            fpuzzles = f.read().split("\n")
            f.close()
            validation_time = time.time()
            validation_tasks = {}
            sys.stdout.write("Validating: Initializing\r")
            sys.stdout.flush()
            for index,puzzle in enumerate(fsolns):
                if puzzle == None or len(puzzle) == 0:
                    continue
                validation_tasks[index] = pool.apply_async(validate,[puzzle])
            for i in validation_tasks:
                valid = validation_tasks[i].get(timeout=10)
                if not valid:
                    raise RuntimeError("Error validating: Invalid puzzle ({})".format(i+1+lowest))
                solved = fsolns[i]
                puzzle = fpuzzles[i+lowest]
                for pos in {pos for pos in range(len(puzzle)) if puzzle[pos] != "."}:
                    if solved[pos] != puzzle[pos]:
                        raise RuntimeError("Error validating: Puzzle mismatch ({})".format(i+lowest+1))
                if i%12 == 3:
                    sys.stdout.write("Validating: {0:10.6f}%  {1:5d}/{2:0=05d}\r".format(100.0 * i / (highest-lowest), i+lowest, highest))
                    sys.stdout.flush()
            print("Validation time: {} seconds".format(time.time() - validation_time))
            print("\033[92m" + "Results in {} are valid answers to {}".format(filename,puzzle_fn)+ "\033[0m")
        except KeyboardInterrupt:
            print("\nStopping manager")
            return

def main():
    global puzzle_fn, fa
    start = time.time()
    puzzle_fn = "sudoku141.txt"
    fa = open(puzzle_fn,"r").read().split("\n")
    if len(sys.argv) < 2:
        all(0,len(fa)-1)
    elif len(sys.argv) == 3:
        all(int(sys.argv[1])-1,int(sys.argv[2]))
    else:
        fn = open(puzzle_fn,"r").read().splitlines()
        grid = readGrid(fn,int(sys.argv[1]) - 1) # 1-based input
        printGrid(grid)
        print()
        grid,pg,validDict = prevalidate(grid)
        start_time = time.time()
        bf,guesses,deductions = bruteForce(grid,validDict)
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "!!!! Invalid")
        print("Guesses: " + str(guesses) + " (Prefilled " + str(pg)+")")
        print("Deductions: " + str(deductions))
    print("Wall time: " + str(time.time() - start) + " seconds")
main()
