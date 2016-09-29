#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt

N = 50000
x = np.random.rand(N)
y = np.random.rand(N)
colors = np.random.rand(N) # np.zeros(N)
area = np.pi * (15 * np.random.rand(N))**2

plt.scatter(x,y,s=area,c=colors,alpha=0.8)
plt.show()
