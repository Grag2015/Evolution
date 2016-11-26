# -*- coding: utf-8 -*-
import cPickle

# загружаем словарь планировок квартир
file = open("D:\YandexDisk\EnkiSoft\Evolution\dict_res.txt", 'r')
dict_res = cPickle.load(file)
file.close()

# загружаем словарь планировок секций
file = open("D:\YandexDisk\EnkiSoft\Evolution\dict_res_sect.txt", 'r')
dict_sect_res = cPickle.load(file)
file.close()

def preparedict():
    """
    Функция обрабатывает файлы с различными планировками квартир и для каждого ключа выбирает планировку с наименьшим числом
    нарушенных ограничений
    """
    import numpy as np
    import pandas as pd
    # подготовка данных
    # список файлов для загрузки
    files_list = ["1_0001","1_0010", "1_0011", "1_0100", "1_0101", "1_0110", "1_0111", "2_0001", "2_0010", "2_0011", "2_0100",
                  "2_0101", "2_0110", "2_0111", "3_0001", "3_0010", "3_0011", "3_0100",
                  "wen1_0001", "wen1_0010", "wen1_0011", "wen1_0100", "wen1_0101", "wen1_0110", "wen1_0111"]
    plall_total = []
    for fl in files_list:
        file = open("d:\YandexDisk\EnkiSoft\Evolution\plall" + fl + ".txt", "rb")
        plall_tmp = cPickle.load(file)
        file.close()
        print len(plall_tmp)
        plall_total += plall_tmp
    outwalls = [x[1] for x in plall_total]
    size = [(x[3],x[4]) for x in plall_total]
    funs = [x[6] for x in plall_total]
    pls = [x[5][0] for x in plall_total]
    hall_pos_dict = {(9,9):0, (9,8):1}
    hall_pos = [hall_pos_dict[x[0][0][1][0]] for x in plall_total]


    data = pd.DataFrame(data=zip(outwalls,size,hall_pos, funs,pls),columns=["outwalls","size","hall_pos","funs","pls"])

    grouped = data[["outwalls","size","hall_pos","funs"]].groupby(["outwalls","size","hall_pos"], as_index=False)
    data_agg = grouped.aggregate(np.min)

    dict_res={}
    for i in range(len(data_agg)):
        dict_res[(data_agg.ix[i,1],data_agg.ix[i,0],data_agg.ix[i,2])] = (data[(data["outwalls"] == data_agg.ix[i,0]) &
                                                                              (data["size"] == data_agg.ix[i,1]) &
                                                                              (data["funs"] == data_agg.ix[i,3]) &
                                                                              (data["hall_pos"] == data_agg.ix[i,2])].reset_index().ix[0,5],
                                                                        data[(data["outwalls"] == data_agg.ix[i, 0]) &
                                                                             (data["size"] == data_agg.ix[i, 1]) &
                                                                             (data["funs"] == data_agg.ix[i, 3]) &
                                                                             (data["hall_pos"] == data_agg.ix[i, 2])].reset_index().ix[0, 4])
    file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res.txt", 'wb')
    cPickle.dump(dict_res, file)
    file.close()

# получить оценку планировки квартиры
def getplfun(flatparams):
    #flatparams = ((4.5, 6.0), (0, 0, 0, 1), 0)
    # округляем до 0.5
    flatparams_new = ((flatparams[0][0] - flatparams[0][0] % 0.5, flatparams[0][1] - flatparams[0][1] % 0.5), flatparams[1], flatparams[2])
    try:
        res = dict_res[flatparams_new][1]
    except KeyError:
        res = 50  # заведомо большая ошибка, т.к. такой планировки нет в базе
    return res

def get_dict_res(flatparams):
    try:
        res = dict_res[flatparams][0]
    except KeyError:
        res = 0
        print "Ошибка: в базе планировок квартир нет значения: " , flatparams
    return res

# exploratory analysis

# выделим столбцы с нужными значениями
import pandas as pd
sizes = [x[0] for x in dict_res.keys()]
out_walls = [x[1] for x in dict_res.keys()]
hall_pos = [x[2] for x in dict_res.keys()]
values = [x[1] for x in dict_res.values()]
# добавим все в датафрейм
df = pd.DataFrame({"sizes":sizes, "out_walls":out_walls, "hall_pos":hall_pos, "values":values})

import ggplot
from ggplot import aes
from ggplot import *
from ggplot import diamonds

ggplot(df, aes(x='values', color='out_walls')) + \
    geom_density() + facet_wrap('hall_pos')
# БЛОК для обработки планировок секции
def preparesectdict():
    """
    Считываем файлы со списками [(b, h), flat_out_walls, nflats, bestfun, bestpl]
    объединяем, группируем по уникальной паре ((b, h), flat_out_walls) и берем вариант с минимальным bestfun
    Словарь планировок имеет формат ("size", "outwalls") = "pls"
    """
    import numpy as np
    import pandas as pd

    # подготовка данных
    # список файлов для загрузки
    files_list = ["sections1101.txt", "sections1111.txt"] #["sections0101.txt", "sections1101.txt", "sections0111.txt", "sections1111.txt"]
    plall_total = []
    for fl in files_list:
        file = open("d:\YandexDisk\EnkiSoft\Evolution\plall_" + fl, "rb")
        plall_tmp = cPickle.load(file)
        file.close()
        print len(plall_tmp)
        plall_total += plall_tmp
    outwalls = [x[1] for x in plall_total]
    size = [x[0] for x in plall_total]
    funs = [x[3] for x in plall_total]
    pls = [x[4] for x in plall_total]

    data = pd.DataFrame(data=zip(outwalls, size, funs, pls),
                        columns=["outwalls", "size", "funs", "pls"])

    grouped = data[["outwalls", "size", "funs"]].groupby(["outwalls", "size"], as_index=False)
    data_agg = grouped.aggregate(np.min)

    dict_res = {}
    for i in range(len(data_agg)):
        dict_res[(data_agg.ix[i, 1], data_agg.ix[i, 0])] = data[(data["outwalls"] == data_agg.ix[i, 0]) &
             (data["size"] == data_agg.ix[i, 1]) &
             (data["funs"] == data_agg.ix[i, 2])].reset_index().ix[0, 4]
    file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res_sect.txt", 'wb')
    cPickle.dump(dict_res, file)
    file.close()

# получить оценку планировки секции
def get_dict_sect_res(sectparams):
    """
    :param sectparams: ((b,h), (0,1,0,1))
    :return: pl
    """
    # округляем размеры секции до полуметра
    (newb, newh) = (sectparams[0][0] - sectparams[0][0] % 0.5, sectparams[0][1] - sectparams[0][1] % 0.5)
    try:

        res = dict_sect_res[((newb, newh), sectparams[1])][0]
    except KeyError:
        res = 0
        print "Ошибка: в базе планировок секций нет значения: " , sectparams
    return res

get_dict_sect_res(((30,20), (1,1,1,1)))