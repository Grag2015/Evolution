# -*- coding: utf-8 -*-
from Flat2Rooms import *
import cPickle
import time
import numpy as np

t1 = time.clock()
# т.к.ВЫКЛЮЧИЛ поворот для квартир с торцевой комнатой, то B_, H_ не нужны, просто присвоим по 1
B_, H_ = (1, 1)
hall_pos, entr_wall = (2, (0, 0))
max_results = 100

scensall = []
for flat_out_walls in [(0,1,0,0), (0,0,1,0), (0,0,0,1),(0,1,1,0),(0,1,0,1),(0,0,1,1),(0, 1, 1, 1)]:
    for count_rooms in [1,2,3,4]:
        compartments_list = ["envelope", "hall", "corr", "bath", "kitchen"]
        # ToDo надо добавлять еще 3-х и 4-хкомнатные квартиры
        if count_rooms == 1:
            compartments_list += ["room"]
        else:
            if count_rooms == 2:
                compartments_list += ["room", "room2"]
            else:
                if count_rooms == 3:
                    compartments_list += ["room", "room2", "room3"]
                else:
                    compartments_list += ["room", "room2", "room3", "room4"]

        recur_int = 0
        scens = main_topology(max_results, compartments_list, hall_pos, entr_wall, B_, H_, flat_out_walls)
        scensall.append((scens, flat_out_walls, count_rooms))
# coding: utf-8
# file = open("d:\YandexDisk\EnkiSoft\Evolution\scensall.txt", 'wb')
# cPickle.dump(scensall, file)
# file.close()
file = open("d:\YandexDisk\EnkiSoft\Evolution\scensall.txt", 'rb')
scensall = cPickle.load(file)
file.close()

blist = np.array([4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10])
hlist = np.array([6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,11.5,12,12.5,13,13.5,14,14.5,15])
plall=[]
for scall in scensall:
    if ((scall[1] == (0, 1, 0, 0) )| (scall[1] == (0,0,1,0))):
        continue
    for sc in scall[0]:
        for b in blist:
            for h in hlist[hlist>=b]:
                try:
                    res_tmp, resfun, res_x = main_size(b, h, [sc], entr_wall, hall_pos, scall[2])
                    plall.append((sc, scall[1], scall[2], b, h, res_tmp, resfun, res_x))
                    if b!=h:
                        res_tmp2, resfun2, res_x2 = main_size(h, b, [sc], entr_wall, hall_pos, scall[2])
                        plall.append((sc, scall[1], scall[2], h, b, res_tmp2, resfun2, res_x2))
                    print scall[2],scall[1], b, h

                except IndexError:
                    plall.append((sc, scall[1], scall[2], b, h, "res_tmp", "resfun", "res_x", "res_tmp2", "resfun2", "res_x2"))
    file = open("d:\YandexDisk\EnkiSoft\Evolution\plall"+str(scall[2])+"_"+str(scall[1][0])+str(scall[1][1])+str(scall[1][2])+str(scall[1][3])+".txt", 'wb')
    cPickle.dump(plall, file)
    file.close()
    plall=[]

t2 = time.clock()
print "Расчет закончен! Время выполнения программы sec.- " + str(t2 - t1)

file = open("d:\YandexDisk\EnkiSoft\Evolution\plall1_0100.txt", 'rb')
plall1_0100 = cPickle.load(file)
file.close()

file = open("d:\YandexDisk\EnkiSoft\Evolution\plall2_0100.txt", 'rb')
plall2_0100 = cPickle.load(file)
file.close()

