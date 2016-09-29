#If possible, pick a corner, otherwise, pick the place that flips over the most tiles.

import sys, random, string
from random import shuffle

def findNeighbors(board):
	dictNeighbors = {}
	for row in range(8):
		for col in range(8):
			dictNeighbors[row*8+col] = set()
			if not row*8+col-1 < 0 and col!=0:
				dictNeighbors[row*8+col].add(row*8+col-1)
			if not row*8+col+1 > 63 and col!=7:
				dictNeighbors[row*8+col].add(row*8+col+1)
			if not (row-1)*8+col < 0 and row!=0:
				dictNeighbors[row*8+col].add((row-1)*8+col)
			if not (row+1)*8+col > 63 and row!=7:
				dictNeighbors[row*8+col].add((row+1)*8+col)
			if not ((row-1)*8+col-1 < 0 or (row-1)*8+col-1 > 63) and (row!=0 and col!=0):
				dictNeighbors[row*8+col].add((row-1)*8+col-1)
			if not ((row-1)*8+col+1 < 0 or (row-1)*8+col+1 > 63) and (row!=0 and col!=7):
				dictNeighbors[row*8+col].add((row-1)*8+col+1)
			if not ((row+1)*8+col-1 < 0 or (row+1)*8+col-1 > 63) and (row!=7 and col!=0):
				dictNeighbors[row*8+col].add((row+1)*8+col-1)
			if not ((row+1)*8+col+1 < 0 or (row+1)*8+col+1 > 63) and (row!=7 and col!=7):
				dictNeighbors[row*8+col].add((row+1)*8+col+1)
	return dictNeighbors

def inBoundaries(tempplace):
	if tempplace>-1 and tempplace<64:
		return True
	else:
		return False

def findAllowedMoves(board, turn):
	turnsymbol = turndict[turn]
	possibleplaces = set()
	turnplaces = set()
	for place in range(64):
		if board[place] == turnsymbol:
			turnplaces.add(place)
	for place in turnplaces:
		for neighbor in dictNeighbors[place]:
			if board[neighbor]==turndict[1-turn]:
				direction = neighbor - place
				tempplace = neighbor
				while inBoundaries(tempplace) and board[tempplace] == turndict[1-turn]:
					tempplace = tempplace + direction
				if (direction==8 or direction==-8) and not (inBoundaries(tempplace)):
					continue
				if (direction==1 or direction==-1) and (tempplace//8 != place//8):
					continue
				if (direction==9 or direction==-7) and (not (inBoundaries(tempplace)) or (tempplace%8 < place%8)):
					continue
				if (direction==7 or direction==-9) and (not (inBoundaries(tempplace)) or (tempplace%8 > place%8)):
					continue
				if inBoundaries(tempplace) and board[tempplace] == ".":
					possibleplaces.add(tempplace)
	return possibleplaces

def flipPieces(board, turn, place):
	dictdirections = {}
	dictdirectionsfinal = {}
	possibleplaces = set()
	for neighbor in dictNeighbors[place]:
		direction = neighbor - place
		tempplace = neighbor
		dictdirections[direction] = set()
		dictdirections[direction].add(tempplace)
		while inBoundaries(tempplace) and board[tempplace] == turndict[1-turn]:
			tempplace = tempplace + direction
			dictdirections[direction].add(tempplace)
		if (direction==8 or direction==-8) and not (inBoundaries(tempplace)):
			continue
		if (direction==1 or direction==-1) and (tempplace//8 != place//8):
			continue
		if (direction==9 or direction==-7) and (not (inBoundaries(tempplace)) or (tempplace%8 < place%8)):
			continue
		if (direction==7 or direction==-9) and (not (inBoundaries(tempplace)) or (tempplace%8 > place%8)):
			continue
		if inBoundaries(tempplace) and board[tempplace] == turndict[turn]:
			possibleplaces.add(tempplace)
			dictdirectionsfinal[direction] = dictdirections[direction]
	toturn = set()
	for mydirection in dictdirectionsfinal:
		for thing in dictdirectionsfinal[mydirection]:
			toturn.add(thing)
	return toturn

corners = set()
corners.add(0)
corners.add(7)
corners.add(56)
corners.add(63)
board = sys.argv[1]
turndict = {0:"X", 1:"O"}
turnsymbol = sys.argv[2]
turn = -1
for turnthing in turndict:
	if turndict[turnthing] == turnsymbol:
		turn = turnthing
dictNeighbors = findNeighbors(board)
possibleplaces = findAllowedMoves(board, turn)
placeScores = {}
for place in possibleplaces:								#random
	placeScores[place] = 1

for place in placeScores:									#corners *100
	if place in corners:
		placeScores[place]*=1000

for place in placeScores:									#places adjacent to corners /100 (unless corner is occupied)
	if place==1 or place==8 or place==6 or place==7 or place==48 or place==57 or place==55 or place==62:
		if place+1 in corners and board[place+1]==turndict[turn]:
			placeScores[place]*=100
		if place-1 in corners and board[place-1]==turndict[turn]:
			placeScores[place]*=100
		if place+8 in corners and board[place+8]==turndict[turn]:
			placeScores[place]*=100
		if place-8 in corners and board[place-8]==turndict[turn]:
			placeScores[place]*=100
		else:
			placeScores[place]/=100

for place in placeScores:									#places diagonal to corners /1000
	if place==9 or place==14 or place==49 or place==54:
		placeScores[place]/=1000

dictplaces = {}												#flips *amountOfFlips
for place in placeScores:
	for neighbor in dictNeighbors[place]:
		direction = neighbor - place
		tempset = set()
		while inBoundaries(neighbor) and board[neighbor]==turndict[1-turn]:
			tempset.add(neighbor)
			neighbor = neighbor + direction
			if (direction==8 or direction==-8) and not (inBoundaries(neighbor)):
				continue
			if (direction==1 or direction==-1) and (neighbor//8 != place//8):
				continue
			if (direction==9 or direction==-7) and (not (inBoundaries(neighbor)) or (neighbor%8 < place%8)):
				continue
			if (direction==7 or direction==-9) and (not (inBoundaries(neighbor)) or (neighbor%8 > place%8)):
				continue
		if inBoundaries(neighbor) and board[neighbor]==turndict[turn]:
			dictplaces[place] = tempset

for possibility in dictplaces:
	placeScores[possibility]*=(len(dictplaces[possibility]))

for place in placeScores:									#limit plays of next player
	boardtemp = board
	boardtemp = board[:place] + turndict[turn] + board[place+1:]
	otherpossiblemoves = findAllowedMoves(boardtemp, 1-turn)
	if 0 in otherpossiblemoves or 7 in otherpossiblemoves or 56 in otherpossiblemoves or 63 in otherpossiblemoves:
		placeScores[place]/=100

for place in placeScores:									#favor edges
	if place%8==0 or place%8==7 or place//8==0 or place//8==7:
		placeScores[place]*=10

turnsymbol = turndict[turn]
for place in placeScores:									#favor edges with corners more
	if place%8==0 and (board[0]==turnsymbol or board[56]==turnsymbol) or place%8==7 and (board[7]==turnsymbol or board[63]==turnsymbol) or place//8==0 and (board[0]==turnsymbol or board[7]==turnsymbol) or place//8==7 and (board[56]==turnsymbol or board[63]==turnsymbol):
		placeScores[place]*=100

for place in placeScores:									#dont play place if it will flip adjacent
	toturn = flipPieces(board, turn, place)
	if 9 in toturn or 14 in toturn or 49 in toturn or 54 in toturn:
		placeScores[place]/=1000
	if 1 in toturn or 8 in toturn or 6 in toturn or 7 in toturn or 48 in toturn or 57 in toturn or 55 in toturn or 62 in toturn:
		placeScores[place]/=100

print (placeScores)

favorablePlace=-1
favorableScore=-1
for place in placeScores:
	if placeScores[place] > favorableScore:
		favorableScore = placeScores[place]
		favorablePlace = place
print (favorablePlace)



