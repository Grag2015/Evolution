# -*- coding: utf-8 -*-
from Section2Flats import Section2Flats
from Flat2Rooms import Flat2Rooms
from Flat2Rooms import visual_pl
import numpy as np

import matplotlib
import time
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def Section2Rooms(B_, H_, out_walls):
    # out_walls - список флагов внешняя/внутренняя стена отсчет по часовой стрелке от левой стены, прим. (0,1,1,0)
    t1 = time.clock()
    flats, hall_pos, entrwall, flats_out_walls = Section2Flats(B_, H_, out_walls)
    prepflats = prepareflats(flats)

    res=[]
    col_list =[]
    show_board = []
    line_width = []
    fill_ = []
    for i, fl in enumerate(prepflats):
        tmp = Flat2Rooms(fl[2], fl[3], entrwall[i], hall_pos[i], fl[4], flats_out_walls[i])
        res.append([(fl[0],fl[1]), tmp[0]])
        col_list += ["#f7f01d"]+tmp[1]
        show_board += tmp[2]
        line_width += [2] + [None] * (len(tmp[2]) - 1)
        fill_ += [False] + [True] * (len(tmp[2]) - 1)
    t2 = time.clock()
    print "РАСЧЕТ СЕКЦИИ ЗАКОНЧЕН! " + "Время выполнения программы sec.- " + str(t2-t1)
    # visualization
    globplac =[[],[]]
    for rs in res:
        globplac[0] += list(np.array(rs[1][0]) + rs[0][0])
        globplac[1] += list(np.array(rs[1][1]) + rs[0][1])

    visual_sect(globplac, B_, H_, col_list, show_board, line_width, fill_)

def prepareflats(flats):
    # output - x1,y1, B, H, count_rooms
    prepflats = []
    for i in range(3, int(len(flats[0])/2)):
        x1 = flats[0][i*2]
        y1 = flats[1][i*2]
        B = flats[0][i*2+1] - flats[0][i*2]
        H = flats[1][i*2+1] - flats[1][i*2]

        if B*H<50:
            count_rooms = 1
        else:
            if B*H<80:
                count_rooms = 2
            else:
                if B*H<110:
                    count_rooms = 3
                else:
                    count_rooms = 4
        prepflats.append((x1, y1, B, H, count_rooms))
    return prepflats


def visual_sect(placement_all, B_, H_, col_list, show_board, line_width, fill_):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    fig1 = plt.figure(figsize=(20,20*float(H_)/B_))
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111)#, aspect='equal')
    for i in range(0, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B_), placement_all[1][2*i]/float(H_)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B_),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H_), alpha=0.6, label='test '+str(i),
                                         facecolor=col_list[i], linestyle=show_board[i], linewidth=line_width[i], fill=fill_[i]
            )
        )
        ax1.text(placement_all[0][2 * i] / float(B_) + (abs(placement_all[0][2 * i] - placement_all[0][2 * i + 1]) / float(B_)) / 2.,
                 placement_all[1][2 * i] / float(H_) + (abs(placement_all[1][2 * i] - placement_all[1][2 * i + 1]) / float(H_)) / 2.,
                 str(round(placement_all[0][2 * i + 1] - placement_all[0][2 * i], 1)) + 'x' + str(round(placement_all[1][2 * i + 1] - placement_all[1][2 * i], 1)))
    plt.show()

# ToDo в секциирум отправляем флаги 0/1 для каждой стороны (причем пока верх и низ считаем = 1)
# ToDo в секциирум на основании флагов выше рассчитываем и отправляет флаги для каждой квартиры - при этом эти флгаи будут абсолютные, на основании информации
# секция енвелоп-флэт, с помощью позиции входной стены надо переводить эти флаги в относительные и передавать дальше
# ToDo в флэт2рум правим условия енвелоп-рум в зависимости от флагов (относительно 0 - левая стенка) возможны такие такие комбинации
# 1 - внешняя стена (1,0,0), (0,1,0), (0,0,1), (1,0,1), (0,1,1), (1,1,0), (1,1,1) - под каждую комбинацию свои енвелоп-рум

# фиксация размеров подъезда, ширина, высота и фиксация по центру подъезда


# ToDo надо выделять горизонтальные и вертикальные  планировки
# Todo надо научить по топологии определять горизонтальность планировки и для планировок с угловой прихожей применять
# симметрию относительно диагонали, чтобы поменять ориентацию планировки - тупо меняем местами элементы 0 и 1 в плэйсменте
    # сделать простое правило поворота - евристика для определения горизонтальности  -если есть торцевая комната, то горизонтальная/вертикальная - см. блокнот

# ToDo топологии надо делать одну для каждого количества квартир.

# дополнительно
# для ускорения можно поработать с глобальными переменными - например, передавать Ay, Ax в целевую функцию

Section2Rooms(20, 15, (0,1,0,1))