from Section2Flats import Section2Flats
from Flat2Rooms import Flat2Rooms
from Flat2Rooms import visual_pl
import numpy as np

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def Section2Rooms(B_, H_):
    scens, flats = Section2Flats(B_, H_)
    prepflats = prepareflats(scens, flats)

    res=[]
    col_list =[]
    for fl in prepflats:
        tmp = Flat2Rooms(fl[2], fl[3], fl[4], fl[5], fl[6])
        res.append([(fl[0],fl[1]), tmp[0]])
        col_list += tmp[1]

    # visualization
    globplac =[[],[]]
    for rs in res:
        globplac[0] += list(np.array(rs[1][0][2:]) + rs[0][0])
        globplac[1] += list(np.array(rs[1][1][2:]) + rs[0][1])

        visual_sect(globplac, B_, H_, col_list)

def prepareflats(scen, flats):
    # output - x1,y1, H,B, entrwall, hall_pos, count_rooms
    prepflats = []
    for i in range(3, len(scen)):
        x1 = flats[0][i*2]
        y1 = flats[1][i*2]
        B = flats[0][i*2+1] - flats[0][i*2]
        H = flats[1][i*2+1] - flats[1][i*2]
        hall_pos, entrwall = entrwall_hall_pos(scen[2][i], scen[1][i])
        if B*H<44:
            count_rooms = 1
        else:
            if B*H<60:
                count_rooms = 2
            else:
                if B*H<90:
                    count_rooms = 3
                else:
                    count_rooms = 4
        prepflats.append((x1, y1, B, H, entrwall, hall_pos, count_rooms))
    return prepflats


def entrwall_hall_pos(corr_flat, podezd_flat):
    # пример входных данных - [(2, 11)], [(0, 3)]
    noCorridEntr={(0, 10), (0, 3), (1, 11), (0, 11), (0, 4), (0, 0), (9, 0), (0, 12), (11, 0), (0, 5), (0, 8), (0, 1), (0, 6),
     (0, 9), (0, 7), (0, 2)}
    if set(corr_flat) in noCorridEntr:
        tmp = podezd_flat
    else:
        tmp = corr_flat

    dct = {(1, 3): (0, (0,0)),
            (1, 2): (0, (0,0)),
            (1, 5): (0, (0,1)),
            (1, 10): (0, (0,1)),
            (3, 11): (0, (1,0)),
            (5, 11): (0, (1,0)),
            (2, 11): (0, (1,0)),
            (10, 11): (0, (1,1)),
            (11, 10): (0, (2,0)),
            (11, 5): (0, (2,0)),
            (11, 2): (0, (2,1)),
            (11, 3): (0, (2,1)),
            (5, 1): (0, (3,0)),
            (10, 1): (0, (3,0)),
            (3, 1): (0, (3,1)),
            (2, 1): (0, (3,1)),
            (1, 6): (2, (0,0)),
            (1, 9): (2, (0,0)),
            (1, 8): (2, (0,0)),
            (1, 7): (2, (0,0)),
            (7, 11): (2, (1,0)),
            (6, 11): (2, (1,0)),
            (8, 11): (2, (1,0)),
            (9, 11): (2, (1,0)),
            (11, 6): (2, (2,0)),
            (11, 9): (2, (2,0)),
            (11, 7): (2, (2,0)),
            (11, 8): (2, (2,0)),
            (8, 1): (2, (3,0)),
            (7, 1): (2, (3,0)),
            (6, 1): (2, (3,0)),
            (9, 1): (2, (3,0)),
            (4, 1): (1, (3,1)),
            (11, 4): (1, (2,1)),
            (1, 4): (1, (0,0)),
            (4, 11): (1, (1,0))}
    return dct[tmp[0]]

def visual_sect(placement_all, B_, H_, col_list):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    fig1 = plt.figure(figsize=(20,20) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(0, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B_), placement_all[1][2*i]/float(H_)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B_),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H_), alpha=0.6, label='test '+str(i),
                                         facecolor=col_list[i]
            )
        )
        ax1.text(placement_all[0][2 * i] / float(B_) + (abs(placement_all[0][2 * i] - placement_all[0][2 * i + 1]) / float(B_)) / 2.,
                 placement_all[1][2 * i] / float(H_) + (abs(placement_all[1][2 * i] - placement_all[1][2 * i + 1]) / float(H_)) / 2.,
                 str(round(placement_all[0][2 * i + 1] - placement_all[0][2 * i], 1)) + 'x' + str(round(placement_all[1][2 * i + 1] - placement_all[1][2 * i], 1)))
    # plt.show()

Section2Rooms(20, 20)