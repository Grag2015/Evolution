# -*- coding: utf-8 -*-
import cPickle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from RoomsPack import *

# load
file = open("d:\YandexDisk\EnkiSoft\Evolution\dump.txt", 'r')
scens = cPickle.load(file)
file.close()

global comp_col
comp_col = {0: '#73DD9B',
            1: '#73DD9B',
            2: '#73DD9B',
            3: '#73DD9B',
            4: '#73DD9B'
           }

# Визуализация
i=0
n=1
for t,pl in enumerate(scens[30:39]):
    if i%(n**2)==0:
        fig1 = plt.figure()
    ax1 = fig1.add_subplot(n,n,i%(n**2)+1, title='scen '+str(i), aspect='equal')
    visual2(quickplacement(pl),ax1)
    i+=1
    if (i>100):
        break

plt.show()