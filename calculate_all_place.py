# -*- coding: utf-8 -*-
from Section2Flats import *
import cPickle
import time
import numpy as np


# coding: utf-8
# file = open("d:\YandexDisk\EnkiSoft\Evolution\scensall.txt", 'wb')
# cPickle.dump(scensall, file)
# file.close()

blist = np.array([15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20,20.5,21,21.5,22,22.5,23,23.5,24,24.5,25,25.5,26,26.5,27,27.5,28,28.5,29,29.5,30])
hlist = np.array([12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20])
plall=[]
for nflats in [4,5,6,7,8]:
    for flat_out_walls in [(0,1,0,0), (0,0,1,0),(0,0,0,1),(0,1,1,0),(0,1,0,1),(0,0,1,1),(0, 1, 1, 1)]:
        if flat_out_walls != (0, 1, 0, 0):
            continue
        for b in blist:
            for h in hlist:
                bestpl, bestfun = Section2Flats(b, h, flat_out_walls, nflats)
                plall.append([(b, h), flat_out_walls, nflats, bestfun, bestpl])


file = open("plall_sections.txt", 'wb')
cPickle.dump(plall, file)
file.close()




