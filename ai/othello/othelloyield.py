#!/usr/bin/python3

import sys
import time

sidelen = 8

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
    while pos//8 > 0:
        pos -= 8
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def upleft(board,pos,sym):
    while pos//8 > 0 and pos%8 > 0:
        pos -= 9
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def upright(board,pos,sym):
    while pos//8 > 0 and pos%8 < 7:
        pos -= 7
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def downright(board,pos,sym):
    while pos//8 < 7 and pos%8 < 7:
        pos += 9
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def downleft(board,pos,sym):
    while pos//8 < 7 and pos%8 > 0:
        pos += 7
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def down(board,pos,sym):
    while pos//8 < 7:
        pos += 8
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def left(board,pos,sym):
    while pos%8 > 0:
        pos -= 1
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
def right(board,pos,sym):
    while pos%8 < 7:
        pos += 1
        yield pos
        if board[pos] == sym: return None
        if board[pos] == '.': break
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
            if adding and next(adding):
                adding = list(adding)
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
        lboard[pos] = id.upper()
    return "".join(lboard)

if len(sys.argv)<2 or len(sys.argv[1]) != 64:
    board = "."*27
    board += "ox......xo"
    board += "."*27
else: board = sys.argv[1]
printboard(board)
print()

p = 0
ids = ['o','x']
id = 0
moves = 0

mode = -1
computer = True

if len(sys.argv)>2:
    if sys.argv[2] == '2':
        mode = 2
        computer = False
    if sys.argv[2] == '1':
        mode = 1
        computer = False

while board.find('.') > -1 and p < 2:
    possible = possiblemoves(board,ids[id])
    if not possible:
        p += 1
        print("{} passed on move {}".format(ids[id],moves+1))
        id = 1-id
        continue
    if mode != id and not computer:
        move = input("As {} (row, col): ".format(ids[id].upper()))
        try:
            move = int(move[-1]) + int(move[0])*8
        except Exception:
            print("Invalid move")
            continue
    else: move = max(possible.keys(), key=lambda d: len(possible[d]))
    if move not in possible:
        print("Invalid move")
        continue
    print()
    moves += 1
    # move = next(iter(possible.keys()))
    board = mv(board,move,possible[move],ids[id])
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
