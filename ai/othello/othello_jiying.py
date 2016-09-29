#!/usr/bin/env python3

import random
import sys
string = ""
tieNum = 0
smartWin = 0
dumbWin = 0
"""
def createBoard(board):
    for y in range(8):
        print(y, end=" | ")
        for x in range(8):
            print('%s' % (board[x][y]), end=' ')
        print("| " + str(y))
    print('   -----------------')
    print('    0 1 2 3 4 5 6 7')
"""

def replaceStringBoard(board):
    i = 0
    for x in range(8):
        for y in range(8):
            board[x][y] = string[i]
            i = i + 1
    return board

def resetBoard():
    board = []
    for i in range(8):
        board.append(['.'] * 8)
    return board

def getValidPositions(board, tile, xstart, ystart):
    if board[xstart][ystart] != '.' or not inBoundBoard(xstart, ystart):
        return False
    board[xstart][ystart] = tile
    if tile == 'X':
        otherTile = 'O'
    else:
        otherTile = 'X'
    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if inBoundBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not inBoundBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not inBoundBoard(x, y):
                    break
            if not inBoundBoard(x, y):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])
    board[xstart][ystart] = '.'
    if len(tilesToFlip) == 0:
        return False
    return tilesToFlip

def inBoundBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <=7

def getBoardCopy(board):
    dupeBoard = resetBoard()
    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]
    return dupeBoard

def createDupeValid(board, tile):
    dupeBoard = getBoardCopy(board)
    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = '*'
    return dupeBoard

def getValidMoves(board, tile):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if getValidPositions(board, tile, x, y) != False:
                validMoves.append([x, y])
    return validMoves

def getScore(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'X':
                xscore += 1
            if board[x][y] == 'O':
                oscore += 1
    return {'X':xscore, 'O':oscore}

def makeMove(board, tile, xstart, ystart):
    tilesToFlip = getValidPositions(board, tile, xstart, ystart)
    if tilesToFlip == False:
        return False
    board[xstart][ystart] = tile
    for x, y in tilesToFlip:
        board[x][y] = tile
    return True

def cornerCheck(x, y):
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)

def getPlayerMove(board, playerTile):
    DIGITS1TO8 = '0 1 2 3 4 5 6 7'.split()
    while True:
        print('What move (xy)?? If you need help type hints. If you wish to pass then type pass. If you wish to quit then type quit.')
        move = input().lower()
        if move == 'quit':
            return 'quit'
        if move == 'hints':
            return 'hints'
        if move == 'pass':
            return 'pass'
        if(move == 'fx'):
            return 'FX'
        elif(move == 'fy'):
            return 'FY'
        elif(move == 'fo'):
            return 'FO'
        elif(move == 'fd'):
            return 'FD'
        elif(move == 'rr'):
            return 'RR'
        elif(move == 'rl'):
            return 'RL'
        elif(move == 'r2'):
            return 'R2'
        elif(move == 'i'):
            return 'I'
        if len(move) == 3 and move[0] in DIGITS1TO8 and move[1] not in DIGITS1TO8 and move[2] in DIGITS1TO8:
            y = int(move[0])
            x = int(move[2])
            if getValidPositions(board, playerTile, x, y) == False:
                print("Move is not possible")
                continue
            else:
                break
        else:
            print('Invalid Input')
    return [x, y]

def getComputerMoveSmart(board, computerTile, oppositeTile):
    if(string == startingString):
        if(computerTile == "X"):
            bestMove = [3, 5]
        elif(computerTile == "O"):
            bestMove = [4, 5]
        return bestMove
    else:
        """
        possibleMoves = getValidMoves(board, computerTile)
        random.shuffle(possibleMoves)
        for x, y in possibleMoves:
            if cornerCheck(x, y):
                return [x, y]
        bestScore = -1
        for x, y in possibleMoves:
            leastMoves = 0
            dupeBoard = getBoardCopy(board)
            makeMove(dupeBoard, computerTile, x, y)
            possibleCorners = getValidMoves(dupeBoard, oppositeTile)
            if len(possibleMoves) > 1:
                for x1, y1 in possibleCorners:
                    if cornerCheck(x1,y1):
                        if [x, y] in possibleMoves:
                            possibleMoves.remove([x, y])
                            """
        bestMove = minimax(board, computerTile, oppositeTile)
        print(bestMove)
        return bestMove

def minimax(board, computerTile, oppositeTile):
    bestMove = [0, 0]
    possibleMoves = getValidMoves(board, computerTile)
    bestScore = 0
    score = 0
    for move in possibleMoves:
        x, y = move
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = minPlay(dupeBoard, oppositeTile, computerTile, 0)
        if score > bestScore:
            bestMove = move
            bestScore = score
    return bestMove

def minPlay(board, computerTile, oppositeTile, depth):
    #bestMove = [0, 0]
    scores = getScore(board)
    totalScore = scores[computerTile] + scores[oppositeTile]
    if(totalScore == 64 or depth == 4):
        return scores[computerTile]
    possibleMoves = getValidMoves(board, computerTile)
    bestScore = 999999999999
    for move in possibleMoves:
        x, y = move
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = maxPlay(dupeBoard, oppositeTile, computerTile, depth + 1)
        if score < bestScore:
            bestMove = move
            bestScore = score
    return bestScore

def maxPlay(board, computerTile, oppositeTile, depth):
    #bestMove = [0, 0]
    scores = getScore(board)
    totalScore = scores[computerTile] + scores[oppositeTile]
    if(totalScore == 64 or depth == 4):
        return scores[computerTile]
    possibleMoves = getValidMoves(board, computerTile)
    bestScore = 0
    for move in possibleMoves:
        x, y = move
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = minPlay(dupeBoard, oppositeTile, computerTile, depth + 1)
        if score > bestScore:
            bestMove = move
            bestScore = score
    return bestScore

def getComputerMoveDumb(board, computerTile, oppositeTile):
    possibleMoves = getValidMoves(board, computerTile)
    bestMove = random.choice(possibleMoves)
    return bestMove

def showPoints(playerTile, otherPlayerTile):
    scores = getScore(mainBoard)
    print(playerTile + " has " + str(scores[playerTile]) + " points. " + otherPlayerTile + " has " + str(scores[otherPlayerTile]) + " points.")

def getRL(board):
    duped = list(zip(*board[::-1]))
    createBoard(duped)
def getRR(board):
    duped = list(zip(*board[::-1]))
    duped = list(zip(*duped[::-1]))
    duped = list(zip(*duped[::-1]))
    createBoard(duped)
def getR2(board):
    duped = list(zip(*board[::-1]))
    duped = list(zip(*duped[::-1]))
    createBoard(duped)
def flipx(board):
    duped = list(board[::-1])
    createBoard(duped)
def flipy(board):
    duped = resetBoard()
    for i in range(64):
        x = (7-i%8) + 8*(i//8)
        duped[i//8][7-i%8] = board[i//8][i%8]
    createBoard(duped)
def flipxy(board):
    duped = resetBoard()
    for i in range(64):
        duped[7-i%8][7-i//8] = board[i//8][i%8]
    createBoard(duped)
def flipyx(board):
    duped = resetBoard()
    for i in range(64):
        duped[i%8][7-i//8] = board[7-i//8][i%8]
    createBoard(duped)
def getOriginal(board):
    createBoard(board)
string = sys.argv[1]
tile = sys.argv[2]
side = ""
#string = ".........................................................ooxox.."
startingString = "...........................xo......ox..........................."
#string = ".xxxxxxxoxxxxxxxxxxxxxxxxxxxxoxx.xxxoxxxxxxxxxxxxxxxxxxoxxxxxxxx"
if(tile.upper() == "X"):
    computer1Tile = 'X'
    computer2Tile = 'O'
    turn = "player"
    nextTurn = "computer"
elif(tile.upper() == "O"):
    computer1Tile = 'O'
    computer2Tile = 'X'
    turn = "computer"
    nextTurn = "player"
string = string.upper()
mainBoard = resetBoard()
mainBoard = replaceStringBoard(mainBoard)
startingBoard = mainBoard
x, y = getComputerMoveSmart(mainBoard, computer1Tile, computer2Tile)
index = x*8+y
print(index)
