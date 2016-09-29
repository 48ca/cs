#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import re
import urllib
import os
import math

T = 12000

DEPTH_LIMIT = float('inf')
COL_TOL = float('inf')

STRONG_COLOR = [0,0,0] # [0,0,255]]
FOUND_COLOR = [0,0,0]
WEAK_COLOR = [0,0,0] # [255,0,0]

# CIRCLE_CANDEDACY_THRESHOLD= 140
CIRCLE_CANDEDACY_THRESHOLD= 90
# Lower is stronger
SET_REQ_LENGTH = 2
CIRCLE_THRESHOLD = .20
DIST = 10

LINE_THRESHOLD = .28
LINE_DIST = 30

EPSILON = .00000000001

cache_folder = "downloaded_images/"
output_folder = "outputs/"

def isanchor(url):
    return re.match("^https?:\/\/",url) # and re.match("\/[a-z0-9-_]+\.[a-z]+$",url)

def makeFolders(*args):
    for arg in args:
        if not os.path.exists(arg):
            os.makedirs(arg)

def waitForKeys(*keys):
    k = -1
    keys = set(keys)
    while k not in keys: k = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()

def setPixel(img, g, x, y):
    for i in range(3):
        img.itemset((y,x,i),g[i])

def main():

    """
    def adj(x,y,edges):
        return True
        # return edges[y,x][1] == 255 or edges[y-1,x][1] == 255 or edges[y-1,x-1][1] == 255 or edges[y-1,x+1][1] == 255 or edges[y,x+1][1] == 255 or edges[y,x-1][1] == 255 or edges[y+1,x][1] == 255 or edges[y+1,x-1][1] == 255 or edges[y+1,x+1][1] == 255
        # return edges[y,x] or edges[y-1,x] or edges[y-1,x-1] or edges[y-1,x+1] or edges[y,x+1] or edges[y,x-1] or edges[y+1,x] or edges[y+1,x-1] or edges[y+1,x+1]

    def fse(img,edges): # filter short edges
        for e in edges:
            x = e[1]
            y = e[0]
            if adj(x,y,edges):
                img[y,x] = [0,255,0]
    """

    def sobeledge(img,grey=True):
        ret = img.copy()
        h = img.shape[0]
        w = img.shape[1]
        y = 1

        if len(sys.argv) > 3:
            T = int(sys.argv[4])
        """
        edges = {}
        for i in range(h):
            edges[i,0] = False
            edges[i,w-1] = False
        for i in range(w):
            edges[0,i] = False
            edges[h-1,i] = False
        """
        while y < h-1:
            x = 1
            while x < w-1:
                # i = 1.0/16 * (img.item(y,x,0)*4 + img.item(y-1,x,0)*2 + img.item(y,x-1,0)*2 + img.item(y+1,x,0)*2 + img.item(y,x+1,0)*2 + img.item(y-1,x-1,0) + img.item(y-1,x+1,0) + img.item(y+1,x-1,0) + img.item(y+1,x+1,0))
                gx = -1 * img.item(y-1,x-1,0) - 2*img.item(y,x-1,0) - 1 * img.item(y+1,x-1,0) + img.item(y-1,x+1,0) + 2*img.item(y,x+1,0) + img.item(y+1,x+1,0)
                if not grey:
                    gx += -1 * img.item(y-1,x-1,1) - 2*img.item(y,x-1,1) - 1 * img.item(y+1,x-1,1) + img.item(y-1,x+1,1) + 2*img.item(y,x+1,1) + img.item(y+1,x+1,1)
                    gx += -1 * img.item(y-1,x-1,2) - 2*img.item(y,x-1,2) - 1 * img.item(y+1,x-1,2) + img.item(y-1,x+1,2) + 2*img.item(y,x+1,2) + img.item(y+1,x+1,2)
                    gx /= 3
                gy = -1 * img.item(y-1,x-1,0) - 2*img.item(y-1,x,0) - 1 * img.item(y-1,x+1,0) + img.item(y+1,x-1,0) + 2*img.item(y+1,x,0) + img.item(y+1,x+1,0)
                if not grey:
                    gy += -1 * img.item(y-1,x-1,1) - 2*img.item(y-1,x,1) - 1 * img.item(y-1,x+1,1) + img.item(y+1,x-1,1) + 2*img.item(y+1,x,1) + img.item(y+1,x+1,1)
                    gy += -1 * img.item(y-1,x-1,2) - 2*img.item(y-1,x,2) - 1 * img.item(y-1,x+1,2) + img.item(y+1,x-1,2) + 2*img.item(y+1,x,2) + img.item(y+1,x+1,2)
                    gy /= 3

                if(gx**2 + gy**2 > T):
                    ret[y,x] = STRONG_COLOR
                    # edges[y,x] = True
                else:
                    ret[y,x] = [255,255,255]
                # else:
                    # edges[y,x] = False
                # print("{} {} {}, {} {} {}".format(img.item(y,x,0), img.item(y,x,1), img.item(y,x,2), r,g,b))
                # ret[y,x] = [r,g,b]
                # setPixel(ret, (g,g,g), x, y)
                x+=1
            y+=1
        # fse(ret.copy(),edges)
        return ret

    def cannyedge(img):
        ret = img.copy()
        h = img.shape[0]
        w = img.shape[1]
        y = 1

        mT = 2500
        lT = 15000

        if len(sys.argv) > 2:
            mT = int(sys.argv[2])
        if len(sys.argv) > 3:
            lT = int(sys.argv[3])
        garr = {}
        while y < h-1:
            x = 0
            while x < w-1:
                gx = -1 * img.item(y-1,x-1,0) - 2*img.item(y,x-1,0) - 1 * img.item(y+1,x-1,0) + img.item(y-1,x+1,0) + 2*img.item(y,x+1,0) + img.item(y+1,x+1,0)
                gy = -1 * img.item(y-1,x-1,0) - 2*img.item(y-1,x,0) - 1 * img.item(y-1,x+1,0) + img.item(y+1,x-1,0) + 2*img.item(y+1,x,0) + img.item(y+1,x+1,0)
                
                mag = gx**2 + gy**2
                theta = math.atan2(gy,gx)*180 / math.pi
                inten = img.item(y,x,0)
                garr[y,x] = [gx,gy,mag,theta,inten]
                ret[y,x] = [255,255,255]
                x+=1
            y += 1
        strong = {}
        weak = {}
        for coord in list(garr.keys()):
            y = coord[0]
            x = coord[1]
            gx = garr[coord][0]
            gy = garr[coord][1]
            mag = garr[coord][2]
            theta = garr[coord][3]
            # if( (theta > 67.5 and theta < 112.5) or (theta < -112.5 and theta > -67.5) ):
            if(theta**2 < 22.5**2 or theta > 157.5 or theta < -157.5):
                if( (y,x-1) in garr and (y,x+1) in garr ):
                    if(mag > garr[y,x-1][2] and mag > garr[y,x+1][2]):
                        if(mag > lT): strong[y,x] = True
                        elif(mag > mT): weak[y,x] = True
                # W and E
            elif(theta < -22.5 and theta > -67.5 or ( theta > 112.5 and theta < 157.5 )):
            # elif( ( theta > 22.5 and theta < 67.5 ) or ( theta > -157.5 and theta < -112.5) ):
                if( (y-1,x+1) in garr and (y+1,x-1) in garr ):
                    if(mag > garr[y-1,x+1][2] and mag > garr[y+1,x-1][2]):
                        if(mag > lT): strong[y,x] = True
                        elif(mag > mT): weak[y,x] = True
                # NE and SW
            # elif(theta < -22.5 and theta > -67.5 or ( theta > 112.5 and theta < 157.5 )):
            elif( ( theta > 22.5 and theta < 67.5 ) or ( theta > -157.5 and theta < -112.5) ):
                if( (y-1,x-1) in garr and (y+1,x+1) in garr ):
                    if(mag > garr[y-1,x-1][2] and mag > garr[y+1,x+1][2]):
                        if(mag > lT): strong[y,x] = True
                        elif(mag > mT): weak[y,x] = True
                # SE and NW
            elif( (theta > 67.5 and theta < 112.5) or (theta > -112.5 and theta < -67.5) ):
            # elif(theta**2 < 22.5**2 or theta > 157.5 or theta < -157.5):
                if( (y-1,x) in garr and (y+1,x) in garr ):
                    if(mag > garr[y-1,x][2] and mag > garr[y+1,x][2]):
                        if(mag > lT): strong[y,x] = True
                        elif(mag > mT): weak[y,x] = True
                # N and S
        trav = {}
        found = set()
        ret2 = ret.copy()
        # print(strong)
        def use(y,x,oy,ox):
            return (y,x) not in trav and ( (y,x) in weak or (y,x) in strong ) and abs(garr[oy,ox][4] - garr[y,x][4]) < COL_TOL
        def trace(y,x,d=0):
            if(d > DEPTH_LIMIT): return False
            if( (y,x) in strong or (y,x) in found ): return True
            trav[y,x] = True
            e = d+1
            if( use(y-1,x,y,x) ):
                if trace(y-1,x,e): return True
            if( use(y-1,x+1,y,x) ):
                if trace(y-1,x+1,e): return True
            if( use(y-1,x-1,y,x) ):
                if trace(y-1,x-1,e): return True
            if( use(y+1,x,y,x) ):
                if trace(y+1,x,e): return True
            if( use(y+1,x-1,y,x) ):
                if trace(y+1,x-1,e): return True
            if( use(y+1,x+1,y,x) ):
                if trace(y+1,x+1,e): return True
            if( use(y,x-1,y,x) ):
                if trace(y+1,x,e): return True
            if( use(y,x+1,y,x) ):
                if trace(y+1,x,e): return True
            return False
        def traceoa(y,x,ang):
            if (y,x) in strong: return True
            trav[y,x] = True
            if(theta**2 < 22.5**2 or theta > 157.5 or theta < -157.5):
                if(use(y-1,x) and trace(y-1,x,ang)): return True
                if(use(y+1,x) and trace(y+1,x,ang)): return True
            elif(theta < -22.5 and theta > -67.5 or ( theta > 112.5 and theta < 157.5 )):
                if(use(y-1,x-1) and trace(y-1,x-1,ang)): return True
                if(use(y+1,x+1) and trace(y+1,x+1,ang)): return True
            elif( ( theta > 22.5 and theta < 67.5 ) or ( theta > -157.5 and theta < -112.5) ):
                if(use(y-1,x+1) and trace(y-1,x+1,ang)): return True
                if(use(y+1,x-1) and trace(y+1,x-1,ang)): return True
            elif( (theta > 67.5 and theta < 112.5) or (theta > -112.5 and theta < -67.5) ):
                if(use(y,x-1) and trace(y,x-1,ang)): return True
                if(use(y,x+1) and trace(y,x+1,ang)): return True
            return False
        for coord in list(weak.keys()):
            y = coord[0]
            x = coord[1]
            ang = garr[coord][3]
            if( (y,x) in found ): continue
            # ret[coord] = [255,0,0]
            trav = {}
            if(trace(y,x)):
            # if(traceoa(y,x,ang)):
                for c in trav:
                    # ret[c] = [0,255,0]
                    ret[c] = FOUND_COLOR
                found.update(set(trav.keys()))
                # ret[y,x] = WEAK_COLOR
            # else:
                # ret[y,x] = [255,0,0]
                # ret[y,x] = [0,0,0]
        for coord in list(strong.keys()):
            # ret[coord] = [0,0,255]
            # ret[coord] = [0,255,0]
            ret[coord] = STRONG_COLOR
            ret2[coord] = STRONG_COLOR
        retset = set(strong.keys())
        retset.update(found)

        return ret,ret2,garr,retset

    def blur(img):
        ret = img
        loops = 1
        # try:
        #     loops = int(sys.argv[3].lower())
        # except Exception:
        #     print("Using default loops {}".format(loops))
        for i in range(loops):
            img = ret
            ret = img.copy()
            h = img.shape[0]
            w = img.shape[1]
            y = 1
            while y < h-1:
                x = 1
                while x < w-1:
                    r = 1.0/16 * (img.item(y,x,0)*4 + img.item(y-1,x,0)*2 + img.item(y,x-1,0)*2 + img.item(y+1,x,0)*2 + img.item(y,x+1,0)*2 + img.item(y-1,x-1,0) + img.item(y-1,x+1,0) + img.item(y+1,x-1,0) + img.item(y+1,x+1,0))
                    g = 1.0/16 * (img.item(y,x,1)*4 + img.item(y-1,x,1)*2 + img.item(y,x-1,1)*2 + img.item(y+1,x,1)*2 + img.item(y,x+1,1)*2 + img.item(y-1,x-1,1) + img.item(y-1,x+1,1) + img.item(y+1,x-1,1) + img.item(y+1,x+1,1))
                    b = 1.0/16 * (img.item(y,x,2)*4 + img.item(y-1,x,2)*2 + img.item(y,x-1,2)*2 + img.item(y+1,x,2)*2 + img.item(y,x+1,2)*2 + img.item(y-1,x-1,2) + img.item(y-1,x+1,2) + img.item(y+1,x-1,2) + img.item(y+1,x+1,2))
                    # print("{} {} {}, {} {} {}".format(img.item(y,x,0), img.item(y,x,1), img.item(y,x,2), r,g,b))
                    ret[y,x] = [r,g,b]
                    # setPixel(ret, (g,g,g), x, y)
                    x+=1
                y+=1

            # corners
            y = h-1
            x = w-1
            ret[0,0] =[ 1.0/9 * (img.item(0,0,0)*4 + img.item(0,1,0)*2 + img.item(1,0,0)*2 + img.item(1,1,0)), 1/9 * (img.item(0,0,1)*4 + img.item(0,1,1)*2 + img.item(1,0,0)*2 + img.item(1,1,0)), 1/9 * (img.item(0,0,2)*4 + img.item(0,1,2)*2 + img.item(1,0,0)*2 + img.item(1,1,0)) ]
            ret[y,x] =[ 1.0/9 * (img.item(y,x,0)*4 + img.item(y,x-1,0)*2 + img.item(y-1,x,0)*2 + img.item(y-1,x-1,0)), 1/9 * (img.item(y,x,1)*4 + img.item(y-1,x,1)*2 + img.item(y,x-1,1)*2 + img.item(y-1,x-1,1)), 1/9 * (img.item(y,x,2)*4 + img.item(y,x-1,2)*2 + img.item(y-1,x,2)*2 + img.item(y-1,x-1,2)) ]
            ret[0,x] =[ 1.0/9 * (img.item(0,x,0)*4 + img.item(0,x-1,0)*2 + img.item(1,x,0)*2 + img.item(1,x-1,0)), 1/9 * (img.item(0,x,1)*4 + img.item(1,x,1)*2 + img.item(0,x-1,1)*2 + img.item(1,x-1,1)), 1/9 * (img.item(0,x,2)*4 + img.item(0,x-1,2)*2 + img.item(1,x,2)*2 + img.item(1,x-1,2)) ]
            ret[y,0] =[ 1.0/9 * (img.item(y,0,0)*4 + img.item(y,1,0)*2 + img.item(y-1,0,0)*2 + img.item(y-1,1,0)), 1/9 * (img.item(y,0,1)*4 + img.item(y-1,0,1)*2 + img.item(y,1,1)*2 + img.item(y-1,1,1)), 1/9 * (img.item(y,0,2)*4 + img.item(y,1,2)*2 + img.item(y-1,0,2)*2 + img.item(y-1,1,2)) ]

            # edges

            for x in range(1,w-1):
                for i in range(3):
                    ret[h-1,x][i] = 1.0/12 * (img.item(h-1,x,i)*4 + img.item(h-2,x,i)*2 + img.item(h-1,x-1,i)*2 + img.item(h-1,x+1,i)*2 + img.item(h-2,x+1,i) + img.item(h-2,x-1,i))
                for i in range(3):
                    ret[0,x][i] = 1.0/12 * (img.item(0,x,i)*4 + img.item(1,x,i)*2 + img.item(0,x-1,i)*2 + img.item(0,x+1,i)*2 + img.item(1,x+1,i) + img.item(1,x-1,i))
            for y in range(1,h-1):
                for i in range(3):
                    ret[y,0][i] = 1.0/12 * (img.item(y,0,i)*4 + img.item(y-1,0,i)*2 + img.item(y+1,0,i)*2 + img.item(y,1,i)*2 + img.item(y+1,1,i) + img.item(y-1,1,i))
                for i in range(3):
                    ret[y,w-1][i] = 1.0/12 * (img.item(y,w-1,i)*4 + img.item(y-1,w-1,i)*2 + img.item(y+1,w-1,i)*2 + img.item(y,w-2,i)*2 + img.item(y+1,w-2,i) + img.item(y-1,w-2,i))
                
        return ret

    def greyscale(img):
        ret = img.copy()
        # ret = img
        h = img.shape[0]
        w = img.shape[1]
        y = 0
        while y < h:
            x = 0
            while x < w:
                g = img.item(y,x,0)*.3 + img.item(y,x,1)*.59 + img.item(y,x,2)*.11
                ret[y,x] = [g,g,g]
                # setPixel(ret, (g,g,g), x, y)
                x+=1
            y+=1
        return ret

    def circle(img,garr,edges,origimg):
        fimg = img.copy()
        img = fimg.copy()
        origimg = origimg.copy()
        h = img.shape[0]
        w = img.shape[1]
        allowed = range(0,h)
        alledges = {}
        for x in range(w):
            for y in allowed:
                img[y,x] = [255,255,255]
                alledges[y,x] = 0
        EDGE_LIMIT = len(edges)
        ec = 0
        # maxx = 0
        # maxy = 0
        mex = 1 # Prevent divide by 0 error
        for y,x in edges:
            if(ec >= EDGE_LIMIT): continue
            else: ec += 1
            """
            img[y,x] = [255,255,0]
            img[y-1,x] = [255,255,0]
            img[y,x-1] = [255,255,0]
            img[y-1,x-1] = [255,255,0]
            img[y+1,x] = [255,255,0]
            img[y,x+1] = [255,255,0]
            img[y+1,x+1] = [255,255,0]
            """
            sys.stdout.write("{}%                    \r".format(100*(ec)/EDGE_LIMIT))
            sys.stdout.flush()
            ang = garr[y,x][3]
            slope = math.tan((ang)*math.pi/180)
            """
            print(ang)
            print(ang * math.pi / 180)
            print(slope)
            print(y)
            print(x)
            print()
            """
            for px in range(w):
                # pyi = math.floor((px-x)*slope + y)
                # pyf = math.floor((px+1-x)*slope + y)
                pyi = round((px-x)*slope + y)
                pyf = round((px+1-x)*slope + y)
                if(pyi < 0):
                    pyi = 0
                    continue
                if(pyi > h-1):
                    pyi = h-1
                    continue
                if(pyf < 0):
                    pyf = 0
                    continue
                if(pyf > h-1):
                    pyf = h-1
                    continue
                if(pyi == pyf):
                    if pyi in allowed:
                        alledges[pyi,px] += 1
                        if alledges[pyi,px] > mex:
                            mex = alledges[pyi,px]
                            # maxy = pyi
                            # maxx = px
                    continue
                if pyi > pyf:
                    tmp = pyi
                    pyi = pyf
                    pyf = tmp
                for py in range(pyi,pyf):
                    alledges[py,px] += 1
                    if alledges[py,px] > mex:
                        mex = alledges[py,px]
                        # maxy = py
                        # maxx = px
        print()
        print(mex)
        for y,x in alledges:
            intens = int(255 * (1-(alledges[y,x]/mex)))
            if(intens != 255):
                img[y,x] = [intens,intens,intens]
        cv2.imshow("hough",img)
        cimg = img.copy()
        def collect(can,y,x):
            img[y,x] = [0,255,0]
            can.remove( (y,x) )
            ret = {(y,x)}
            if( (y-1,x) in can ):
                # ret.append( (y-1,x) )
                ret.update(collect(can,y-1,x))
                # can.remove( (y-1,x) )
            if( (y+1,x) in can ):
                ret.update(collect(can,y+1,x))
                # ret.append( (y+1,x) )
                # can.remove( (y+1,x) )
            if( (y+1,x+1) in can ):
                ret.update(collect(can,y+1,x+1))
                # ret.append( (y+1,x+1) )
                # can.remove( (y+1,x+1) )
            if( (y+1,x-1) in can ):
                ret.update(collect(can,y+1,x-1))
                # ret.append( (y+1,x-1) )
                # can.remove( (y+1,x-1) )
            if( (y,x+1) in can ):
                ret.update(collect(can,y,x+1))
                # ret.append( (y,x+1) )
                # can.remove( (y,x+1) )
            if( (y-1,x+1) in can ):
                ret.update(collect(can,y-1,x+1))
                # ret.append( (y-1,x+1) )
                # can.remove( (y-1,x+1) )
            if( (y-1,x-1) in can ):
                ret.update(collect(can,y-1,x-1))
                # ret.append( (y-1,x-1) )
                # can.remove( (y-1,x-1) )
            if( (y,x-1) in can ):
                ret.update(collect(can,y,x-1))
                # ret.append( (y,x-1) )
                # can.remove( (y,x-1) )
            return ret
        def gengroup(el,g,cc):
            g.append(el)
            cc.remove(el)
            yrange = range(el[0]-DIST,el[0]+DIST)
            xrange = range(el[1]-DIST,el[1]+DIST)
            for c in cc:
                if(c[0] in yrange and c[1] in xrange):
                    gengroup(c,g,cc)
                    
        def group(cc):
            ret = []
            while cc:
                temp = []
                # print(cc)
                gengroup(cc[0],temp,cc)
                g = [0,0]
                for t in temp:
                    g[0] += t[0]
                    g[1] += t[1]
                g[0] = round(g[0] / len(temp))
                g[1] = round(g[1] / len(temp))
                ret.append(tuple(g))
            return ret
        def centers(i):
            candidates = set([(y,x) for y in range(h) for x in range(w) if cimg.item(y,x,0) < CIRCLE_CANDEDACY_THRESHOLD])
            cc = []
            while candidates:
                y,x = next(iter(candidates))
                temp = list(collect(candidates,y,x))
                if(len(temp) < SET_REQ_LENGTH): continue
                """
                xmax = max(temp, key=lambda g:g[1])[1]
                xmin = min(temp, key=lambda g:g[1])[1]
                ymax = max(temp, key=lambda g:g[0])[0]
                ymin = min(temp, key=lambda g:g[0])[0]
                cc.append((round((ymax+ymin)/2),round((xmax+xmin)/2)))
                """
                xavg = 0
                yavg = 0
                for z in temp:
                    xavg += z[1]
                    yavg += z[0]
                xavg /= len(temp)
                yavg /= len(temp)
                cc.append((round(yavg), round(xavg)))
            # print(cc)
            cc = group(cc)
            for c in cc:
                img[c] = [0,0,255]
            return cc
        centers = centers(cimg)
        def setoncircle(cy,cx,r):
            sqr = r**2
            ret = set()
            for x in range(-r,r):
                y1i = round(cy - (sqr - x**2)**.5)
                y2i = round(cy + (sqr - x**2)**.5)
                y1f = round(cy - (sqr - (x+1)**2)**.5)
                y2f = round(cy + (sqr - (x+1)**2)**.5)
                if(y1i == y1f):
                    ret.add( (y1i,cx+x) )
                else:
                    mx,mn = (y1i,y1f) if y1i > y1f else (y1f,y1i)
                    for i in range(mn,mx):
                        ret.add( (i,cx+x) )
                if(y2i == y2f):
                    ret.add( (y2i,cx+x) )
                else:
                    mx,mn = (y2i,y2f) if y2i > y2f else (y2f,y2i)
                    for i in range(mn,mx):
                        ret.add( (i,cx+x) )
            return ret
        allowed = set([(y,x) for y in range(h) for x in range(w)])
        print(centers)
        for cen in centers:
            cx = cen[1]
            cy = cen[0]
            lim = h if h > w else w # change < to > to expand past the edges of the image; breaks things
            print(cx,cy)
            minr = 0
            maxl = 0
            minset = set()
            sets = [] # list of list of sets
            currset = [] # list of sets
            # for r in range(lim):
            for r in range(3,lim):
                s = setoncircle(cy,cx,r)
                se = s & edges
                # for c in s:
                    # if(c[0] < 0 or c[0] >= h or c[1] < 0 or c[1] >= w): continue
                    # img[c] = [255,0,0]
                # print("\t{} {}".format(s,edges))
                l = len(se) / len(s)
                if(l > CIRCLE_THRESHOLD):
                    # minr = r
                    # maxl = l
                    minset = s & allowed
                    currset.append(minset)
                    # for c in minset:
                    #     img[c] = [0,0,255]
                else:
                    if(currset):
                        sets.append(currset)
                    currset = []
            for cs in sets:
                s = max(cs, key=lambda k: len(k))
                for c in s:
                    img[c] = [0,0,255]
                    fimg[c] = [0,0,255]
                    origimg[c] = [0,0,255]
                    
            # print(minr)
            # print(maxl)
            # for c in minset:
            #     img[c] = [0,0,255]
        return img,fimg,origimg

    def line(img,garr,edges,origimg):
        limg = img.copy()
        oimg = origimg.copy()
        h = img.shape[0]
        w = img.shape[1]
        for x in range(w):
            for y in range(h):
                limg[y,x] = [255,255,255]
        dtheta = math.pi / h # Not going to 2pi because i abs the distance
        etheta = []
        piby2 = math.pi/2
        for i in range(h):
            etheta.append(i*dtheta - piby2)
        hough = {}
        maxd = round((2**.5)/2 * (w + h))
        maxh = 0
        sins = {}
        coss = {}
        print("Stage 1")
        for theta in etheta:
            coss[theta] = math.cos(theta)
            sins[theta] = math.sin(theta)
            for i in range(maxd):
                hough[round(theta/dtheta),i] = 0
        print("Stage 2")
        l = 100/len(edges)/len(etheta)
        iter = 0
        for y,x in edges:
            for theta in etheta:
                d = ((x * coss[theta] + y * sins[theta])**2)**.5 + EPSILON
                t = round(theta/dtheta),round(d)
                addition = 80-math.log(maxd/d)*15
                addition -= ((theta**2)**.5)*10
                # addition = 1
                if(addition > 0):
                    hough[t] += addition
                c = hough[t]
                if(c > maxh): maxh = c
                iter += 1
                if(iter % 1000 == 0): sys.stdout.write("Progress: {}%                      \r".format(iter*l))
        print()
        print("Stage 3")
        lines = set()
        for theta in etheta:
            for i in range(maxd):
                val = hough[round(theta/dtheta),i]
                intens = 255 * val / maxh
                t = (round(theta/dtheta),w*i/maxd)
                # diff = abs(val/maxh - hough[round((theta-dtheta)/dtheta),i])
                # print("Diff: {}".format(diff))
                limg[t] = [intens,intens,intens]
                if(val/maxh > LINE_THRESHOLD):
                    limg[t] = [0,0,255]
                    lines.add((theta,i))
                # print(round(theta/dtheta), i, intens)
                """
                else:
                    lines.add(max(tmplines))
                    m = max(tmplines)
                    limg[round(m[0]/dtheta),round(w*m[1]/maxd)] = [0,0,255]
                    tmplines = set()
                """
        print("Stage 4")
        maxlines = set()
        flines = set()
        seen = {}
        maxdepth = 6
        def collect(line,depth):
            if depth > maxdepth or (line in seen and seen[line] <= depth): return None
            if line not in seen:
                seen[line] = depth
            depth+=1
            if line in lines:
                maxlines.add(line)
                limg[round(line[0]/dtheta),line[1]] = [0,255,255]
            else:
                limg[round(line[0]/dtheta),line[1]] = [255,255,0]
            theta = line[0]
            collect((theta+dtheta,line[1]),depth)
            # collect((theta+dtheta,line[1]-1),depth)
            # collect((theta+dtheta,line[1]+1),depth)
            collect((theta-dtheta,line[1]),depth)
            # collect((theta-dtheta,line[1]-1),depth)
            # collect((theta-dtheta,line[1]+1),depth)
            collect((theta,line[1]+1),depth)
            collect((theta,line[1]-1),depth)
            return maxlines
        iter = 0
        for l in lines:
            maxlines = set()
            tmp = collect(l,0)
            iter+=1 
            print("Done: {}/{}".format(iter,len(lines)))
            if tmp:
                m = max(tmp,key=lambda k: hough[round(k[0]/dtheta), k[1]])
                limg[round(m[0]/dtheta),m[1]] = [0,255,0]
                flines.add(m)
                for s in seen:
                    seen[s] = -1
            
        print("Stage 5")
        for l in flines:
            # print(l)
            theta = l[0]
            ux = coss[theta] # math.cos(theta)
            uy = sins[theta] # math.sin(theta)
            if uy == 0: continue
            m = -1 * ux / uy
            # oimg[50,100] = [255,255,0]
            d = l[1]
            # IMPORTANT DELETION OF BAD VARS
            if(abs(d) < 20): continue
            ix = ux*d
            iy = uy*d
            allfunc = {x:round((x-ix) * m + iy) for x in range(0,w)}
            for x in range(0,w-1):
                fy = allfunc[x]
                ly = allfunc[x+1]
                if(fy >= h or fy < 0 or ly >= h or ly < 0): continue
                if(fy == ly): oimg[fy,x] = [0,0,255]
                else:
                    if(fy > ly):tmp=fy;fy=ly;ly=tmp
                    yr = range(fy,ly+1)
                    for y in yr:
                        oimg[y,x] = [0,0,255]
        return limg,oimg

    if len(sys.argv) < 2:
        print("Specify an image")
        return

    modes = {'g':greyscale,'b':blur,'e':sobeledge,'canny':cannyedge,'circle':circle}
    desc = {'g':'grey','b':'blur','e':'edges','canny':'canny edge detection'}

    # mode = 'g'
    # if len(sys.argv) > 2:
        # mode = sys.argv[2].lower()

    makeFolders(cache_folder,output_folder)

    url = sys.argv[1]

    iext = {".jpg",".png",".jpe",".jp2",".pbm",".tff",".tif",".bmp",".dip",".pgm",".ppm",".sr",".ras",".tif"}
    iurl = url
    title = iurl
    ext = re.search("\.[a-z]+$",url).group(0)
    basename = re.search("(?<=\/)?[^\/]+(?=\.[a-z0-9-_]+$)",url).group(0)
    if isanchor(url):
        ext = re.search("\.[a-z]+$",url).group(0)
        basename = re.search("(?<=\/)[^\/]+(?=\.[a-z0-9-_]+$)",url).group(0)
        iurl = cache_folder + basename + ext
        title = basename + ext
        if ext not in iext:
            print("Warning: {} may not be a valid image".format(iurl))
        if os.path.isfile(iurl):
            print("Reading cache")
        else:
            print("Saving image as {}...".format(iurl))
            urllib.urlretrieve(url, iurl)
            print("Saved")
    print("Reading {}".format(iurl))
    img = cv2.imread(iurl,cv2.IMREAD_COLOR)
    # cv2.namedWindow(title, cv2.WINDOW_NORMAL)

    def writeImage(img, tag):
        fn = output_folder + basename + "_" + tag + ext
        print("Writing image as " + fn)
        return cv2.imwrite(fn,img)

    # mode = input

    print("Greyscaling...")
    gimage = modes['g'](img.copy())
    print("Blurring...")
    bimage = modes['b'](gimage.copy())
    # print("Sobel...")
    # simage = modes['e'](gimage.copy())
    print("Canny...")
    nimage,p1,garr,edges = modes['canny'](bimage.copy())
    # print("Circle...")
    # cimage,cimage2,cimageorig = circle(nimage.copy(),garr,edges,img.copy())
    cv2.imshow("edges",nimage)
    print("Line...")
    limg,loimg = line(nimage.copy(),garr,edges,img.copy())
    """
    bgimage = modes['b'](gimage.copy())
    print("Blurring grey image...")
    ngimage = modes['e'](bgimage.copy())
    print("Detecting edges on blurred grey image...")
    # ngimage = modes['g'](nimage.copy())
    nimage = modes['b'](img.copy())
    writeImage(gimage,'grey')
    cv2.imshow(title,img)
    writeImage(nimage,"blur")
    cv2.imshow(title + " BLURRY", nimage)
    gimage = modes['b'](gimage.copy())
    """
    # writeImage(simage,'final/sobel')
    # writeImage(p1,'final/cannypart1')
    # writeImage(nimage,'final/finalcanny')
    writeImage(limg,"huff")
    writeImage(loimg,"lines")

    cv2.imshow(title,limg)
    cv2.imshow(title + "lines",loimg)

    # cv2.imshow(title + desc['g'], gimage)
    # cv2.imshow(title + desc['g'] + desc['b'], bimage)
    # cv2.imshow(title + 'CANNY', nimage)
    # cv2.imshow(title + 'sobel', simage)

    # cv2.imshow('circlefinal',cimage)
    # cv2.imshow('circlefinaloncanny',cimage2)
    # cv2.imshow('circleoriginal',cimageorig)
    # writeImage(cimage,"circlefinal")

    waitForKeys(27,ord('q'))

main()
