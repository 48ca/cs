#!/usr/bin/env python2
import cv2
import numpy as np
import sys
import re
import urllib
import os

T = 12000


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

    def edge(img,grey=True):
        ret = img.copy()
        h = img.shape[0]
        w = img.shape[1]
        y = 1

        if len(sys.argv) > 3:
            T = int(sys.argv[3])
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
                    ret[y,x] = [0,255,0]
                    # edges[y,x] = True
                # else:
                    # edges[y,x] = False
                # print("{} {} {}, {} {} {}".format(img.item(y,x,0), img.item(y,x,1), img.item(y,x,2), r,g,b))
                # ret[y,x] = [r,g,b]
                # setPixel(ret, (g,g,g), x, y)
                x+=1
            y+=1
        # fse(ret.copy(),edges)
        return ret

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

    if len(sys.argv) < 2:
        print("Specify an image")
        return

    modes = {'g':greyscale,'b':blur,'e':edge}
    desc = {'g':'grey','b':'blur','e':'edges'}

    mode = 'g'
    if len(sys.argv) > 2:
        mode = sys.argv[2].lower()

    makeFolders(cache_folder,output_folder)

    url = sys.argv[1].lower()

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
    img = cv2.imread(iurl,cv2.IMREAD_COLOR)
    # cv2.namedWindow(title, cv2.WINDOW_NORMAL)

    def writeImage(img, tag):
        fn = output_folder + basename + "_" + tag + ext
        print("Writing image as " + fn)
        return cv2.imwrite(fn,img)

    def oneel(img,el):
        h = img.shape[0]
        w = img.shape[1]
        rem = list({1,2,0} - {el})
        for y in range(h):
            for x in range(w):
                for i in rem:   
                    img.itemset(y,x,i,0)
        return img
                

    # mode = input

    ci = img.copy()
    # last = ci.copy()
    color = True
    while True:
        cv2.imshow(title,ci)
        k = cv2.waitKey(0) & 0xFF
        if(k == ord('c')):
            color = True
            ci = img.copy()
        if(k == ord('b')):
            print("Blurring...")
            ci = modes['b'](ci)
            print("Blurred.")
        if(k == ord('g')):
            color = False
            print("Greyscaling...")
            ci = modes['g'](ci)
            print("Greyscaled.")
        if(k == ord('e')):
            print("Detecting edges...")
            # ci = modes['e'](ci,not color)
            ci = modes['e'](modes['g'](ci))
            print("Done.")
        if(k == ord('r')):
            ci = oneel(ci,2)
        if(k == ord('f')):
            ci = oneel(ci,1)
        if(k == ord('v')):
            ci = oneel(ci,0)
        if(k == 27 or k == ord('q')):
            return
    

    print("Greyscaling...")
    gimage = modes['g'](img.copy())
    print("Blurring...")
    bimage = modes['b'](gimage.copy())
    print("Detecting edges...")
    nimage = modes['e'](bimage.copy(),False)
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
    # writeImage(ngimage,desc[mode] + 'afterblur')
    cv2.imshow(title,img)
    cv2.imshow(title + desc['g'], gimage)
    cv2.imshow(title + desc['g'] + desc['b'], bimage)
    cv2.imshow(title + desc['e'] + desc['b'] + desc['g'], nimage)

    waitForKeys(27,ord('q'))

main()
