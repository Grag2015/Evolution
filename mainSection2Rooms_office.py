# -*- coding: utf-8 -*-
from Section2Flats_office import Section2Flats
from Flat2Rooms_office import Flat2Rooms
from Flat2Rooms_office import visual_pl
import numpy as np

import time
# import matplotlib
# matplotlib.use('Qt4Agg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
from interface2_office import pl2json
from interface2_office import json2params
import json
import copy

def Section2Rooms(B_, H_):
    # out_walls - список флагов внешняя/внутренняя стена отсчет по часовой стрелке от левой стены, прим. (0,1,1,0)
    # выходные данные: list [((x1,y1), pl),...]
    if (B_< 24) | (H_ < 24):
        print 'Введено значение меньше минимальной ширины/глубины 24: ', (B_, H_)

    dict_office = {}
    pl1 = [[0, 24, 12.5, 18, 6, 11.5, 11.5, 12.5, 12.5, 12.5 + 5.5, 5.7, 9.2, 9.2, 13.2, 13.2, 17.2, 17.2, 24,
            0, 3.96, 24 - 3.92, 24, 0, 3.96, 24 - 3.92, 24, 0, 3.96, 24 - 3.92, 24, 0, 3.96, 24 - 3.92, 24,
            0, 6.55, 6.55, 6.55 + 3.7, 6.55 + 3.7, 6.55 + 3.7 * 2, 6.55 + 3.7 * 2, 6.55 + 3.7 * 3, 24 - 3.92, 24],
           [0, 24, 7.4 + 5.9, 7.4 + 8.8, 7.4, 7.4 + 8.8, 7.4, 7.4 + 8.8, 7.4, 7.4 + 8.8 - 2.9, 24 - 4.9, 24, 24 - 4.9,
            24,
            24 - 4.9, 24, 24 - 4.9, 24, 24 - 4.9, 24, 24 - 4.9 - 3, 24 - 4.9, 24 - 4.9 - 3, 24 - 4.9,
            24 - 4.9 - 3 - 3.12, 24 - 4.9 - 3,
            24 - 4.9 - 3 - 3.12, 24 - 4.9 - 3, 24 - 4.9 - 3 - 3.12 - 2.97, 24 - 4.9 - 3 - 3.12, 5.8,
            24 - 4.9 - 3 - 3.12, 5.8, 24 - 4.9 - 3 - 3.12 - 2.97, 0, 5.8, 0, 5.8, 0, 5.8,
            0, 5.8, 0, 5.8]]
    dict_office[(24,24)] = pl1
    deltaX = B_ - 24
    deltaY = H_ - 24
    pl = copy.deepcopy(dict_office[(24,24)])

    # преобразуем планировку - все стены пропорционально сдвигаем на locB%0.5 и locH%0.5
    xlist = list(set(pl[0]))
    xlist.sort()
    delta = (deltaX) / float(len(xlist)-1) # сдвиг для каждой стены
    for i in range(len(pl[0])):
        pl[0][i] += delta*xlist.index(pl[0][i])

    ylist = list(set(pl[1]))
    ylist.sort()
    delta = (deltaY) / float(len(ylist)-1) # сдвиг для каждой стены
    for i in range(len(pl[1])):
        pl[1][i] += delta*ylist.index(pl[1][i])
    return pl



def calculation(bh):
    # функция получает JSON с размерами функ.зон, рассчитывает для каждой уникальной пары размеров планировку секции
    # и возвращает обратно JSON с планировками для каждой функциональной зоны
    print "beforerroe"
    print bh
    print "aftererroe"

    pl = Section2Rooms(bh[0], bh[1])
    sect_pl = {}
    sect_pl = pl2json(pl)

    file_obj = open('json_out_office.txt', "w")
    file_obj.write(json.dumps(sect_pl))
    file_obj.close()
    return json.dumps(sect_pl)


