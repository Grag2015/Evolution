# -*- coding: utf-8 -*-
from Section2Flats import Section2Flats
from Flat2Rooms import Flat2Rooms
from Flat2Rooms import visual_pl
import numpy as np

import time
# import matplotlib
# matplotlib.use('Qt4Agg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
from interface2 import pl2json
from interface2 import json2params
import json


def Section2Rooms(B_, H_, out_walls):
    # out_walls - список флагов внешняя/внутренняя стена отсчет по часовой стрелке от левой стены, прим. (0,1,1,0)
    # выходные данные: list [((x1,y1), pl),...]
    t1 = time.clock()
    flats, hall_pos, entrwall, flats_out_walls = Section2Flats(B_, H_, out_walls, showgraph=False)
    if len(flats) == 0:
        return 0, 0
    prepflats = []
    for flat in flats:
        prepflats.append(prepareflats(flat))

    res1 = []  # тут храним координаты нижн.лев. угол квартир
    res2 = []  # тут храним планировки квартир
    for j, prepflat in enumerate(prepflats):
        res1tmp = []
        res2tmp = []
        col_list = []
        show_board = []
        line_width = []
        fill_ = []
        for i, fl in enumerate(prepflat):
            tmp = Flat2Rooms(fl[2], fl[3], entrwall[j][i], hall_pos[j][i], fl[4], flats_out_walls[j][i])
            if tmp == 0:
                return (0, 0)
            res1tmp.append((fl[0], fl[1]))
            res2tmp.append(tmp[0])
            col_list += ["#f7f01d"] + tmp[1]
            show_board += tmp[2]
            line_width += [2] + [None] * (len(tmp[2]) - 1)
            fill_ += [False] + [True] * (len(tmp[2]) - 1)
        res1.append(res1tmp)
        res2.append(res2tmp)
    return res1, res2

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

def calculation(bh):
    # функция получает JSON с размерами функ.зон, рассчитывает для каждой уникальной пары размеров планировку секции
    # и возвращает обратно JSON с планировками для каждой функциональной зоны
    print "beforerroe"
    print bh
    print "aftererroe"

    out_walls = (1,1,1,1)

    res1, res2 = Section2Rooms(bh[0], bh[1], out_walls)
    sect_pl = []
    for i in range(len(res2)):  # идем по планировкам секций
        for k in range(3):  # идем по номерам планировок квартир
            sect_pl.append({})
            list_pl = map(lambda x: x[k], res2[i])
            list_pos = map(lambda x: x, res1[i])
            sect_pl[-1]["functionalzones"] = pl2json(list_pl, list_pos)
            sect_pl[-1]["BimType"] = "section"
            sect_pl[-1]["Position"] = {"X": 0, "Z": 0, "Y": 0}

    file_obj = open('json_out_pl3.txt', "w")
    file_obj.write(json.dumps(sect_pl))
    file_obj.close()
    return json.dumps(sect_pl)




