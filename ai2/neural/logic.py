#!/usr/bin/env python3

import sys
import numpy as np

upper = .8 # Not used
lower = .2 # Not used
gamma = .1
learning_rate = .5

def dsig(x): # Gradient function
    return sig(x)*(1-sig(x))
def sig(x):
    return 1/(1+np.exp(-x))

def gdiff(o,z):
    d = o-z
    if(np.linalg.norm(d) == 0): return d
    return d/np.linalg.norm(d)

def error(out,a):
    # print(out-a)
    return np.linalg.norm(np.square(out-a))

def train(mat,out,theta):
    for iter in range(10000):
        flayer = mat
        alayer = sig(np.dot(flayer,theta)) # Forward propogation

        # Back prop
        j = gdiff(out,alayer)
        change = j * dsig(alayer)*learning_rate # Continue along the sigmoid
        theta += np.dot(flayer.T,change) # Update the weights
    print("Training set:")
    print(flayer)
    print("Results for training set:")
    print(alayer)
    # print("Before sigmoid:")
    # print(np.dot(change,theta))
    print("Weights:")
    print(theta)
    print("Error:")
    print(error(out,alayer))
    return alayer, theta

def ghidden(inputs,wi,wh,des,a,b):
    e = (des - b) * a
    return e
def ginput(inputs,wi,wh,des,a,b):
    e = (des - b) * a * (1 - a) * inputs
    return e

def mltrain(mat,out,wi,wh):
    for iter in range(100000):
        flayer = mat
        # print(flayer)
        # print(wi)
        # print(flayer)
        # print(wi)
        # print(wh)
        alayer = sig(np.dot(flayer,wi)) # Forward propogation
        # print(alayer)
        # print(alayer)
        # print(wh)
        blayer = sig(np.dot(alayer,wh))
        # print(blayer)
        # print(blayer)
        # Back prop
        """
        j = gdiff(out,alayer)
        change = j * dsig(alayer)*learning_rate # Continue along the sigmoid
        """
        # print(out)
        # print(alayer)
        # print(blayer)
        # j = cost(out,blayer)
        # changei = np.array(3,3)
        # changeh = np.array(3,1)
        deltah = np.multiply((out-blayer),dsig(blayer))
        changeh = np.dot(sig(alayer.T), deltah) *learning_rate
        deltai = np.dot(deltah,wh.T)*dsig(alayer)
        changei = np.dot(sig(flayer.T), deltai) *learning_rate
        # changei = np.dot(flayer.T, gdiff(out,blayer)*dsig(blayer)*dsig(alayer)*learning_rate)
        # changei = -ginput(flayer,wi,wh,out,alayer,blayer) * learning_rate
        # changeh = -ghidden(flayer,wi,wh,out,alayer,blayer) * learning_rate
        """
        print(deltai)
        print(deltah)
        print(changei)
        print(changeh)
        print(wi)
        print(wh)
        """
        wi += changei # Update the weights
        wh += changeh
    print("Training set:")
    print(flayer)
    print("Correct values:")
    print(out)
    print("Results for training set:")
    print(blayer)
    # print("Before sigmoid:")
    # print(np.dot(change,theta))
    print("Weights:")
    print(wi)
    print(wh)
    print("Error:")
    print(error(out,blayer))
    return blayer, wi, wh

def notf():
    mat = np.array([
        [1,0],
        [1,1]
    ])
    out = np.array([[1,0]]).T
    np.random.seed(1)
    theta = 10*np.random.random((2,1)) - 5
    res,syn = train(mat,out,theta)
    return

def andf():
    mat = np.array([
        [1,0,0],
        [1,1,0],
        [1,0,1],
        [1,1,1]
    ])
    out = np.array([[0,0,0,1]]).T
    np.random.seed(1)
    theta = 10*np.random.random((3,1)) - 5
    res,syn = train(mat,out,theta)
    return

def orf():
    mat = np.array([
        [1,0,0],
        [1,1,0],
        [1,0,1],
        [1,1,1]
    ])
    out = np.array([[0,1,1,1]]).T
    np.random.seed(1)
    theta = 10*np.random.random((3,1)) - 5
    res,syn = train(mat,out,theta)
    return

def xorf():
    mat = np.array([
        [1,0,0],
        [1,1,0],
        [1,0,1],
        [1,1,1]
    ])
    out = np.array([[0,1,1,0]]).T
    np.random.seed(1)
    wi = 2*np.random.random((3,2)) - 1
    wh = 2*np.random.random((2,1)) - 1
    res,syn0,syn1 = mltrain(mat,out,wi,wh)
    return

def main():
    fs = {'not':notf,'and':andf,'or':orf,'xor':xorf}
    if len(sys.argv) < 2 or sys.argv[1].lower() not in fs:
        for m in fs.keys():
            print(m.upper())
            fs[m]()
            print()
    else:
        return fs[sys.argv[1].lower()]()
main()
