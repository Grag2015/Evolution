
# -*- coding: utf-8 -*-
from Section2Flats import Section2Flats
from Flat2Rooms import Flat2Rooms
from Flat2Rooms import visual_pl
import numpy as np

import time
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from interface2 import pl2json
from interface2 import json2params
from settings import *
import json

def Section2Rooms(B_, H_, out_walls):
    # out_walls - список флагов внешняя/внутренняя стена отсчет по часовой стрелке от левой стены, прим. (0,1,1,0)
    # выходные данные: list [((x1,y1), pl),...]

    # расчет шага сетки колонн - берем шаг, остатки по с которым минимальны
    grid_columns_steps = np.array(sett_grid_columns)
    x_col_step = grid_columns_steps[np.argmin(B_ % grid_columns_steps)]
    y_col_step = grid_columns_steps[np.argmin(H_ % grid_columns_steps)]

    # корректировка размеров под шаг
    B_, H_ = (B_ - B_ % x_col_step, H_ - H_ % y_col_step)

    # сетка колонн
    grid_columns_x = x_col_step * np.array(range(B_/x_col_step + 1))
    grid_columns_x_inner = grid_columns_x[1:-1]
    grid_columns_y = y_col_step * np.array(range(H_/y_col_step + 1))
    grid_columns_y_inner = grid_columns_y[1:-1]
    grid_columns = list(((x, y) for x in grid_columns_x for y in grid_columns_y))
    grid_columns_inner = list(((x, y) for x in grid_columns_x_inner for y in grid_columns_y_inner))

    t1 = time.clock()
    flats, hall_pos, entrwall, flats_out_walls, flat_col_dict = Section2Flats(B_, H_, out_walls, (grid_columns_x_inner, grid_columns_y_inner), showgraph = False, mode=2)
    if len(flats)==0:
        return 0,0

    prepflats = []
    for flat in flats:
        prepflats.append(prepareflats(flat))

    res1=[] # тут храним координаты нижн.лев. угол квартир
    res2=[] # тут храним планировки квартир
    col_list =[]
    show_board = []
    line_width = []
    fill_ = []

    for j, prepflat in enumerate(prepflats):
        res1tmp = []
        res2tmp = []
        col_list_tmp = []
        show_board = []
        line_width = []
        fill_ = []
        for i, fl in enumerate(prepflat):
            # если в квартире есть колонны, передадим их список в ф-ю
            if i + 3 in flat_col_dict:
                flat_col_list = map(lambda x: (x[0] - fl[0], x[1] - fl[1]), flat_col_dict[j][i + 3])
            else:
                flat_col_list = []
        tmp = Flat2Rooms(fl[2], fl[3], entrwall[j][i], hall_pos[j][i], fl[4], flats_out_walls[j][i], flat_col_list)
        if tmp == 0:
            return (0, 0)
        res1tmp.append((fl[0], fl[1]))
        res2tmp.append(tmp[0])
        col_list_tmp += ["#f7f01d"] + tmp[1]
        show_board += tmp[2]
        line_width += [2] + [None] * (len(tmp[2]) - 1)
        fill_ += [False] + [True] * (len(tmp[2]) - 1)
    res1.append(res1tmp)
    res2.append(res2tmp)
    col_list.append(col_list_tmp)


    t2 = time.clock()
    print "РАСЧЕТ СЕКЦИИ ЗАКОНЧЕН! " + "Время выполнения программы sec.- " + str(t2 - t1)

    # visualization
    globplac = [[], []]
    for rs in zip(res1, res2):
        globplac[0] += list(np.array(rs[1][0]) + rs[0][0])
        globplac[1] += list(np.array(rs[1][1]) + rs[0][1])

    visual_sect(globplac, B_, H_, col_list, show_board, line_width, fill_, grid_columns)

    return res1, res2, col_list, flats_out_walls


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


def visual_sect(placement_all, B_, H_, col_list, show_board, line_width, fill_, grid_columns):
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

    # Отрисовка колонн
    for xy in grid_columns:
        ax1.add_patch(
            mpatches.Rectangle(((xy[0]-0.1)/float(B_), (xy[1] - 0.1)/float(H_)),  # (x,y)
                               0.2/float(B_),  # width
                               0.2/float(H_), alpha=0.9, facecolor="Black", linewidth=3, fill=True
                               )
            )

    plt.show()

def calculation(json_string):
    # функция получает JSON с размерами функ.зон, рассчитывает для каждой уникальной пары размеров планировку секции
    # и возвращает обратно JSON с планировками для каждой функциональной зоны
    print "calculation: json_in"
    data = json.loads(json_string)
    print "/calculation: json_in"

    out_walls = (1, 1, 1, 1)

    # НУЖНА ОБРАБОТКА DATA

    res1, res2, col_list, flats_out_walls = Section2Rooms(bh[0], bh[1], out_walls)
    sect_pl = []
    for i in range(len(res2)):  # идем по планировкам секций
        for k in range(3):  # идем по номерам планировок квартир
            sect_pl.append({})
            list_pl = map(lambda x: x[k], res2[i])
            list_pos = map(lambda x: x, res1[i])
            flats_out_walls_tmp = map(lambda x: x, flats_out_walls[i])
            color_list = map(lambda x: x[k], col_list)
            sect_pl[-1]["functionalzones"] = pl2json(list_pl, list_pos, col_list, flats_out_walls_tmp)
            sect_pl[-1]["BimType"] = "section"
            sect_pl[-1]["Position"] = {"X": 0, "Z": 0, "Y": 0}

    file_obj = open('json_out_pl3.txt', "w")
    file_obj.write(json.dumps(sect_pl))
    file_obj.close()
    return json.dumps(sect_pl)
# json_string = '''[{"Deep": 20.0, "Height": 3.0, "Width": 30.0, "ParentId": 4, "Position": {"Y": 0.6, "X": 0.0, "Z": 0.0}, "Id": 18, "BimType": "section"},
#  {"Deep": 20.0, "Height": 3.0, "Width": 30.0, "ParentId": 4, "Position": {"Y": 0.6, "X": 80.0, "Z": 0.0}, "Id": 20, "BimType": "section"}]'''
# calculation(json_string)
# json_string = '[{"BimType":"section","Deep":20.0,"Height":3.0,"Id":18,"Position":{"X":0.0,"Y":0.6,"Z":0.0},"Width":30.0, "ParentId":4}]'
# calculation(json_string)

#Section2Rooms(20, 20, (0,1,1,1))

# ToDo надо убрать возврат по количеству квартир, нужно сразу несколько планировок с разным числом квартир разбирать.
# создание ограничений позволяет отрезать заведомо неисполнимые планировки, остальные будем рассчитывать.