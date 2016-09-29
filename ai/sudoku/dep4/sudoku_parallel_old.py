#!/usr/bin/env python3

import sys, time, os, cProfile
from math import sqrt
from multiprocessing import Pool, current_process, cpu_count
# os.system("taskset -p 0xff %d" % os.getpid())

grid_len = 81
possible = set()
# validDict = {}
posWithIndex = {}
full_groups = {"row":[],"col":[],"sq":[]}
aGroups = [{i+k for i in range(0,9)} for k in range(0,81,9)] # Columns
aGroups += [{i for i in range(0+k,81,9)} for k in range(0,9)] # Rows
aGroups += [{row*9+col+i+k for i in range(0,3) for k in range(0,27,9)}
for row in range(0,9,3) for col in range(0,9,3)] # Squares

def readGrid(fa,index):
    # return open(filename).read().split()[index]
    # print(index)
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

"""
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
"""

def validate(grid):
    for group in aGroups:
        seen = set()
        for pos in group:
            if grid[pos] in seen: return False
            seen.add(grid[pos])
    return True

def validNext(grid,pos):
    row_n = pos//9
    col_n = pos%9
    sq_n = (3*(pos//27) + (pos%9)//3)
    row_int = {grid[number] for number in aGroups[row_n]}
    col_int = {grid[number] for number in aGroups[9+col_n]}
    sq_int = {grid[number] for number in aGroups[18+sq_n]}
    # print(row_int)
    # print(col_int)
    # print(sq_int)
    # print("pos: {} r: {} col: {} sq:{}".format(pos,row_n,col_n,sq_n))
    return set("123456789") - (row_int | col_int | sq_int)

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
        if bf != "": return bf,guesses,deductions
        possible.add(pos)
    possible.update(added)
    return "",guesses,deductions

def prevalidate(grid,pv):
    
    global possible
    possible = {pos for pos in range(grid_len) if grid[pos] == "."}

    """
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
    """
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
            grid,deductions,validDict = prevalidate(oldgrid,possibleValues[:])
            bf,guesses,tempd = bruteForce(grid,validDict)
            ct = time.time() - start_time
            valid = True # skipping validation routine (validate(bf))
            # valid = validate(bf)
            if not valid:
                raise RuntimeError('Algorithm produced an invalid board ({})'.format(i+1))
            else:
                # ret.append(["{0:0=5d} {1}".format(i+1,bf),tempd,guesses,deductions,ct,i+1])
                ret.append([bf,tempd,guesses,deductions,ct,i+1])
                """
                ret.append(
                    ["{0:0=3d} {1}\n{2:0=3d} {3}\n{4}".format(
                        i+1, oldgrid, i+1,bf,
                    "Time: {0:0.15f}s --- Guesses (Deductions): {1} ({2})\n\n".format(
                        ct,guesses,deductions
                    )),tempd, guesses, deductions, ct]
                )
                """
        return ret
    except KeyboardInterrupt:
        print("\nStopping {}".format(current_process()))

def all(lowest,highest):
    global puzzle_fn
    tguesses = 0
    tdeductions = 0
    tct = 0
    num_proc = cpu_count()
    print("Using {} processes".format(num_proc))
    filename = "all_solutions.txt"
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
            for i,res in enumerate(tasks):
                arr = res.get(timeout=100)
                for result in arr:
                    tdeductions += result[1]
                    tguesses += result[2]
                    tdeductions += result[3]
                    tct += result[4]
                    # print(result[0])
                    sys.stdout.write("Answering: {0:10.6f}%  {1:5d}/{2:0=05d}\r".format(100 * i / highest, i, highest))
                    sys.stdout.flush()
                    answers[result[5]] = result[0]
            f = open(filename,"w")
            for result in sorted(answers):
                f.write(answers[result] + "\n")
            f.close()
            print("Results written to {}".format(filename))
            print("Total puzzles solved: "+str(highest) + "                 ")
            print("Total guesses: " + str(tguesses))
            print("Total deductions: " + str(tdeductions))
            print("Total calculation time: {} seconds".format(tct))
            print("Total solve time: {} seconds".format(time.time() - solve_time))
            print("Approximate serial solve time: {} seconds".format(num_proc*(time.time() - solve_time)))
            if lowest == 0 and highest == len(fa)-1:
                # Validation of all puzzles
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
                for index,puzzle in enumerate(fpuzzles):
                    if len(puzzle) == 0:
                        continue
                    solved = fsolns[i]
                    validation_tasks[index] = pool.apply_async(validate,[solved])
                for i in validation_tasks:
                    valid = validation_tasks[i].get(timeout=10)
                    if not valid:
                        raise RuntimeError("Invalid puzzle")
                    solved = fsolns[i]
                    for pos in {pos for pos in range(len(puzzle)) if puzzle[pos] != "."}:
                        if solved[pos] != puzzle[pos]:
                            raise RuntimeError("Puzzle mismatch")
                    sys.stdout.write("Validating: {0:10.6f}%  {1:5d}/{2:0=05d}\r".format(100 * i / highest, i, highest))
                    sys.stdout.flush()
                print("Validation time: {} seconds".format(time.time()-validation_time))
        except KeyboardInterrupt:
            print("\nStopping manager")
            return

def main():

    start = time.time()

    global possibleValues, puzzle_fn
    possibleValues = ['1','2','3','4','5','6','7','8','9']
    genv()
    puzzle_fn = "sudokuRoyle.txt"
    global fa
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
        grid,pg,validDict = prevalidate(grid,possibleValues[:])
        start_time = time.time()
        bf,guesses,deductions = bruteForce(grid,validDict)
        printGrid(bf)
        print()
        print("Valid" if validate(bf) else "!!!! Invalid")
        print("Guesses: " + str(guesses) + " (Prefilled " + str(pg)+")")
        print("Deductions: " + str(deductions))
    print("Wall time: " + str(time.time() - start) + " seconds")
main()
# cProfile.run("main()")
