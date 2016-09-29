#!/usr/bin/python3

import sys
import time
import re
import random
import operator

sidelen = 8

ids = ['o','x']
MAX_LEVEL = 4

def isCorner(pos):
    return pos//8 == 0 and pos%8 == 0
def isEdge(pos):
    return pos//8 == 0 or pos%8 == 0
def isCloseEdge(pos):
    return pos//8 == 1 or pos//8 == 6 or pos%8 == 1 or pos%8 == 6
def isCloseCorner(pos):
    return (pos//8 == 1 or pos//8 == 6) and (pos%8 == 6 or pos%8 == 1)

def scaledNumPossibleAfterMove(grid,id):
    pos = 10-len(possiblemoves(grid,ids[id]))
    return pos

def min_play(board,id,level):
    opid = 1-id
    idl = ids[id]
    if(level >= MAX_LEVEL):
        # return 64 - board.count(ids[1-id])
        # return board.count(idl)
        # return board.count(idl) - board.count(ids[1-id])
        return board.count(idl) - board.count(ids[opid])
    moves_dict = possiblemoves(board,idl)
    moves = list(moves_dict.keys())
    if not moves:
        # return board.count(idl)
        # return board.count(idl) - board.count(ids[1-id])
        return board.count(idl) - board.count(ids[opid])
        # return board.count(ids[ACTUAL]) - board.count(ids[1-ACTUAL])
    best_score = float('inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],idl)
        score = max_play(clone,opid,level+1)
        if(score > best_score):
            best_move = move
            best_score = score
    return best_score

def max_play(board,id,level):
    opid = 1-id
    idl = ids[id]
    if(level >= MAX_LEVEL):
        # return 64 - board.count(ids[1-id])
        # return board.count(idl)
        # return board.count(idl) - board.count(ids[1-id])
        # return board.count(ids[ACTUAL]) - board.count(ids[1-ACTUAL])
        return board.count(idl) - board.count(ids[opid])
    moves_dict = possiblemoves(board,idl)
    moves = list(moves_dict.keys())
    if not moves:
        # return board.count(idl)
        # return board.count(idl) - board.count(ids[1-id])
        # return board.count(ids[ACTUAL]) - board.count(ids[1-ACTUAL])
        return board.count(idl) - board.count(ids[opid])
    best_score = float('-inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],idl)
        score = min_play(clone,opid,level+1)
        if(score < best_score):
            best_move = move
            best_score = score
    return best_score

def minimax(board,id,moves,moves_dict,scores,level=0):
    idl = ids[id]
    # moves_dict = possiblemoves(board,idl)
    # moves = list(moves_dict.keys())
    # print(moves)
    best_move = moves[0]
    print(best_move)
    best_score = float('-inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],idl)
        score = min_play(clone,1-id,level+1)*1000 + scores[move]
        # print("SCORE: {}, {}".format(score,scores[move]))
        if score > best_score:
            best_move = move
            print(best_move)
            best_score = score
    return best_move
    

def bestMove(grid,possible,id,debug=True):
    turns = len(grid.replace('.','')) - 4
    scores = {}
    for pos in possible.keys():
        scores[pos] = 10*scaledNumPossibleAfterMove(mv(grid,pos,possible[pos],ids[id]),1-id)
        if(scores[pos] == 100): return pos
        scores[pos] += len(possible[pos]) * 500
        if isCorner(pos): scores[pos] += 10000
        elif isEdge(pos): scores[pos] += 2000
        elif isCloseEdge(pos): scores[pos] -= 5000
        elif isCloseCorner(pos): scores[pos] -= 10000
    if debug: print(scores)
    moves = [x[0] for x in sorted(scores.items(), key=operator.itemgetter(1), reverse=True)]
    return minimax(grid,id,moves,possible,scores,0)

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

def mv(board,move,positions,id):
    lboard = list(board)
    for pos in positions:
        lboard[pos] = id
    return "".join(lboard)

def main():
    if(len(sys.argv) < 3): return
    board = sys.argv[1].lower()
    # printboard(board)
    # print()

    p = 0
    id = ids.index(sys.argv[2].lower())
    moves = 0

    mode = -1
    computer = True

    possible = possiblemoves(board,ids[id])
    if not possible:
        print("No moves to play")
        return
    move = bestMove(board,possible,id,False)
    # move = minimax(board,id)
    # move = next(iter(possible.keys()))
    print(move)
main()
