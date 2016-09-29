#!/usr/bin/python3

import sys
import time
import re
import random
import operator

sidelen = 8

identities = {
    "i":list(range(64)),
    "rl":[8*(7-i%8) + i//8 for i in range(64)],
    "rr":[8*(i%8) + 7-(i//8) for i in range(64)],
    "r2":[8*(7-i//8) + 7-i%8 for i in range(64)],
    "fx":[8*(i//8) + (7-i%8) for i in range(64)],
    "fy":[8*(7-i//8) + i%8 for i in range(64)],
    "fd":[8*(7-i%8) + (7-i//8) for i in range(64)],
    "fo":[8*(i%8) + (i//8) for i in range(64)]
}

second_move = {
    "...........................xo.....xxx...........................": 42,
    "...................x.......xx......xo...........................": 18,
    "...........................xxx.....ox...........................": 21,
    "...........................ox......xx.......x...................": 45
}

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
        return board.count(idl) - board.count(ids[1-id])
        # return board.count(idl)
    moves_dict = possiblemoves(board,idl)
    moves = list(moves_dict.keys())
    if not moves:
        # return board.count(idl)
        return board.count(idl) - board.count(ids[1-id])
    best_score = float('inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],id).lower()
        score = max_play(clone,opid,level+1)
        if(score < best_score):
            best_move = move
            best_score = score
    return best_score

def max_play(board,id,level):
    opid = 1-id
    idl = ids[id]
    if(level >= MAX_LEVEL):
        # return 64 - board.count(ids[1-id])
        # return board.count(idl)
        return board.count(idl) - board.count(ids[1-id])
    moves_dict = possiblemoves(board,idl)
    moves = list(moves_dict.keys())
    if not moves:
        # return board.count(idl)
        return board.count(idl) - board.count(ids[1-id])
    best_score = float('-inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],id).lower()
        score = min_play(clone,opid,level+1)
        if(score > best_score):
            best_move = move
            best_score = score
    return best_score

def minimax(board,id,moves,moves_dict,scores,level=0):
    idl = ids[id]
    # moves_dict = possiblemoves(board,idl)
    # moves = list(moves_dict.keys())
    # print(moves)
    best_move = moves[0]
    # print(best_move)
    best_score = float('-inf')
    for move in moves:
        clone = mv(board,move,moves_dict[move],id).lower()
        score = min_play(clone,1-id,level+1)*500 + scores[move]
        # score = min_play(clone,1-id,level+1)# *200 + scores[move]
        print("SCORE: {}, {}".format(score,scores[move]))
        if score > best_score:
            best_move = move
            # print(best_move)
            best_score = score
    return best_move
    

def bestMove(grid,possible,id,debug=True):
    # turns = len(grid.replace('.','')) - 4
    scores = {}
    for pos in possible.keys():
        scores[pos] = 10*scaledNumPossibleAfterMove(mv(grid,pos,possible[pos],id).lower(),1-id)
        if(scores[pos] == 100): return pos
        scores[pos] += len(possible[pos]) * 500
        if isCorner(pos): scores[pos] += 10000
        elif isEdge(pos): scores[pos] += 2000
        elif isCloseEdge(pos): scores[pos] -= 5000
    if debug: print(scores)
    moves = [x[0] for x in sorted(scores.items(), key=operator.itemgetter(1), reverse=True)]
    # moves = list(possible.keys())
    # print(moves)
    return minimax(grid,id,moves,possible,scores,0)
    # return max(scores, key=lambda d: scores[d])

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
            sys.stdout.write(" {}".format(printmap[board[j*sidelen+i]]))
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

def mv(board,move,positions,id,show=True):
    lid = ids[id]
    lboard = list(board)
    for pos in positions:
        if show:
            lboard[pos] = lid.upper()
        else:
            lboard[pos] = lid
    return "".join(lboard)

def main():
    if len(sys.argv)<2 or len(sys.argv[1]) != 64:
        board = "."*27
        board += "xo......ox"
        board += "."*27
    else: board = sys.argv[1]
    printboard(board)
    print()

    p = 0
    id = 1
    moves = 0

    mode = -1
    computer = True

    if len(sys.argv)>2:
        if sys.argv[2] == '2':
            mode = 2
            computer = False
        if sys.argv[2] == '0':
            mode = 0
            computer = False
        if sys.argv[2] == '1':
            mode = 1
            computer = False

    while board.find('.') > -1 and p < 2:
        possible = possiblemoves(board,ids[id])
        if not possible:
            p += 1
            moves += 1
            print("{} passed on move {}".format(ids[id].upper(),moves))
            id = 1-id
            continue
        else:
            p = 0
        if mode != id and not computer:
            move = input("As {} (row, col): ".format(ids[id].upper()))
            try:
                if move.lower() in identities:
                    print()
                    printboard("".join([
                        board[i] for i in identities[move]
                    ]))
                    print()
                    continue
                if move.lower() == ".":
                    print(possible)
                    continue
                if len(re.sub(r"[^0-9A-Za-z]","",move)) != 2: raise Exception
                move = int(move[-1])*8 + int(move[0])
            except Exception:
                print("Invalid move")
                continue
        else:
            if id == 0 and mode == -1: # when id == 'o'
                move = random.choice(list(possible.keys()))
            else:
                move = bestMove(board,possible,id)
        if move not in possible:
            print("Invalid move")
            continue
        print()
        moves += 1
        # move = next(iter(possible.keys()))
        board = mv(board,move,possible[move],id)
        printboard(board,moves)
        print()
        board = board.lower()
        id = 1-id

    os = board.count('o')
    xs = board.count('x')
    winner = 'No one'
    if os > xs:
        winner = 'O'
    elif os < xs:
        winner = 'X'
    print()
    print("{} won in {} moves".format(winner,moves))
    n = min(os,xs)
    print("{} - {}".format(64-n,n))
    # print()
    # printboard(board,moves)
def runcomp(trials):
    win = 0
    for i in range(trials):
        for id in range(2):
            board = "."*27 + "xo......ox" + "."*27
            id = 1
            moves = 0
            p = 0
            while(board.find('.') > -1 and p < 2):
                possible = possiblemoves(board,ids[id])
                if not possible:
                    p += 1
                    moves += 1
                    id = 1-id
                    continue
                else:
                    p = 0
                if id == 0:
                    move = random.choice(list(possible.keys()))
                else:
                    move = bestMove(board,possible,id,False)
                board = mv(board,move,possible[move],id)
                id = 1 - id
                board = board.lower()
            os = board.count('o')
            xs = board.count('x')
            winner = 'No one'
            if os > xs:
                winner = 'O'
            elif os < xs:
                winner = 'X'
                win += 1
            n = min(os,xs)
            if(n < 10 ):
                print("\x1b[31;1m{} :: {} won :: {} - {}\x1B[0m".format(i+1,winner,64-n,n))
            else:
                print("{} : {} won :: {} - {}".format(i+1,winner,64-n,n))
    print("X won {}% of the time".format(50*win/trials))

try:
    runcomp(int(sys.argv[1]))
except Exception:
    main()
