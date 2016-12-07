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
    flats, hall_pos, entrwall, flats_out_walls = Section2Flats(B_, H_, out_walls, showgraph = False)
    if len(flats)==0:
        return 0,0
    prepflats = prepareflats(flats)

    res1=[] # тут храним координаты нижн.лев. угол квартир
    res2=[] # тут храним планировки квартир
    col_list =[]
    show_board = []
    line_width = []
    fill_ = []
    for i, fl in enumerate(prepflats):
        tmp = Flat2Rooms(fl[2], fl[3], entrwall[i], hall_pos[i], fl[4], flats_out_walls[i])
        if tmp == 0:
            return (0, 0)
        res1.append((fl[0],fl[1]))
        res2.append(tmp[0])
        col_list += ["#f7f01d"]+tmp[1]
        show_board += tmp[2]
        line_width += [2] + [None] * (len(tmp[2]) - 1)
        fill_ += [False] + [True] * (len(tmp[2]) - 1)
    t2 = time.clock()
    print "РАСЧЕТ СЕКЦИИ ЗАКОНЧЕН! " + "Время выполнения программы sec.- " + str(t2-t1)

    # visualization
    globplac =[[],[]]
    for rs in zip(res1, res2):
        globplac[0] += list(np.array(rs[1][0]) + rs[0][0])
        globplac[1] += list(np.array(rs[1][1]) + rs[0][1])

    visual_sect(globplac, B_, H_, col_list, show_board, line_width, fill_)

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

def calculation(json_string):
    # функция получает JSON с размерами функ.зон, рассчитывает для каждой уникальной пары размеров планировку секции
    # и возвращает обратно JSON с планировками для каждой функциональной зоны
    print "beforerroe"
    data = json.loads(json_string)
    print "aftererroe"

    Sizes, StartPosId, out_walls = json2params(data)

    # ищем различные уникальные значения пар Размеры-Внешние_стены
    Sizes_out_walls = zip(Sizes, out_walls)
    Sizes_out_walls_unique = list(set(Sizes_out_walls))

    # Рассчитываем планировки секции для каждого элемента из списка Sizes_out_walls_unique
    optim_pls = []
    optim_pls_pos = []
    for bh in Sizes_out_walls_unique:
        tmp1, tmp2 = Section2Rooms(bh[0][0], bh[0][1], bh[1])
        if tmp1 == 0:
            return ""
        optim_pls.append(map(lambda x: [x[0][2:],x[1][2:]],tmp2))  # exclude envelop
        optim_pls_pos.append(tmp1)

    # Готовим список с планировками и отправляем его в pl2json вместе с StartPosId
    plac_ls = map(lambda x: optim_pls[Sizes_out_walls_unique.index(x)], Sizes_out_walls)
    plac_pos_ls = map(lambda x: optim_pls_pos[Sizes_out_walls_unique.index(x)], Sizes_out_walls)
    for i in range(len(plac_ls)):
        data[i]["functionalzones"] = pl2json(plac_ls[i], plac_pos_ls[i], (StartPosId[i][0],StartPosId[i][1],StartPosId[i][3],StartPosId[i][2]))
    file_obj = open('json_out.txt', "w")
    file_obj.write(json.dumps(data))
    file_obj.close()
    return json.dumps(data)

# json_string = '''[{"Deep": 20.0, "Height": 3.0, "Width": 30.0, "ParentId": 4, "Position": {"Y": 0.6, "X": 0.0, "Z": 0.0}, "Id": 18, "BimType": "section"},
#  {"Deep": 20.0, "Height": 3.0, "Width": 30.0, "ParentId": 4, "Position": {"Y": 0.6, "X": 80.0, "Z": 0.0}, "Id": 20, "BimType": "section"}]'''
# calculation(json_string)
# json_string = '[{"BimType":"section","Deep":20.0,"Height":3.0,"Id":18,"Position":{"X":0.0,"Y":0.6,"Z":0.0},"Width":30.0, "ParentId":4}]'
# calculation(json_string)