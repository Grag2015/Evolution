from Section2Flats import Section2Flats
from Flat2Rooms import Flat2Rooms
from Flat2Rooms import visual_pl
import numpy as np

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def Section2Rooms(B_, H_):
    flats, hall_pos, entrwall = Section2Flats(B_, H_)
    prepflats = prepareflats(flats)

    res=[]
    col_list =[]
    for i, fl in enumerate(prepflats):
        tmp = Flat2Rooms(fl[2], fl[3], entrwall[i], hall_pos[i], fl[4])
        res.append([(fl[0],fl[1]), tmp[0]])
        col_list += tmp[1]

    # visualization
    globplac =[[],[]]
    for rs in res:
        globplac[0] += list(np.array(rs[1][0][2:]) + rs[0][0])
        globplac[1] += list(np.array(rs[1][1][2:]) + rs[0][1])

    visual_sect(globplac, B_, H_, col_list)

def prepareflats(flats):
    # output - x1,y1, H,B, entrwall, hall_pos, count_rooms
    prepflats = []
    for i in range(3, int(len(flats[0])/2)):
        x1 = flats[0][i*2]
        y1 = flats[1][i*2]
        B = flats[0][i*2+1] - flats[0][i*2]
        H = flats[1][i*2+1] - flats[1][i*2]

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
        prepflats.append((x1, y1, B, H, count_rooms))
    return prepflats


def visual_sect(placement_all, B_, H_, col_list):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    fig1 = plt.figure(figsize=(20,20*float(H_)/B_))
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111)#, aspect='equal')
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
    plt.show()

# ToDo надо выделять горизонтальные и вертикальные  планировки
# ToDo в секциирум отправляем флаги 0/1 для каждой стороны (причем пока верх и низ считаем = 1)
# ToDo в секциирум на основании флагов выше рассчитываем и отправляет флаги для каждой комнаты - при этом эти флгаи будут абсолютные, на основании информации
# секция енвелоп-флэт, с помощью позиции входной стены надо переводить эти флаги в относительные и передавать дальше
# ToDo в флэт2рум правим условия енвелоп-рум в зависимости от флагов (относительно 0 - левая стенка) возможны такие такие комбинации
# 1 - внешняя стена (1,0,0), (0,1,0), (0,0,1), (1,0,1), (0,1,1), (1,1,0), (1,1,1) - под каждую комбинацию свои енвелоп-рум
