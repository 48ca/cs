#!/usr/bin/python3

import sys

sidelen = 8

def printboard(board):
    printmap = {
        'o': "O",
        'x': "\x1b[30;1mX\x1b[0m",
        '.': ".",
        'X': "\x1b[31;1mX\x1b[0m",
        'O': "\x1b[31;1mO\x1b[0m"
    }
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

def up(board,pos,ipos,sym):
    while pos//8 >= 0:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos -= 8
def upleft(board,pos,ipos,sym):
    while pos//8 >= 0 and ipos%8 + (pos - ipos) >= 0:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos -= 9
def upright(board,pos,ipos,sym):
    while pos//8 >= 0 and ipos%8 + (pos - ipos) < 8:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos -= 7
def downright(board,pos,ipos,sym):
    while pos//8 < 8 and ipos%8 + (pos - ipos) < 8:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos += 9
def downleft(board,pos,ipos,sym):
    while pos//8 < 8 and ipos%8 + (pos - ipos) >= 0:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos += 7
def down(board,pos,ipos,sym):
    while pos//8 < 8:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos += 8
def left(board,pos,ipos,sym):
    while pos%8 >= 0:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos -= 1
def right(board,pos,ipos,sym):
    while pos%8 < 8:
        if ipos != pos and board[pos] == sym: break
        if board[pos] == '.': return pos
        else: pos += 1
dird = {'u':up,'ur':upright,'ul':upleft,'dr':downright,'dl':downleft,'d':down,'l':left,'r':right}

def possiblemoves(board,id):
    pos = 0
    ret = set()
    while True:
        pos = board.find(id,pos)
        if pos < 0: return ret
        poss = positionsaround(board,pos,id)
        for pa in poss:
            direction = poss[pa]
            adding = dird[direction](board,pos,pos,id)
            if adding:
                ret.add(adding)
        pos += 1
    return pm

#### END MOVE FINDER

board = sys.argv[1]
if len(board) != 64: board = "."*64
printboard(board)

if len(sys.argv) < 3:
    id = 'x'
else: id = sys.argv[2].lower()
possible = possiblemoves(board,id)
for move in possible:
    board = board[:move] + id.upper() + board[1+move:]
printboard(board)
