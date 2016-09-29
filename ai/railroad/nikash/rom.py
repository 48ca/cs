import sys, urllib.request, time, queue
from math import pi, acos, sin, cos

startTime = time.clock()

def getstations():
	link = "https://academics.tjhsst.edu/compsci/ai/romNodes.txt"
	hfile = urllib.request.urlopen(link)	#accesses link
	stationslatlng = {}
	for line in hfile:
		myline = line.decode()[:-1]
		mycomponents = myline.split()
		latlng = [float(mycomponents[2]), float(mycomponents[1])]
		stationslatlng[mycomponents[0]] = latlng
	return stationslatlng

def calcd(y1,x1, y2,x2):
   y1  = float(y1)
   x1  = float(x1)
   y2  = float(y2)
   x2  = float(x2)
   R   = 3958.76 # miles
   y1 *= pi/180.0
   x1 *= pi/180.0
   y2 *= pi/180.0
   x2 *= pi/180.0
   if x2 - x1 == 0: return 0
   return acos( sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(x2-x1) ) * R

def getedgesnoweight(stationslatlng):
	link = "https://academics.tjhsst.edu/compsci/ai/romEdges.txt"
	hfile = urllib.request.urlopen(link)	#accesses link
	stationsdictnoweight = {}
	for word in stationslatlng:
		stationsdictnoweight[word] = []

	for line in hfile:
		myline = line.decode()[:-1]
		mycomponents= myline.split()
		start = mycomponents[0]
		end = mycomponents[1]
		stationsdictnoweight[start].append(end)
		stationsdictnoweight[end].append(start)
	return stationsdictnoweight

def getedges(stationslatlng):
	link = "https://academics.tjhsst.edu/compsci/ai/romEdges.txt"
	hfile = urllib.request.urlopen(link)	#accesses link
	stationsdict = {}
	for word in stationslatlng:
		stationsdict[word] = {}

	for line in hfile:
		myline = line.decode()[:-1]
		mycomponents= myline.split()
		start = mycomponents[0]
		end = mycomponents[1]
		startlatlng = stationslatlng[start]
		endlatlng = stationslatlng[end]
		weight = calcd(startlatlng[1], startlatlng[0], endlatlng[1], endlatlng[0])
		stationsdict[start][end] = weight
		stationsdict[end][start] = weight
	return stationsdict

def getkey(stationslatlng):
	link = "https://academics.tjhsst.edu/compsci/ai/romFullNames.txt"
	hfile = urllib.request.urlopen(link)	#accesses link
	stationskey = {}

	for line in hfile:
		mycity = line.decode()[:-1]
		abbr = mycity[0]
		#stationskey[mycity] = abbr
		stationskey[abbr] = mycity
	return stationskey

def BFS(start, end, stationsdictnoweight):
	visited = set([])
	pathdictionary = {}
	pathdictionary[start] = []
	countqueue = 0
	myqueue = queue.Queue()
	myqueue.put(start)
	while not myqueue.empty():
		previous = myqueue.get()
		countqueue+=1
		for neighbor in stationsdictnoweight[previous]:
			if neighbor not in visited:
				myqueue.put(neighbor)
				templist = []
				for word in pathdictionary[previous]:
					templist.append(word)
				templist.append(neighbor)
				pathdictionary[neighbor] = templist
				visited.add(neighbor)
				if neighbor == end:
					return (pathdictionary[neighbor], countqueue)
	return (pathdictionary[end], countqueue)

def dijkstra(start, end, stationsdict):
	minimumdistances = {}
	minimumpaths = {}
	minimumdistances[start] = 0
	minimumpaths[start] = []
	visited = set([])
	tovisit = set([])
	maxsetsize = 0
	tovisit.add(start)
	while not len(tovisit) == 0:
		distance = 100000
		for element in tovisit:
			if minimumdistances[element] < distance:
				distance = minimumdistances[element]
				previous = element
		tovisit.remove(previous)
		for neighbor in stationsdict[previous]:
			if neighbor not in visited:
				minimumdistances[neighbor] = minimumdistances[previous] + stationsdict[previous][neighbor]
				templist = []
				for vertex in minimumpaths[previous]:
					templist.append(vertex)
				templist.append(neighbor)
				minimumpaths[neighbor] = templist
				tovisit.add(neighbor)
				if(len(tovisit) > maxsetsize):
					maxsetsize = len(tovisit)
			if neighbor == end:
				return (minimumpaths[end], minimumdistances[end], len(visited))
			visited.add(neighbor)
	return (minimumpaths[end], minimumdistances[end], len(visited))

def astar(start, end, stationsdict, stationslatlng):
	gcosts = {start: 0}
	hcosts = {}
	firstlatlong = stationslatlng[start]
	secondlatlong = stationslatlng[end]
	hcosts[start] = calcd(firstlatlong[1], firstlatlong[0], secondlatlong[1], secondlatlong[0])
	fcosts = {}
	fcosts[start] = 0
	path = {start: []}
	opened = set([])
	opened.add(start)
	closed = set([])
	while not len(opened)==0:
		distance = 100000
		for element in opened:
			if fcosts[element] < distance:
				distance = fcosts[element]
				before = element
		opened.remove(before)
		for neighbor in stationsdict[before]:
			if neighbor == end:
				return (path[neighbor], fcosts[neighbor], len(closed))
			templist = []
			for vertex in path[before]:
				templist.append(vertex)
			templist.append(neighbor)
			#path->templist
			tempg = gcosts[before] + stationsdict[before][neighbor]
			firstlatlong = stationslatlng[neighbor]
			secondlatlong = stationslatlng[end]
			temph = calcd(firstlatlong[1], firstlatlong[0], secondlatlong[1], secondlatlong[0])
			tempf = temph + tempg
			if neighbor in opened and fcosts[neighbor] < tempf:
				break;
			elif (neighbor in closed and fcosts[neighbor] < tempf):
				break;
			else:
				gcosts[neighbor] = tempg
				hcosts[neighbor] = temph
				fcosts[neighbor] = tempf
				path[neighbor] = templist
				opened.add(neighbor)
		closed.add(before)
		print (before)
	return (path[neighbor], fcosts[neighbor], len(closed))

	"""while not len(opened)==0:
		distance = 100000
		for element in opened:
			if fcosts[element] < distance:
				distance = fcosts[element]
				before = element
		opened.remove(before)
		for neighbor in stationsdict[before]:
			if neighbor not in closed:
				templist = []
				for vertex in path[before]:
					templist.append(vertex)
				templist.append(neighbor)
				path[neighbor] = templist
				gcosts[neighbor] = gcosts[before] + stationsdict[before][neighbor]
				firstlatlong = stationslatlng[neighbor]
				secondlatlong = stationslatlng[end]
				hcosts[neighbor] = calcd(firstlatlong[1], firstlatlong[0], secondlatlong[1], secondlatlong[0])
				fcosts[neighbor] = hcosts[neighbor] + gcosts[neighbor]
				opened.add(neighbor)
				if neighbor == end:
					return (path[neighbor], fcosts[neighbor], len(closed))
			closed.add(before)
	return (path[neighbor], fcosts[neighbor], len(closed))"""


stationslatlng = getstations()
stationsdictnoweight = getedgesnoweight(stationslatlng)
stationsdict = getedges(stationslatlng)
stationskey = getkey(stationslatlng)

print ("")
if(len(sys.argv)==3):
	"""try:

		startcity=sys.argv[1]
		endcity=sys.argv[2]
		start = startcity[0].upper()
		end = endcity[0].upper()

		pathbetween, distancebetweenunrounded, countqueue = astar(start, end, stationsdict, stationslatlng)
		distancebetween = round(distancebetweenunrounded, 1)
		print ("A-Star")
		print ("The Path From " + startcity + " to " + endcity + " is:")
		pathstring = ""
		for city in pathbetween:
			pathstring += stationskey[city] + " "
		print (pathstring)
		print ("The Distance Between " + startcity + " and " + endcity + " is:")
		print (distancebetween)
		print ("The Number of Vertices Visited is:")
		print (countqueue)
		
		
	except KeyError:
		print (start + " and " + end + " are not connected.") """

	startcity=sys.argv[1]
	endcity=sys.argv[2]
	start = startcity[0].upper()
	end = endcity[0].upper()

	pathbetween, distancebetweenunrounded, countqueue = astar(start, end, stationsdict, stationslatlng)
	distancebetween = round(distancebetweenunrounded, 1)
	print ("A-Star")
	print ("The Path From " + startcity + " to " + endcity + " is:")
	pathstring = ""
	for city in pathbetween:
		pathstring += stationskey[city] + " "
	print (pathstring)
	print ("The Distance Between " + startcity + " and " + endcity + " is:")
	print (distancebetween)
	print ("The Number of Vertices Visited is:")
	print (countqueue)
	

print ("")
print ("Runtime: " + str(time.clock() - startTime))
