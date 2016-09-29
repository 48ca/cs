#!/usr/bin/env python2

import matplotlib.pyplot as plt

from erdos import main as erdos
from bara import main as bara

fig, (ax1, ax2) = plt.subplots(2)
erdos(ax1,50000,2)
bara(ax2,50000,2)
plt.show()
