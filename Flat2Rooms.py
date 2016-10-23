# -*- coding: utf-8 -*-
import itertools
import numpy as np
import time
import copy
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re

import fileinput
import cProfile
import json
from interface2 import pl2json, json2params

# настройки алгоритма
timeout = 15
depth_recurs = 100000
recur_int = 0
B=5
H=6
max_res = 10 #максимальное количество результатов, важно ограничивать для скорости работы
min_margin = 1.2

# комнаты
# TODO удалить лишние элементы в списке (коридор)
compartments = ["envelope",  "hall", "corr", "bath", "kitchen", "room", "room2"]
rooms_weights = [1, 1, 1, 1.5, 2, 2] # веса комнат, используются для придания ограничений по каждому типу комнат
areaconstr = [1,1,3.6,9,14,14] # минимальные без оболочки
areaconstrmax = [4.5,4.5,4.5,16,1000,1000] #[4.5,1000,4.5,16,1000,1000] # максимальные без оболочки
widthconstrmin = [1.4,1.2,1.5,2.3,3,3] # минимальные без оболочки
widthconstrmax = [2, 1.5, 1.5, 1000, 1000, 1000] # максимальные без оболочки
areaconstr_opt = [3,1,4,12,16,16] # оптимальные без оболочки
sides_ratio = [0, 0, 1, 1, 1, 1] # вкл/выкл ограничение на соотношение сторон, без оболочки
#цвета для визуализации, без оболочки
comp_col = {0: '#73DD9B',
            1: '#73DD9B',
            2: '#EAE234',
            3: '#ECA7A7',
            4: '#ACBFEC',
            5: '#ACBFEC'
           }
len_comp=len(compartments)



# часть общей стены + минимум одна смежная стена
partcommon_adjacency = [(1,3),(1,5),(1,6),(1,7),(1,9),(3,1),(5,1),(6,1),(7,1),(9,1)]
# часть общей стены
partcommon = list(set(partcommon_adjacency) | set([(1,2),(1,4),(1,8),(1,10),(2,1),(4,1),(8,1),(10,1), (11,6),(6,11)]))
# А содержит В и есть 1,2 общая часть стены
inclusion_partcommon = [(9,6),(9,7),(9,8),(9,9),(7,6),(7,7),(7,8),(7,9),(8,6),(8,7),(8,9),(6,9),(6,10)]

# смежные
adjacency = [(1, 1), (2, 1),(3, 1), (4, 1),(5, 1),(6, 1),(6, 11),(7, 1),(8, 1),(9, 1),(10, 1),(11,1),
			(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (11, 6),
			(0, 1), (0, 2), (0, 3), (0, 4), (0, 5),(0, 6), (0, 7),(0, 8), (0, 9), (0, 10), (0, 11),
			(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0)]

def inverse(noatomicBArel):
    res=[]
    for elem in noatomicBArel:
        res.append((12-elem[0],12-elem[1]))
    return res

envel_hall = [(9, 9), (9, 8)]#list(set(inclusion_partcommon) - {(6, 9), (9, 6)}) # TODO - убираешь (9, 8) и сразу время работы вырастает в десять раз
envel_room = list(set(inclusion_partcommon) - {(9, 6)}) #(8, 7), (8, 9), (9, 8)}
bath_kitchen = partcommon_adjacency
# hall_other = partcommon #Для случая без коридора
hall_corr = list((set(partcommon))- set([(1,6),(6,1),(10,1),(5,1),(4,1),(11,6),(6,11)])) #Для случая c коридор  - set([(7,1),(10,1),(5,1),(4,1),(11,6)])
envel_corr = list((set(inclusion_partcommon)- {(6, 9), (9, 6)}) | set([(8,8)]))
corr_other = list(((set(partcommon) | set(inverse(partcommon))) - set([(11,2), (11,3), (11,4)])) | {(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),(0,11),(0,12),(11,0),(9,0)} ) # -
hall_other = list(set(partcommon) | {(0,0),(0,1),(0,2),(0,3),(0,5),(0,7),(0,10),(0,11),(0,12),(3,11)}) # используем для случая с коридором
bath_kitch2room = list(set(adjacency) | {(3,12), (4,12), (5,12), (2, 12), (5, 11)})
other_room2 = list(set(adjacency) | {(3,12),(4,12), (3,11), (5,12), (5,11)})


# Если нет коридора, то hall_other:=corr_other - это надо вынести в ф-ю main

# topologic constraints
# TODO эту матрицу тоже надо чистить
tc_src=[[[], envel_hall, envel_corr, envel_room, envel_room, envel_room, envel_room],
    [[],[], hall_corr , hall_other , hall_other, hall_other, other_room2],
    [[],[], [], corr_other, corr_other, corr_other, other_room2],
    [[], [], [], [],  bath_kitchen, bath_kitch2room, other_room2],
    [[], [], [], [], [], bath_kitch2room, other_room2],
    [[], [], [], [], [], [], other_room2],
    [[], [], [], [], [], [], []]]

# envel_hall | envel_corr | envel_room



def prepare_tc(tc_src):
    tc = copy.deepcopy(tc_src)
    # верхний треугольник оставляем без изменений
    # диагональ заполняем значением (6,6)
    for i in range(len_comp):
        tc[i][i].append((6,6))

    # нижний треугольник заполняем симметричными элементами преобразованными ф-ей inverse
    for i in range(0,len_comp): # go along rows
        for j in range(i+1, len_comp): # go along columns
            tc[j][i] = inverse(tc[i][j])
    return tc


# interval algebra composition matrix
# TODO пока оставляем множеством
IAcomp = [[{0}, {0}, {0}, {0}, {0, 1, 2, 3, 4}, {0, 1, 2, 3, 4}, {0}, {0}, {0}, {0}, {0, 1, 2, 3, 4}, {0, 1, 2, 3, 4},
           {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}],
          [{0}, {0}, {0}, {1}, {2, 3, 4}, {2, 3, 4}, {1}, {0}, {0}, {1}, {0, 1, 2, 3, 4}, {5, 6, 7},
           {8, 9, 10, 11, 12}],
          [{0}, {0}, {0, 1, 2}, {0}, {2, 3, 4}, {2, 3, 4}, {2}, {0, 1, 2}, {0, 1, 2, 7, 8}, {2, 7, 8},
           {2, 3, 4, 5, 6, 7, 8, 9, 10}, {8, 9, 10}, {8, 9, 10, 11, 12}],
          [{0}, {0}, {0, 1, 2}, {3}, {4}, {4}, {3}, {0, 1, 2}, {0, 1, 2, 7, 8}, {3, 6, 9}, {4, 5, 10}, {11}, {12}],
          [{0}, {0}, {0, 1, 2, 3, 4}, {4}, {4}, {4}, {4}, {0, 1, 2, 3, 4}, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},
           {4, 5, 10, 11, 12}, {4, 5, 10, 11, 12}, {12}, {12}],
          [{0}, {1}, {2, 3, 4}, {4}, {4}, {5}, {5}, {5, 6, 7}, {8, 9, 10, 11, 12}, {10, 11, 12}, {10, 11, 12}, {12},
           {12}],
          [{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}],
          [{0}, {1}, {2}, {2}, {2, 3, 4}, {5, 6, 7}, {7}, {7}, {8}, {8}, {8, 9, 10}, {8, 9, 10}, {8, 9, 10, 11, 12}],
          [{0, 1, 2, 7, 8}, {2, 7, 8}, {2, 7, 8}, {2, 7, 8}, {2, 3, 4, 5, 6, 7, 8, 9, 10}, {8, 9, 10}, {8}, {8}, {8},
           {8}, {8, 9, 10}, {8, 9, 10}, {8, 9, 10, 11, 12}],
          [{0, 1, 2, 7, 8}, {2, 7, 8}, {2, 7, 8}, {3, 6, 9}, {4, 5, 10}, {10}, {9}, {8}, {8}, {9}, {10}, {11}, {12}],
          [{0, 1, 2, 7, 8}, {2, 7, 8}, {2, 3, 4, 5, 6, 7, 8, 9, 10}, {4, 5, 10}, {4, 5, 10}, {10}, {10}, {8, 9, 10},
           {8, 9, 10, 11, 12}, {10, 11, 12}, {10, 11, 12}, {12}, {12}],
          [{0, 1, 2, 7, 8}, {3, 6, 9}, {4, 5, 10}, {4, 5, 10}, {4, 5, 10}, {11}, {11}, {11}, {12}, {12}, {12}, {12},
           {12}],
          [{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}, {4, 5, 10, 11, 12}, {4, 5, 10, 11, 12}, {4, 5, 10, 11, 12},
           {4, 5, 10, 11, 12}, {12}, {12}, {12}, {12}, {12}, {12}, {12}, {12}]]


def atomicIAcomp(IArel1, IArel2):
    return IAcomp[IArel1][IArel2]

# tt=itertools.product([1,2,3],[4,5,6])

# декартово произведение множеств
def cartesProduct(set1, set2):
    #return list(((x, y) for x in set1 for y in set2))
    return list(itertools.product(set1,set2))

# композиция атомарных элементов блочной алгебры
def atomicBAcomp(atomicBArel1, atomicBArel2):
    """
    >>> atomicBAcomp((1,2),(1,2))
    [(0, 0), (0, 1), (0, 2)]
    >>> atomicBAcomp((6,6),(1,2))
    [(1, 2)]
    >>> atomicBAcomp((1,2),(2,1))
    [(0, 0)]
    >>> atomicBAcomp((1,3),(3,1))
    [(1, 0)]
    """
    return cartesProduct(atomicIAcomp(atomicBArel1[0],atomicBArel2[0]),atomicIAcomp(atomicBArel1[1],atomicBArel2[1]))

# композиция НЕатомарных элементов блочной алгебры
def noatomicBAcomp(noatomicBArel1, noatomicBArel2):
    res=[]
    for i in noatomicBArel1:
        for j in noatomicBArel2:
            res+=atomicBAcomp(i,j)
    return list(set(res))

# ищем пути из i в j xthtp 3-ю точку, но не k
def Paths(i,j,k):
    """
    >>> Paths(0,1,2)
    [(0, 1, 3), (0, 1, 4), (0, 1, 5), (0, 1, 6)]
    >>> Paths(1,1,1)
    Traceback (most recent call last):
      File "D:\Program Files\Anaconda2\lib\site-packages\IPython\core\interactiveshell.py", line 2885, in run_code
        exec(code_obj, self.user_global_ns, self.user_ns)
      File "<ipython-input-105-55c139226b39>", line 1, in <module>
        Paths(1,1,1)
      File "<ipython-input-71-c4c31cde3b6d>", line 131, in Paths
        ls.remove(i)
    ValueError: list.remove(x): x not in list
    >>> Paths(0,2,len(compartments)-1)
    [(0, 2, 1), (0, 2, 3), (0, 2, 4), (0, 2, 5)]
    >>> Paths(2,0,len(compartments)-1)
    [(2, 0, 1), (2, 0, 3), (2, 0, 4), (2, 0, 5)]
    """
    ls = range(len_comp)
    ls.remove(k)
    ls.remove(i)
    ls.remove(j)
    res=[]
    for elem in ls:
        res.append((i,j,elem))
    return res

# Функция поиска допустимых подмножеств
def PathConsistency(C):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> PathConsistency(sc)[0]
    (0, 0, 0)
    >>> PathConsistency(sc)[2]
    210
    >>> PathConsistency(sc)[3]
    0
    >>> PathConsistency(sc)[3]
    0
    """
    # >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    # ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    # ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    # ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    # ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 0)]],
    # ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    # ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    # >>> PathConsistency(sc)[0]
    # (4, 6, 1)
    # >>> PathConsistency(sc)[2]
    # 31
    LPathsToVisit = []
    NPathsChecked = 0
    NChanges = 0

    if not(withoutgapes3(C)):
        return ((1,2,2), C, 0, 0)

    if not(IsEntrCorrHall(C)):
        return ((1,2,2), C, 0, 0)

    # begin first loop
    samples_3 = itertools.permutations(range(len_comp),3)
    for elem in samples_3:
        NPathsChecked+=1
        if (elem in LPathsToVisit):
            LPathsToVisit.remove(elem)
        TmpCij = list(set(C[elem[0]][elem[1]]) & set(noatomicBAcomp(C[elem[0]][elem[2]],C[elem[2]][elem[1]])))
        if (len(TmpCij)==0):
            # print C[elem[0]][elem[1]]
            # print noatomicBAcomp(C[elem[0]][elem[2]],C[elem[2]][elem[1]])
            return (elem, C, NPathsChecked, NChanges)
        if (len(TmpCij) != len(C[elem[0]][elem[1]])):
            NChanges += 1
            # print C[elem[0]][elem[1]]
            # print TmpCij
            C[elem[0]][elem[1]] = TmpCij
            C[elem[1]][elem[0]] = inverse(TmpCij)
            # print 'union',  C[elem[0]][elem[1]]
            LPathsToVisit = list(set(LPathsToVisit) | set(Paths(elem[0],elem[1],elem[2])))
    # end first loop
    # begin second loop
    while len(LPathsToVisit)>0:
        NPathsChecked += 1
        [i, j, k] = LPathsToVisit.pop()
        # TODO тут можно убрать операцию LIST, она лишняя
        TmpCij = list(set(C[elem[0]][elem[1]]) & set(noatomicBAcomp(C[elem[0]][elem[2]], C[elem[2]][elem[1]])))
        if (len(TmpCij)==0):
            return (elem, C, NPathsChecked, NChanges)
        if (len(TmpCij)!= len(C[elem[0]][elem[1]])):
            NChanges += 1
            # print C[elem[0]][elem[1]]
            # print TmpCij
            C[elem[0]][elem[1]] = TmpCij
            C[elem[1]][elem[0]] = inverse(TmpCij)
            # print 'union', C[elem[0]][elem[1]]
            LPathsToVisit = list(set(LPathsToVisit) | set(Paths(elem[0], elem[1], elem[2])))
    # end second loop
    return ((0, 0, 0), C, NPathsChecked, NChanges) #

#
def IsScenario(N):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> IsScenario(sc)
    True
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7),(3, 6)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> IsScenario(sc)
    False
    """
    for i in range(0,len_comp): # go along rows
        for j in range(i+1, len_comp): # go along columns
            if (len(N[i][j])!=1):
                return False
    return True

# ctrl+j - insert template
# ctrl+K - commit


# TODO см. стр. 368 про эвристики, как выбирать next relations
def AssignNextRelFirst(TmpN):
    # """
    # >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    # ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1),(9, 3)], [(9, 0)], [(7, 1)]],
    # ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    # ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    # ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    # ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    # ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    # >>> AssignNextRelFirst(sc)[1][4]
    # [(9, 3)]
    # """
    for i in range(0,len_comp): # go along rows
        for j in range(i+1, len_comp): # go along columns
            if (len(TmpN[i][j])>1):
                # удалить некоторый элемент из множества
                TmpN[i][j] = [TmpN[i][j][0]]
                TmpN[j][i] = [(12-TmpN[i][j][0][0], 12-TmpN[i][j][0][1])]
                return TmpN

def AssignNextRelRest(TmpN):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1),(9, 3)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> AssignNextRelRest(sc)[1][4]
    [(9, 3)]
    """
    for i in range(0,len_comp): # go along rows
        for j in range(i+1, len_comp): # go along columns
            if (len(TmpN[i][j])>1):
                # удалить некоторый элемент из множества
                #tmp = copy.copy(TmpN[i][j])
                #tmp.pop()
                #TmpN[i][j] = tmp
                #TmpN[j][i] = inverse(tmp)
                # TODO 2 строки ниже предполагают, что симметричные элементы имеют одинаковые порядковые номера
                TmpN[i][j] = TmpN[i][j][1:]
                TmpN[j][i] = TmpN[j][i][1:]
                return TmpN

def AssignNextRel(TmpN1,TmpN2):
    for i in range(0,len_comp): # go along rows
        for j in range(i+1, len_comp): # go along columns
            if (len(TmpN1[i][j])>1):
                TmpN1[i][j] = [TmpN1[i][j][0]]
                TmpN1[j][i] = [(12-TmpN1[i][j][0][0], 12-TmpN1[i][j][0][1])]
                TmpN2[i][j] = TmpN2[i][j][1:]
                TmpN2[j][i] = TmpN2[j][i][1:]
                return (TmpN1,TmpN2)

nres = 0
stop = False

def EnumerateScenarios(N):
    global recur_int
    recur_int+=1
    global nres
    global stop

    # input - matrix of constraints
    L = []
    if (stop):
        return L

    (i, j, k) = PathConsistency(N)[0]

    # begin base cases
    if ((i!=0)|(j!=0)):
        #print 1
        return L # if N is inconsistent, return the empty list
    if IsScenario(N):
        # if (N == sc):
        #     print "sc was found"
        # быстрая проверка на наличие пустот
        if(withoutgapes(N)):
            L.append(N)
            nres+=1
            if (nres>=max_res):
                stop = True
        #print 2
        return L # if N is a scenario, return a list only with N
    # end base cases

    #print depth_recurs
    if (recur_int > depth_recurs):
        print "depth_recurs exceeded"
        return L

    # begin recursive case 1
    (TmpN1,TmpN2) = (copy.deepcopy(N),copy.deepcopy(N))
    AssignNextRel(TmpN1,TmpN2) #assign next relation
    TmpL = EnumerateScenarios(TmpN1) # recursive call
    #print TmpL
    if (len(TmpL)!=0):
        L+=TmpL

    # end recursive case 1

    # begin recursive case 1
    TmpL = EnumerateScenarios(TmpN2)  # recursive call
    if (len(TmpL)!=0):
        L+=TmpL
    # end recursive case 2
    #print 3
    return L

# TODO в dmin и dmax надо удалять пару столбцов и пару строк (в новой версии они не должны использоваться)
dminm = [[0, B, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
         [B, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
         [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
         [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
         [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
         [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]
def dmin(i, j, scen, dim):
    global dminm
    tmp = copy.deepcopy(scen)
    IAatom = tmp[i/2][j/2].pop()[dim]
    if ((IAatom==8)|(IAatom==4)): #During, вношу сразу пару симметричных значений.
        dminm = [[1,2],[2,1]]
        return dminm[i%2][j%2]

    if ((IAatom==3)|(IAatom==9)): #During, вношу сразу пару симметричных значений.
        dminm = [[0,0.5],[0.5,0.5]]
        return dminm[i%2][j%2]

    if ((IAatom==2)|(IAatom==10)): #During, вношу сразу пару симметричных значений.
        dminm = [[0.5,0.5],[0.5,0.5]]
        return dminm[i%2][j%2]

    if ((IAatom==0)|(IAatom==12)): #During, вношу сразу пару симметричных значений.
        dminm = [[2,3],[1,2]]
        return dminm[i%2][j%2]

    if ((IAatom==7)|(IAatom==5)): #During, вношу сразу пару симметричных значений.
        dminm = [[1,1],[1,1]]
        return dminm[i%2][j%2]

    return dminm[i][j]


dmax = [[0, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B],
        [B, 0, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1],
        [B-1, B, 0, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B],
        [B, B-1, B, 0, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1],
        [B-1, B, B-1, B, 0, B, B-1, B, B-1, B, B-1, B, B-1, B],
        [B, B-1, B, B-1, B, 0, B, B-1, B, B-1, B, B-1, B, B-1],
        [B-1, B, B-1, B, B-1, B, 0, B, B-1, B, B-1, B, B-1, B],
        [B, B-1, B, B-1, B, B-1, B, 0, B, B-1, B, B-1, B, B-1],
        [B-1, B, B-1, B, B-1, B, B-1, B, 0, B, B-1, B, B-1, B],
        [B, B-1, B, B-1, B, B-1, B, B-1, B, 0, B, B-1, B, B-1],
        [B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, 0, B, B-1, B],
        [B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, 0, B, B-1],
        [B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, 0, B],
        [B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, B-1, B, 0]]

# # проверка симметричности таблица мин и макс.
# for i in range(10):
#     for j in range(10):
#         if dmin[i][j]!=dmin[j][i]:
#             print i,j

matr = [[[0, 0], [0, 0]],
        [[0, 0], [-1, 0]],
        [[0, 0], [1, 0]],
        [[-1, 0], [1, 0]],
        [[1, 0], [1, 0]],
        [[1, 0], [1, -1]],
        [[-1, 0], [1, -1]],
        [[0, 0], [1, -1]],
        [[0, 0], [1, 1]],
        [[-1, 0], [1, 1]],
        [[1, 0], [1, 1]],
        [[1, -1], [1, 1]],
        [[1, 1], [1, 1]]]

def AfterTo(j,k, scen, dim):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> (AfterTo(0,1, sc, 0), AfterTo(7,5, sc, 1), AfterTo(9,8, sc, 1))
    (0, -1, 1)
    """
    # возвращает -1, если стены совпадают, 1 - если j правее k, и 0 - если j левее k
    if ((j/2 == k/2) & (abs(j - k) == 1)):
        return j%2
    IAatom = scen[j/2][k/2][0][dim] #проверить редактируется ли оригинал scen

    return matr[IAatom][j%2][k%2] # остаток от деления на 2 указывает правая ли стена

def IsEntrCorrHall(scen):
    # Есть выход в любую комнату из коридора или прихожей
    isentr = {(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(2,1),(2,11),(3,1),(3,11),(4,1),(4,11),(5,1),(5,11),(6,1),(6,11),(7,1),(7,11),(8,1),(8,11),(9,1),(9,11),(10,1),(10,11),(11,5),(11,6),(11,7),(11,8),(11,9),(11,10)}
    if (len((set(scen[2][3]) | set(scen[1][3])) & isentr)==0):
        return False
    if (len((set(scen[2][4]) | set(scen[1][4])) & isentr)==0):
        return False
    if (len((set(scen[2][5]) | set(scen[1][5])) & isentr)==0):
        return False
    return True

# функция используется для быстрой оценки наличия пустот
def quickplacement(scen):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> quickplacement(sc)[0]
    [0.0, 5.0, 0.0, 5.0, 2.0, 3.5, 0.0, 2.0, 0.0, 2.0, 0.0, 3.5, 3.5, 5.0]
    """
    BH=[B,H]
    def quickplacementdim(dim, dmin, dmax, scen):
        matr=np.zeros(((len_comp) * 2,(len_comp) * 2))
        for i in range(1,len_comp*2):
            for j in range(i+1,len_comp*2):
                tmp = AfterTo(i, j, scen, dim)
                if(tmp==1):
                    matr[i][j] += 1
                else:
                    if (tmp==0):
                        matr[j][i] += 1
        tmp = map(sum, matr)
        return map(lambda x: BH[dim]*float(x)/max(tmp),tmp)
    return [quickplacementdim(0, dmin, dmax, scen),quickplacementdim(1, dmin, dmax, scen)]


# функция запускается для каждой размерности
def placement(dim, dmin, dmax, scen):
    done = False
    # для оболочки сразу задаем координаты стен - 0 и 10
    p = [0,10]+[0]*(len_comp-1)*2 # координаты одной размерности, левая стена i-го помещения, правая стена i-го помещения, i=[0,n]
    # [0,10,0,2,2,10,0,2,2,10]
    # tt=0
    while (not(done)):
        #print p
        done = True
        # tt+=1
        # print tt
        for j in range(2*len_comp):
            for k in range(j+1, 2*len_comp):
                # print 'j, k', j, k
                # print 'AfterTo', AfterTo(j,k, scen, dim), AfterTo(k,j, scen, dim)
                if ((AfterTo(j,k, scen, dim)==-1)): # walls j and k are coincident
                    if (p[j]!=p[k]):
                        done = False
                        #print j, k, 1
                        if (p[j] > p[k]):
                            p[k] = p[j]
                        else:
                            p[j] = p[k]
                else:
                    # walls j and k aren't coincident
                    if (AfterTo(k,j, scen, dim)==1):
                        if (p[k] < p[j] + dmin(j, k, scen, dim)):
                            done = False
                            #print j, k, 2
                            p[k] = p[j] + dmin(j, k, scen, dim)
                        else:
                            if (p[k] > p[j] + dmax[j][k]):
                                done = False
                                #print j, k, 3
                                p[j] = p[k] - dmax[j][k]

                    if (AfterTo(j, k, scen, dim)==1):
                        if (p[k] > p[j] - dmin(j, k, scen, dim)):
                            done = False
                            #print j, k, 4
                            p[j] = p[k] + dmin(j, k, scen, dim)
                        else:
                            #print j, k, 5
                            if (p[k] < p[j] - dmax[j][k]):
                                done = False
                                #print j, k, 5
                                p[k] = p[j] - dmax[j][k]
                # print j, k
                # print p
        #done = True
    return p

# Проверяет содержит ли сценарий (т.е. топология) пустоты
def withoutgapes(N):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> withoutgapes(sc)
    True
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 0)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> withoutgapes(sc)
    False
    """

# Неточная проверка на наличие пустот
    # вначале проверяем эвристикой, и если она не дает результата, то делаем точную проверку.
    dct = [(6, 9), (6, 10), (7, 6), (7, 7), (7, 8), (7, 9), (8, 6), (8, 7), (8, 8), (8, 9), (9, 6), (9, 7), (9, 8), (9, 9)]
    korner =[2, 0, 2, 1, 0, 1, 0, 0, 0, 0, 2, 1, 0, 1]

    s = 0
    st = set()
    for t in range(1, len_comp):
        st = st | set(N[0][t]) # TODO тут возможно ошибка
    for t in range(len(dct)):
        if dct[t] in st:
            s += korner[t]
    if s >= 4:
        return withoutgapes2(quickplacement(N))
    else:
        return False

# проверяет содержит ли планировка пустоты
def withoutgapes2(plac_all): #[[0, 10, 0, 1, 1, 2, 3, 10, 2, 3], [0, 10, 0, 10, 0, 10, 0, 10, 0, 10]]
    """
    >>> pl = [[0.0, 5.0, 0.0, 5.0, 2.0, 3.5, 0.0, 2.0, 0.0, 2.0, 0.0, 3.5, 3.5, 5.0],
    ... [0.0, 6.0, 0.0, 0.6, 0.6, 4.0, 3.0, 4.0, 0.6, 3.0, 4.0, 6.0, 0.6, 6.0]]
    >>> withoutgapes2(pl)
    True
    """
    s=0
    for i in range(1,len_comp):
        s+=(plac_all[0][2*i+1] - plac_all[0][2*i])*(plac_all[1][2*i+1] - plac_all[1][2*i])
    if (abs(s-H*B)<0.001):
        return True
    else:
        return False #

def placement_all(dmin, dmax, scen):
    res=[]
    res.append(placement(0, dmin, dmax, scen))
    res.append(placement(1, dmin, dmax, scen))
    return res

def visual(placement_all, ax1):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    # fig1 = plt.figure(figsize=(10,10) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    # ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(1, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B), placement_all[1][2*i]/float(H)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H), alpha=0.6, label='test '+str(i),
                                         facecolor=comp_col[i-1]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i]+ '\n'+
                 str(round(placement_all[0][2 * i+1]-placement_all[0][2*i],1)) + 'x' + str(round(placement_all[1][2 * i+1]-placement_all[1][2*i],1)))
    # plt.show()

# visual without sizes
def visual2(placement_all, ax1):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    # fig1 = plt.figure(figsize=(10,10) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    # ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(1, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B), placement_all[1][2*i]/float(H)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H), alpha=0.6, label='test '+str(i),
                                         facecolor=comp_col[i-1]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i])
    # plt.show()

# move walls
def movewalls(playsments_a):
    playsments_all=copy.deepcopy(playsments_a)
    dm=[B,H]
    newplas=[]
    for dim in [0,1]:
        ls=[]
        for i in range(len_comp*2):
            if (i%2==1):
                ls.append(playsments_all[dim][i])
                st = set(ls)
        if dm[dim] in st:
            st.remove(dm[dim])
        l = float(dm[dim])/(len(st)+1) #step
        ls2=list(st)
        ls2.sort()
        # print ls2
        newplasit=playsments_all[dim]
        for i in range(len_comp*2):
            if ((playsments_all[dim][i]!=0) & (playsments_all[dim][i]!= dm[dim])):
                newplasit[i]=l*(ls2.index(playsments_all[dim][i])+1)
        newplas.append(newplasit)
    return newplas

# sc=[[{(6, 6)}, {(9, 9)}, {(8, 9)}, {(7, 9)}, {(7, 7)}, {(9, 7)}],
#  [{(3, 4)}, {(6, 6)}, {(1, 3)}, {(0,3)}, {(1, 0)}, {(6, 1)}],
#  [{(4, 3)}, {(11, 7)}, {(6, 6)}, {(1, 6)}, {(3, 1)}, {(11, 2)}],
#  [{(3, 3)}, {(6, 1)}, {(1, 3)}, {(6, 6)}, {(5, 1)}, {(12, 2)}],
#  [{(3, 5)}, {(9, 11)}, {(7, 11)}, {(9, 12)}, {(6, 6)}, {(11, 5)}],
#  [{(5, 5)}, {(12, 9)}, {(11, 10)}, {(12, 11)}, {(11, 7)}, {(6, 6)}]]
#
# sc2 = prepare_tc(sc)
# PathConsistency(sc2)

def visual_pl(placement_all):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    fig1 = plt.figure(figsize=(10,10) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(1, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B), placement_all[1][2*i]/float(H)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H), alpha=0.6, label='test '+str(i),
                                         facecolor=comp_col[i-1]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i])
    # plt.show()


# Решение уравнение

import scipy.optimize as opt

# placement example
# placemnt = [[0, 10, 0, 10, 1, 2, 0, 1, 0, 2, 2, 10], [0, 10, 0, 1, 1, 4, 2, 3, 4, 10, 3, 10]]
# функция формирует матрицы для целевой функции

def makeconst(placemnt, discret=True):
    global Ax, Ay, Bx, By, bx, by, bounds
    # создаем матрицу для целевой функции
    def makematr(placemnt):

        global Ax, Ay, Bx, By
        # удаляем из планировки стены контура
        placemnt[0] = placemnt[0][2:]
        placemnt[1] = placemnt[1][2:]

        xlist = list(set(placemnt[0]))
        xlist.sort()
        xlist.remove(0)
        #xlist.remove(B)

        ylist = list(set(placemnt[1]))
        ylist.sort()
        ylist.remove(0)
        #ylist.remove(H)

        # ограничение по площади
        Ax = np.zeros((len_comp - 1, len(xlist)))
        Ay = np.zeros((len_comp - 1, len(ylist)))

        # ограничение по взаимному расположению
        Bx = np.zeros((len(xlist) - 2, len(xlist)-1))
        By = np.zeros((len(ylist) - 2, len(ylist)-1))

        for i in range(len(Bx)):
            Bx[i,i] = -1
            Bx[i,i+1] = 1

        for i in range(len(By)):
            By[i,i] = -1
            By[i,i+1] = 1

        for i in range(len_comp-1):
            for xl in range(len(xlist)):
                # если стенка левая
                if (placemnt[0][2*i]==xlist[xl]):
                    Ax[i,xl] = -1
                    Ax[i, xlist.index(placemnt[0][2*i+1])] = 1
                # если стенка правая
                if (placemnt[0][2*i+1]==xlist[xl]):
                    Ax[i, xl] = 1
                    if (placemnt[0][2 * i]!=0):
                        Ax[i, xlist.index(placemnt[0][2 * i])] = -1
            for yl in range(len(ylist)):
                # если стенка левая
                if (placemnt[1][2*i]==ylist[yl]):
                    Ay[i,yl] = -1
                    Ay[i,ylist.index(placemnt[1][2*i+1])] = 1
                # если стенка правая
                if (placemnt[1][2*i+1]==ylist[yl]):
                    Ay[i, yl] = 1
                    if (placemnt[1][2 * i] != 0):
                        Ay[i, ylist.index(placemnt[1][2 * i])] = -1
    makematr(placemnt)
    bounds = []
    if (discret):
        matrlist =  [len(Ax[0])-1, len(Ay[0])-1]
        boundslist = [(min_margin, B-min_margin), (min_margin, H-min_margin)]
    else:
        matrlist =  [len(Ax[0])-1, len(Ay[0])-1, len(Ax), len(Bx), len(By)]
        boundslist = [(0, B), (0, H), (0,B*H), (min_margin,B), (min_margin,H)]
    for matr in range(len(matrlist)):
        for i in range(matrlist[matr]):
            bounds.append(boundslist[matr])
    return True

# непрерывная функция с фиктивными переменными для описания ограничений-неравенств
def func2_contin(xys):
    # добавить В и Х в конце векторов у и х
    global Ax
    global Ay
    global Bx
    global By
    global areaconstr

    #print xys

    x = xys[0:len(Ax[0]) - 1]
    x = np.append(x, B)
    y = xys[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2]
    y = np.append(y, H)
    s = xys[len(Ax[0]) + len(Ay[0]) - 2:len(Ax[0]) + len(Ay[0]) - 2 + len(Ax)]
    sx = xys[len(Ax[0]) + len(Ay[0]) - 2 + len(Ax):len(Ax[0]) + len(Ay[0]) - 2 + len(Ax) + len(Bx)]
    sy = xys[len(Ax[0]) + len(Ay[0]) - 2 + len(Ax) + len(Bx):]

    res1 = Ax.dot(x) * Ay.dot(y) - s - areaconstr
    res2 = Bx.dot(xys[0:len(Ax[0])]) - sx
    res3 = By.dot(xys[len(Ax[0]):len(Ax[0]) + len(Ay[0])]) - sy # тут видимо ошибка см. дискретную версию ф-и

    return np.absolute(res1).dot(rooms_weights)+sum(np.absolute(res2))*5+sum(np.absolute(res3))*5+sum(np.absolute(s))

# дискретная ф-я, в т.ч. для ген.алгоритма
# TODO нарушается топология при оптимизации, т.к. не учитывается взаимное расположение стен разных комнат
def func2_discret(xy):
    # добавить В и Х в конце векторов у и х
    global Ax
    global Ay
    global Bx
    global By
    global areaconstr
    global areaconstrmax

    #print xys

    x = xy[0:len(Ax[0]) - 1]
    x = np.append(x, B)
    y = xy[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2]
    y = np.append(y, H)

    # Ограничение по площади снизу
    res1 = Ax.dot(x) * Ay.dot(y) - areaconstr
    # Ограничение по площади сверху
    res1max = areaconstrmax - Ax.dot(x) * Ay.dot(y)

    # Ограничение на расположение соседних стен
    res2 = Bx.dot(xy[0:len(Ax[0])-1]) - [min_margin]*len(Bx)#np.sign(Bx.dot(xy[0:len(Ax[0])-1]))*min_margin
    res3 = By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]) - [min_margin]*len(By) #- np.sign(By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]))*min_margin
    # ограничение на соотношение сторон
    res4 = map(lambda d: int((d>=1./3)&(d<=3))-1, Ay.dot(y)/Ax.dot(x))*np.array(sides_ratio)
    # ограничение на минимальную ширину
    res5 = Ax.dot(x) - widthconstrmin
    res6 = Ay.dot(y) - widthconstrmin

    # ограничение на максимальную ширину
    res7 = np.array(widthconstrmax) - np.array(map(min, zip(Ax.dot(x),Ay.dot(y))))
    # отрицательные элементы переводим в 1, 0 и положительные - в 0
    res1sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res1))
    res1maxsign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res1max))
    res2sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res2))
    res3sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res3))
    res4sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res4))
    res5sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res5))
    res6sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res6))
    res7sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res7))

    return res1sign.dot(rooms_weights) + sum(res2sign)*10 + sum(res3sign)*10 + sum(res4sign) + sum(res5sign) + sum(res6sign)+ sum(res7sign) + sum(res1maxsign)

def func2_discret_results(xy):
    # добавить В и Х в конце векторов у и х
    global Ax
    global Ay
    global Bx
    global By
    global areaconstr
    global areaconstrmax

    # print xys

    x = xy[0:len(Ax[0]) - 1]
    x = np.append(x, B)
    y = xy[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2]
    y = np.append(y, H)

    # Ограничение по площади снизу
    res1 = Ax.dot(x) * Ay.dot(y) - areaconstr
    # Ограничение по площади сверху
    res1max = areaconstrmax - Ax.dot(x) * Ay.dot(y)

    # Ограничение на расположение соседних стен
    res2 = Bx.dot(xy[0:len(Ax[0]) - 1]) - [min_margin] * len(Bx)  # np.sign(Bx.dot(xy[0:len(Ax[0])-1]))*min_margin
    res3 = By.dot(xy[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2]) - [min_margin] * len(
        By)  # - np.sign(By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]))*min_margin
    # ограничение на соотношение сторон
    res4 = map(lambda d: int((d >= 1. / 3) & (d <= 3)) - 1, Ay.dot(y) / Ax.dot(x)) * np.array(sides_ratio)
    # ограничение на минимальную ширину
    res5 = Ax.dot(x) - widthconstrmin
    res6 = Ay.dot(y) - widthconstrmin

    # ограничение на максимальную ширину
    res7 = np.array(widthconstrmax) - np.array(map(min, zip(Ax.dot(x), Ay.dot(y))))

    res1sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res1))
    res1maxsign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res1max))
    res2sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res2))
    res3sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res3))
    res4sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res4))
    res5sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res5))
    res6sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res6))
    res7sign = np.array(map(lambda x: np.sign(x) * (np.sign(x) - 1) / 2, res7))

    listres = ["areasmin", "areasmax", "dist_neib_x", "dist_neib_y", "ratio", "widthX", "widthY", "widthMax"]
    res_vec = [sum(res1sign), sum(res1maxsign), sum(res2sign), sum(res3sign), sum(res4sign), sum(res5sign), sum(res6sign), sum(res7sign)]
    res = ''
    for i in range(len(listres)):
        if res_vec[i] > 0:
            res+=listres[i]+" "

    return res

# декодирование размещения из результатов решения уравнения func2==0
# xlistnew, ylistnew - списки
def optim_placement(placemnt, xlistnew, ylistnew):

    xlist = list(set(placemnt[0]))
    xlist.sort()
    xlistnew = [0]+xlistnew + [B]
    # xlist.remove(0)
    # xlist.remove(B)
    plac_new = copy.copy(placemnt)
    for i in range(len(placemnt[0])):
        plac_new[0][i]=xlistnew[xlist.index(placemnt[0][i])]

    ylist = list(set(placemnt[1]))
    ylist.sort()
    ylistnew = [0] + ylistnew + [H]
    # ylist.remove(0)
    for i in range(len(placemnt[1])):
        plac_new[1][i] = ylistnew[ylist.index(placemnt[1][i])]

    return plac_new

def withoutgapes3(N):
    """
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 3)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> withoutgapes(sc)
    True
    >>> sc = [[[(6, 6)], [(6, 9)], [(8, 8)], [(9, 8)], [(9, 8)], [(9, 7)], [(7, 7)]],
    ... [[(6, 3)], [(6, 6)], [(8, 1)], [(9, 0)], [(9, 1)], [(9, 0)], [(7, 1)]],
    ... [[(4, 4)], [(4, 11)], [(6, 6)], [(11, 7)], [(11, 9)], [(5, 1)], [(1, 3)]],
    ... [[(3, 4)], [(3, 12)], [(1, 5)], [(6, 6)], [(6, 11)], [(3, 1)], [(0, 4)]],
    ... [[(3, 4)], [(3, 11)], [(1, 3)], [(6, 1)], [(6, 6)], [(3, 0)], [(0, 0)]],
    ... [[(3, 5)], [(3, 12)], [(7, 11)], [(9, 11)], [(9, 12)], [(6, 6)], [(1, 5)]],
    ... [[(5, 5)], [(5, 11)], [(11, 9)], [(12, 8)], [(12, 9)], [(11, 7)], [(6, 6)]]]
    >>> withoutgapes(sc)
    False
    """

# Неточная проверка на наличие пустот
    # вначале проверяем эвристикой, и если она не дает результата, то делаем точную проверку.
    dct = [(6, 9), (6, 10), (7, 6), (7, 7), (7, 8), (7, 9), (8, 6), (8, 7), (8, 8), (8, 9), (9, 6), (9, 7), (9, 8), (9, 9)]
    korner =[2, 0, 2, 1, 0, 1, 0, 0, 0, 0, 2, 1, 0, 1]

    s = 0
    st = []
    for t in range(1, len_comp):
        st = st + N[0][t]
    st = set(st)
    for t in range(len(dct)):
        if dct[t] in st:
            s += korner[t]
    if s >= 4:
        return True
    else:
        return False

# Поиск различных вариантов компоновки (топологий)
# ЗАГЛУШКА
def main_topology(max_results, compartments_list, hall_pos, printres = True):
    """
    >>> main_topology(10, ["envelope",  "hall", "corr", "room", "room2", "bath", "kitchen"], False)[0][1]
    [[(3, 6)], [(6, 6)], [(1, 7)], [(0, 9)], [(1, 9)], [(0, 9)], [(0, 9)]]
    """
    global max_res, compartments, envel_hall, recur_int, nres, stop, rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col, len_comp, areaconstrmax
    max_res = max_results

    # правим envel_hall в зависимости от hall_pos
    if hall_pos==0:
        envel_hall = [(9,9)]
    else:
        if hall_pos == 1:
            envel_hall = [(9, 8)]
        else:
            if hall_pos != 2:
                print "envel_hall incorrect"
                return False
    # sc = [[[[(6, 6)], [(9, 9)], [(8, 8)], [(7, 9)], [(7, 8)], [(9, 7)], [(7, 7)]],
    #  [[(3, 3)], [(6, 6)], [(1, 7)], [(1, 9)], [(0, 7)], [(3, 1)], [(0, 1)]],
    #  [[(4, 4)], [(11, 5)], [(6, 6)], [(3, 11)], [(1, 6)], [(5, 1)], [(1, 1)]],
    #  [[(5, 3)], [(11, 3)], [(9, 1)], [(6, 6)], [(7, 1)], [(10, 0)], [(7, 0)]],
    #  [[(5, 4)], [(12, 5)], [(11, 6)], [(5, 11)], [(6, 6)], [(11, 1)], [(6, 1)]],
    #  [[(3, 5)], [(9, 11)], [(7, 11)], [(2, 12)], [(1, 11)], [(6, 6)], [(1, 6)]],
    #  [[(5, 5)], [(12, 11)], [(11, 11)], [(5, 12)], [(6, 11)], [(11, 6)], [(6, 6)]]]]
    # return sc

    # подготовка списков и таблиц с ограничениями TODO добавить здесь новые ограничения
    changing_lists = [rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col, areaconstrmax]
    new_lists=[]
    for i in range(len(changing_lists)): new_lists.append([])
    for i in range(len(compartments[1:])):
        if (compartments[1:][i] in set(compartments_list)):
            for j in range(len(changing_lists)):
                new_lists[j].append(changing_lists[j][i])

    rooms_weights = new_lists[0]
    areaconstr = new_lists[1]
    areaconstr_opt = new_lists[2]
    sides_ratio = new_lists[3]
    comp_col = new_lists[4]

    # есть есть коридор, то с прихожей снимается требование "смежность со всеми комнатами"
    if ("corr" in compartments_list):
        tc_src[1][3] = adjacency
        tc_src[1][4] = adjacency
        tc_src[1][5] = adjacency + [(3,11)]

    k = 0
    for i in range(len(compartments)):
        if (not (compartments[i] in set(compartments_list))):
            # удаляем строку i
            # print k
            tc_src.pop(k)
            # удаляем столбец i
            for j in range(len(tc_src)):
                tc_src[j].pop(k)
            k -= 1
        k += 1

    compartments = compartments_list
    len_comp = len(compartments)
    tc = prepare_tc(tc_src)

    # topology
    t1 = time.clock()
    N = copy.deepcopy(tc)
    recur_int = 0
    nres = 0
    stop = False

    # #check
    # for i in range(7):
    #     for j in range(7):
    #         if not(sc3[i][j][0] in tc[i][j]):
    #             print str(i) +":" + str(j) + "Test wasn't passed"
    # print "Test was passed!"
    # return 1

    scens = EnumerateScenarios(N)
    t2 = time.clock()
    if printres:
        print "Найдено " + str(len(scens)) + " вариантов размещения комнат" + '\n' + "Время выполнения программы sec.- " + str(t2-t1)

    return scens

def rotate90(pl, n): # n time по часовой стрелке
    """
    >>> pl = [[0.0, 5.0, 0.0, 1.3636363636363635, 0.0, 3.1818181818181817, 1.3636363636363635, 2.2727272727272729,
    ... 2.2727272727272729, 3.1818181818181817, 0.0, 3.1818181818181817, 3.1818181818181817, 5.0],
    ... [0.0, 6.0, 0.0, 2.3999999999999999, 2.3999999999999999, 4.7999999999999998, 0.0, 2.3999999999999999, 0.0,
    ... 2.3999999999999999, 4.7999999999999998, 6.0, 0.0, 6.0]]
    >>> (rotate90(pl)[0][0],rotate90(pl)[0][5],rotate90(pl)[1][4],rotate90(pl)[1][6])
    (0.0, 3.0, 0.0, 1.6363636363636362)
    """
    if n==0:
        return pl
    if n==1:
        pln=[[],[]]
        pln[0] = map(lambda x: (x/float(H))*B, pl[1])
        pln[1] = map(lambda y: (H-(y/float(B))*H), pl[0])
        for i in range(len(pl[0])/2):
            b1=min(pln[1][2*i],pln[1][2 * i+1])
            b2=max(pln[1][2*i],pln[1][2 * i+1])
            pln[1][2*i]=b1
            pln[1][2*i+1]=b2
        return pln
    else:
        return rotate90(rotate90(pl, n-1), 1)

# Учет ограничений по площади/длине
def main_size(B_, H_, scens, entr_wall, hall_pos):
    global B, H, res_x
    B = B_
    H = H_
    t1 = time.clock()
    optim_scens=[]
    res_x=[]
    bestmin = 1000
    bestmini = -1
    for i in range(len(scens)):
        try:
            makeconst(quickplacement(scens[i])) # подготовка ограничения для целевой функции
            res = opt.differential_evolution(func2_discret, bounds) # оптимизация целевой ф-и с указанными ограничениями
            if res.fun < bestmin:
                bestmin = res.fun
                bestmini = i
            xlistnew = list(res.x[0:len(Ax[0]) - 1])
            ylistnew = list(res.x[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2])
            #print i
            res_tmp = optim_placement(quickplacement(scens[i]), xlistnew, ylistnew) # преобразование результатов оптимизации во внутренний формат
            # вращение планировки в зависимости от позиции входной стены entr_wall in {(0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,0),(3,1)}
            # если прихожая может быть в центре, то просто поворачиваем по часовой стрелке entr_wall[0] раз
            if hall_pos>=1:
                res_tmp = rotate90(res_tmp, entr_wall[0])
            # если прихожая только угловая
            else:
                res_tmp = rotate90(res_tmp, entr_wall[0]+entr_wall[1])

            optim_scens.append(res_tmp)
            res_x.append(func2_discret_results(res.x))
        except ValueError:
            print('Планировка '+str(i)+' не была рассчитана!')
    t2 = time.clock()
    print "Расчет размеров комнат закончен! Время выполнения программы sec.- " + str(t2 - t1)

    return optim_scens[bestmini]


def calculation(json_string):
    # функция получает JSON с размерами функ.зон, рассчитывает для каждой уникальной пары размеров планировку
    # и возвращает обратно JSON с планировками для каждой функциональной зоны
    print "beforerroe"
    data = json.loads(json_string)
    print "aftererroe"
    Sizes, StartPosId = json2params(data)
    # Расчет топологий
    scens = main_topology(1, ["envelope", "hall", "corr", "bath", "kitchen", "room", "room2"])

    # Расчитываем планировки для каждого элемента из списка (Для каждой топологии)
    SizesUnique = list(set(Sizes))
    optim_scens = []
    for bh in SizesUnique:
        # Беру первую рассчитанную планировку (в дальнейшем их сортируем в порядке возр. кол-ва нарушенных ограничений)
        tmp = main_size(bh[0], bh[1], scens)[0]
        optim_scens.append([tmp[0][2:], tmp[1][2:]])  # exclude envelop

    # Готовим список с планировками и отправляем его в pl2json вместе с StartPosId
    plac_ls = map(lambda x: optim_scens[SizesUnique.index(x)], Sizes)
    newres = pl2json(plac_ls, compartments, StartPosId)
    return newres


# hall_pos - позиция коридора 0 -левый нижн, 1 - центр левый, 2- обе позиции возможны,
# entr_wall - стена входа 2-tuple (стена,угол), стена: 0-лево, 1-верх, 2-право, 3-низ; угол: 0 - первый угол при обходе контура по час.стрелке, 1 - 2-й угол
# Todo внимание! нужно возвращать 1 наилучшую планировку!
def Flat2Rooms(B_, H_, entr_wall, hall_pos, count_rooms):
    # Поиск топологий
    # Параметры - количество результатов, список комнат
    compartments_list = ["envelope",  "hall", "corr", "bath", "kitchen"]
    # ToDo надо добавлять еще 3-х и 4-хкомнатные квартиры
    if count_rooms==1:
        compartments_list += ["room"]
    else:
        compartments_list += ["room","room2"]
    max_results = 3
    recur_int = 0
    scens = main_topology(max_results, compartments_list, hall_pos)
    print scens

    # Визуализация
    i=0
    for pl in scens:
        if i%9==0:
            fig1 = plt.figure(figsize=(15, 15))
        ax1 = fig1.add_subplot(3,3,i%9+1, title='scen '+str(i), aspect='equal')
        visual2(quickplacement(pl), ax1)
        i+=1
        if (i>100):
            break

    # Учет ограничений по площади
    # Параметры - ширина, высота, сценарии (топологические)
    optim_scens = main_size(B_, H_, scens, entr_wall, hall_pos)
    # Визуализация
    i=0
    n=2
    for pl in optim_scens:
        if i%n**2==0:
            fig1 = plt.figure(figsize=(15, 15))
        ax1 = fig1.add_subplot(n,n,i%n**2+1, title='scen '+str(i)+ " " + str(res_x[i]), aspect='equal')
        visual(pl, ax1)
        i+=1
        if (i>30):
            break


Flat2Rooms(20, 20, (0,1),0, 2)