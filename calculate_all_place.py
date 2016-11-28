# -*- coding: utf-8 -*-
from Section2Flats import *
import cPickle
import time
import numpy as np


# coding: utf-8
# file = open("d:\YandexDisk\EnkiSoft\Evolution\scensall.txt", 'wb')
# cPickle.dump(scensall, file)
# file.close()

blist = np.array([30.5,31,31.5,32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40])
hlist = np.array([12.5,13,13.5,14,14.5,15,15.5,16,16.5,17,17.5,18,18.5,19,19.5,20])
plall=[]
for nflats in [4,5,6,7,8]:
    for flat_out_walls in [(0,1,0,1), (0,1,1,1),(1,1,0,1),(1,1,1,1)]:
        for b in blist:
            for h in hlist:
                bestpl, bestfun = Section2Flats(b, h, flat_out_walls, nflats)
                plall.append([(b, h), flat_out_walls, nflats, bestfun, bestpl])


file = open("plall_sections_30_40.txt", 'wb')
cPickle.dump(plall, file)
file.close()




