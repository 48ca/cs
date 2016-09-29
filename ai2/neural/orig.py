#!/usr/bin/env python3

import sys
import numpy as np

upper = .8
lower = .2

def dsig(x): # Gradient function
    return sig(x)*(1-sig(x))
def sig(x):
    return 1/(1+np.exp(-x))

def train(mat,out,syn0,valid,bias=0):
    for iter in range(10000):
        # Forward propagation
        l0 = mat
        l1 = sig(np.dot(l0,syn0))
        l1_error = out - l1
        l1_delta = l1_error * dsig(l1) # Continue along the sigmoid
        syn0 += np.dot(l0.T,l1_delta) # Update the weights
    print("Results for training set:")
    print(l1)
    print("Before sigmoid:")
    print(np.dot(l0,syn0))
    print("Weights:")
    print(syn0)
    return l1, syn0

def notf():
    offset = -.1
    mat = np.array([
        [0+offset],
        [1]
    ])
    indmap = {
        0:0,
        1:1
    }
    out = np.array([[1,0]]).T
    np.random.seed(1)
    syn0 = 10*np.random.random((1,1)) - 5 # Synapse 0
    print(syn0)
    valid = [0,1]
    res,syn = train(mat,out,syn0,valid) # -2
    try:
        while True:
            a = input("Enter values to test: ")
            if int(a) not in valid:
                print("Print a valid number ({})".format(valid))
                continue
            a = int(a)+offset
            # ind = indmap[a]
            # r = res[indmap[a]]
            r = sig(syn[0] * a)
            print(r)
            # r = res[0][ind][0]
            # r = sig(res[0][ind])
            # print(r)
            if r < lower:
                print(0)
            elif r > upper:
                print(1)
            else:
                print("???")
    except (KeyboardInterrupt,EOFError):
        print("Done")
    return

def andf():
    o = -.7
    mat = np.array([
        [o,o],
        [1,o],
        [o,1],
        [1,1]
    ])
    out = np.array([[o,o,o,1]]).T
    np.random.seed(1)
    syn0 = 2*np.random.random((2,1)) - 1 # Synapse 0
    valid = [(0,0),(0,1),(1,0),(1,1)]
    res,syn = train(mat,out,syn0,valid,-.5) # 0
    print("0-offset: "+str(o))
    return

def orf():
    o = -.1
    mat = np.array([
        [o,o],
        [1,o],
        [o,1],
        [1,1]
    ])
    out = np.array([[o,1,1,1]]).T
    np.random.seed(1)
    syn0 = 2*np.random.random((2,1)) - 1 # Synapse 0
    valid = [(0,0),(0,1),(1,0),(1,1)]
    res,syn = train(mat,out,syn0,valid) # -1
    # print(dsig(0))
    print("0-offset: "+str(o))
    return

def cusf():
    mat = np.array([
        [0,0,1],
        [0,1,1],
        [1,0,1],
        [1,1,1]
    ])
    out = np.array([[0,0,1,1]]).T
    np.random.seed(1)
    syn0 = 2*np.random.random((3,1)) - 1 # Synapse 0
    valid = [(0,0),(0,1),(1,0),(1,1)]

#     for iter in range(10000):
#         # Forward propagation
#         l0 = mat
#         l1 = sig(np.dot(l0,syn0),0)
#         l1_error = out - l1
#         l1_delta = l1_error * dsig(l1)
#         syn0 += np.dot(l0.T,l1_delta)
#     print("Results for training set:")
#     print(l1)

    res,syn = train(mat,out,syn0,valid)
    return



def main():
    fs = {'not':notf,'and':andf,'or':orf}
    if len(sys.argv) < 2 or sys.argv[1].lower() not in fs:
        print("Enter 'not', 'and', or 'or'.")
        return cusf()
    else:
        return fs[sys.argv[1].lower()]()
main()
