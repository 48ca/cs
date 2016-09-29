#!/usr/bin/python3

import sys
import time
import re

sidelen = 8

def bestMove(possible):
    edges = []
    score = 0
    pos = -1
    for pos in possible.keys():
        print(pos)
        if isCorner(pos): return pos
        elif isEdge(pos): edges.append(pos)
    if edges:
        return max(edges, key=lambda d: len(possible[d]))
    return max(possible.keys(), key=lambda d: len(possible[d]))

def printboard(board,turn=0):
    printmap = {
        'o': "O",
        'x': "\x1b[30;1mX\x1b[0m",
        '.': ".",
        'X': "\x1b[31;1mX\x1b[0m",
        'O': "\x1b[31;1mO\x1b[0m"
    }
    sys.stdout.write("       TURN {:3d}   \n".format(turn))
    sys.stdout.write("   -----------------\n")
    for i in range(sidelen):
        sys.stdout.write("{} |".format(i))
        for j in range(sidelen):
            sys.stdout.write(" {}".format(printmap[board[i*sidelen+j]]))
        sys.stdout.write(" | {}\n".format(i))
    sys.stdout.write("   -----------------\n")
    sys.stdout.write("   ")
    for i in range(sidelen):
        sys.stdout.write(" {}".format(i))
    sys.stdout.write("\n")

#### MOVE FINDER

def positionsaround(board,pos,sym):
    ret = {}
    m8l = pos%8 < 7
    m8g = pos%8 > 0
    d8l = pos//8 < 7
    d8g = pos//8 > 0
    if d8g:
        ret[pos-8] = 'u'
        if m8l:
            ret[pos-7] = 'ur'
        if m8g:
            ret[pos-9] = 'ul'
    if d8l:
        ret[pos+8] = 'd'
        if m8l:
            ret[pos+9] = 'dr'
        if m8g:
            ret[pos+7] = 'dl'
    if m8l:
        ret[pos+1] = 'r'
    if m8g:
        ret[pos-1] = 'l'
    for pos in ret.copy():
        if board[pos] == '.' or board[pos] == sym: del ret[pos]
    return ret

def up(board,pos,sym):
    positions = []
    while pos//8 > 0:
        pos -= 8
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def upleft(board,pos,sym):
    positions = []
    while pos//8 > 0 and pos%8 > 0:
        pos -= 9
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def upright(board,pos,sym):
    positions = []
    while pos//8 > 0 and pos%8 < 7:
        pos -= 7
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def downright(board,pos,sym):
    positions = []
    while pos//8 < 7 and pos%8 < 7:
        pos += 9
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def downleft(board,pos,sym):
    positions = []
    while pos//8 < 7 and pos%8 > 0:
        pos += 7
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def down(board,pos,sym):
    positions = []
    while pos//8 < 7:
        pos += 8
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def left(board,pos,sym):
    positions = []
    while pos%8 > 0:
        pos -= 1
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
def right(board,pos,sym):
    positions = []
    while pos%8 < 7:
        pos += 1
        positions.append(pos)
        if board[pos] == sym: break
        if board[pos] == '.': return positions
dird = {'u':up,'ur':upright,'ul':upleft,'dr':downright,'dl':downleft,'d':down,'l':left,'r':right}

def possiblemoves(board,id):
    pos = 0
    ret = {}
    while True:
        pos = board.find(id,pos)
        if pos < 0: return ret
        poss = positionsaround(board,pos,id)
        for pa in poss:
            direction = poss[pa]
            adding = dird[direction](board,pos,id)
            if adding:
                toadd = adding[-1]
                if toadd not in ret:
                    ret[toadd] = []
                ret[toadd] += adding
        pos += 1
    return ret

#### END MOVE FINDER

def isCorner(pos):
    return pos//8 == 0 and pos%8 == 0
def isEdge(pos):
    return pos//8 == 0 or pos%8 == 0

def mv(board,move,positions,id):
    lboard = list(board)
    for pos in positions:
        lboard[pos] = id.upper()
    return "".join(lboard)

def main():
    if(len(sys.argv) < 3): return
    board = sys.argv[1].lower()
    # printboard(board)
    # print()

    p = 0
    ids = ['o','x']
    id = ids.index(sys.argv[2].lower())
    moves = 0

    mode = -1
    computer = True

    possible = possiblemoves(board,ids[id])
    if not possible:
        print("No moves to play")
        return
    move = bestMove(possible)
    # move = next(iter(possible.keys()))
    # print(move)
main()
