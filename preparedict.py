# -*- coding: utf-8 -*-
import cPickle
from settings import *

# загружаем словарь планировок квартир
file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res.txt", 'r')
dict_res = cPickle.load(file)
file.close()

# загружаем словарь планировок секций
file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res_sect.txt", 'r')
dict_sect_res = cPickle.load(file)
file.close()

# ToDo подключить newplall
def preparedict():
    """
    Функция обрабатывает файлы с различными планировками квартир и для каждого ключа выбирает
    3 планировки с наименьшим числом нарушенных ограничений
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
    funs = [float(x[6]/(len(x[5][0][0])/2-2)) for x in plall_total] # усредняем количество нарушенных ограничений на количество помещений
    pls = [x[5][0] for x in plall_total]
    hall_pos_dict = {(9,9):0, (9,8):1}
    hall_pos = [hall_pos_dict[x[0][0][1][0]] for x in plall_total]


    data = pd.DataFrame(data=zip(outwalls,size,hall_pos, funs,pls),columns=["outwalls","size","hall_pos","funs","pls"])

    grouped = data[["outwalls","size","hall_pos","funs","pls"]].groupby(["outwalls","size","hall_pos"], as_index=False)

    # идем по ключам словаря групп grouped и берем в каждой группе 3 наилучшие планировки
    dict_res={}
    for gr in grouped.groups.keys():
        df = grouped.get_group(gr)
        df = df.sort_values("funs")[0:3]
        dict_res[(df.values[0][1], df.values[0][0], df.values[0][2])] = []
        for d in df.values:
            dict_res[(df.values[0][1], df.values[0][0], df.values[0][2])].append((d[4], d[3]))

    file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res.txt", 'wb')
    cPickle.dump(dict_res, file)
    file.close()

# получить оценку планировки квартиры
def getplfun(flatparams, best_flat):
    #flatparams = ((4.5, 6.0), (0, 0, 0, 1), 0)
    # округляем до 0.5
    flatparams_new = ((flatparams[0][0] - flatparams[0][0] % 0.5, flatparams[0][1] - flatparams[0][1] % 0.5), flatparams[1], flatparams[2])
    try:
        res = dict_res[flatparams_new][best_flat][1]
    except KeyError:
        res = sett_penalty_nores
    return res

def get_dict_res(flatparams, best_flat):
    try:
        res = dict_res[flatparams][best_flat][0]
    except KeyError:
        res = 0
        print "Ошибка: в базе планировок квартир нет значения: " , flatparams, "best_flat", best_flat
    return res

# БЛОК для обработки планировок секции
def preparesectdict():
    """
    Считываем файлы со списками [(b, h), flat_out_walls, nflats, bestfun, bestpl]
    объединяем, группируем по уникальной паре ((b, h), flat_out_walls) и берем 3 варианта с минимальным bestfun
    Словарь планировок имеет формат ("size", "outwalls") = [pls1, pls2, pls3]
    """
    import numpy as np
    import pandas as pd

    # подготовка данных
    # список файлов для загрузки
    files_list = ["sections0101.txt", "sections1101.txt", "sections0111.txt", "sections1111.txt", "sections_30_40_0101.txt",
                  "sections_30_40_1101.txt", "sections_30_40_0111.txt"]
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

    grouped = data[["outwalls", "size", "funs", "pls"]].groupby(["outwalls", "size"], as_index=False)

    dict_res = {}
    # идем по ключам словаря групп grouped и берем в каждой группе 3 наилучшие планировки
    for gr in grouped.groups.keys():
        df = grouped.get_group(gr)
        df = df.sort_values("funs")[0:3]
        dict_res[(df.values[0][1], df.values[0][0])] = []
        for d in df.values:
            if len(d[3])!=0:
                dict_res[(df.values[0][1], df.values[0][0])].append(d[3][0])

    file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res_sect_3pl.txt", 'wb')
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

        res = dict_sect_res_3pl[((newb, newh), sectparams[1])]
    except KeyError:
        res = 0
        print "Ошибка: в базе планировок секций нет значения: " , sectparams
    return res