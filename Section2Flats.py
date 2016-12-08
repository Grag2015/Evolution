# -*- coding: utf-8 -*-
import itertools
import numpy as np
import time
import copy
import cPickle
#import pylab
# import PySide
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib
# matplotlib.use('Qt4Agg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
import re
from Flat2Rooms import place2scen
from preparedict import get_dict_sect_res
from preparedict import getplfun

#from knapsack import Knapsack
from pl_graph import createbounds
# настройки алгоритма
timeout = 15
depth_recurs = 100000
recur_int = 0
B=20
H=20
max_res = 10 #максимальное количество результатов, важно ограничивать для скорости работы
min_margin = 1.2
delta = 0.1

# переменная хранит индекс в xlist левой стены подъезда и передается в целевую функцию
x1ind=0
x2ind=0

# размеры подъезда
B1=6
H1=6
# предварительные размеры коридора для задачи о рюкзаке
# коридор горизонтальный
B2=B/2
H2=2

compartments_src = ["envelope",  "podezd", "corr"] #["flat1", "flat2", "flat3", "flat4"]
rooms_weights_src = [5, 0] #[1, 1, 1, 1] # веса комнат, используются для придания ограничений по каждому типу комнат
areaconstr_src = [(B1 - 0.2)*(H1 - 2), H2*H2] ## минимальные без оболочки
areaconstrmax_src = [(B1 + 0.2)*(H1 + 2), H2*B2] #[60*(1+delta),60*(1+delta),110*(1+delta),110*(1+delta)] #[4.5,1000,4.5,16,1000,1000] # максимальные без оболочки
widthconstrmin_src = [B1 - 0.2, 2] #4.5, 4.5, 4.5, 4.5] # минимальные без оболочки
widthconstrmax_src = [B1 + 0.2, 3] #100, 100, 100, 100] # максимальные без оболочки
sides_ratio_src = [0, 0] #1, 1, 1, 1] # вкл/выкл ограничение на соотношение сторон, без оболочки

#цвета для визуализации, без оболочки
comp_col_src = {0: '#73DD9B',
            1: '#73DD9B'
           }





len_comp=len(compartments_src)

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

envel_podezd = [(8, 9)]#list(set(inclusion_partcommon) - {(6, 9), (9, 6)}) # TODO - убираешь (9, 8) и сразу время работы вырастает в десять раз
envel_room = list(set(inclusion_partcommon) - {(9, 6)}) #(8, 7), (8, 9), (9, 8)}
bath_kitchen = partcommon_adjacency
# hall_other = partcommon #Для случая без коридора
podezd_corr = [(4,1)]#[(6,1),(5,1),(4,1),(3,1)]
podezd_flat = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(10,0),(11,0),(12,0),
               (0,1),(0,2),(0,3),(0,6),(0,9),(12,1),(12,2),(12,3),(12,6),(12,9),
               (1, 1), (1, 2), (1, 3), (1, 6), (1, 9), (11, 1), (11, 2), (11, 3), (11, 6), (11, 9)]
envel_corr = [(8,8)] #[(9,8),(8,8),(7,8),(6,8)]
envel_flat = [(7,6),(7,7),(7,9),(8,7),(8,9),(9,7),(9,9)]
corr_other = list(((set(partcommon) | set(inverse(partcommon))) | {(1,11),(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),
                                                                  (0,8),(0,9),(0,10),(0,11),(0,12),(11,0),(9,0)}) - {(1,4),(1,6)} ) # -
hall_other = list(set(partcommon) | {(0,0),(0,1),(0,2),(0,3),(0,5),(0,7),(0,10),(0,11),(0,12),(3,11)}) # используем для случая с коридором
bath_kitch2room = list(set(adjacency) | {(3,12), (4,12), (5,12), (2, 12), (5, 11)})
other_room2 = [(1, 3),  (3, 11), (4, 12), (1, 6), (0, 10), (0, 3), (12, 9), (1, 2), (0, 6),
               (1, 5), (0, 11),  (0, 4), (1, 10), (6, 11), (1, 4), (0, 5), (1, 9), (0, 8),
               (9, 11), (1, 8), (1, 7), (0, 9), (0, 7), (0, 2), (1, 11), (2, 11), (4, 11), (5, 11), (7, 11), (8, 11), (10, 11), (11, 11), (12, 11),
               (2, 1), (1, 1), (0, 1), (0, 0), (1, 0), (2, 0),
               (0,12),(1,12),(2,12),(3,12),(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),(12,12)]
            # вот эти под вопросом - ,
kitchen_livroom = list({(1,6), (6,1), (11,6), (6,11), (3,1), (4,1), (5,1),(1,3), (1,4), (1,5),(3,11), (4,11), (5,11),(11,3), (11,4), (11,5), (12,5)})
room2_bath = inverse(kitchen_livroom)
envel_kitchen = list({(7,7),(7,9),(9,7),(9,9)})

# Если нет коридора, то hall_other:=corr_other - это надо вынести в ф-ю main

# topologic constraints
# TODO эту матрицу тоже надо чистить
tc_src_s = [[[], envel_podezd, envel_corr],# envel_flat, envel_flat, envel_flat, envel_flat], #envelope
        [[], [], podezd_corr],# podezd_flat, podezd_flat, podezd_flat, podezd_flat], # "podezd"
        [[], [], []]]# corr_other, corr_other, corr_other, corr_other], # "corr"
        # [[], [], [], [], other_room2, other_room2, other_room2], # "flat1"
        # [[], [], [], [], [], other_room2, other_room2], # "flat2"
        # [[], [], [], [], [], [], other_room2], # "flat3"
        # [[], [], [], [], [], [], []]] #"flat4"


def create_constr():
    global compartments, rooms_weights, areaconstr, areaconstrmax, widthconstrmin, widthconstrmax, sides_ratio, comp_col, tc_src
    # B1 = 2.5
    # H1 = 15
    # # коридор горизонтальный
    # B2 = B / 2
    # H2 = 2
    print (B, H, B1, H1, B2, H2)
    #varres, areasres = Knapsack(B, H, B1, H1, B2, H2)
    #todo надо выносить в настройки
    r1 = int(round((B/7.),0))#int(round((B/2.-1)*10/55,0))
    r2 = int(round((H/7.),0))#int(round((B/2.-1)*H/55,0))
    nflats = min(max(r1*r2-2,4),8)# в алгоритме рассчитаны планировки максимум для 8 квартир в секции, минимум - 4 квартиры
    varres= [1]*nflats
    areasres= [50]*nflats
    print varres, areasres
    compartments = copy.deepcopy(compartments_src)
    rooms_weights = copy.deepcopy(rooms_weights_src)
    areaconstr = copy.deepcopy(areaconstr_src)
    areaconstrmax = copy.deepcopy(areaconstrmax_src)
    widthconstrmin = copy.deepcopy(widthconstrmin_src)
    widthconstrmax = copy.deepcopy(widthconstrmax_src)
    sides_ratio = copy.deepcopy(sides_ratio_src)
    comp_col = copy.deepcopy(comp_col_src)
    # добавление доп.ограничений на комнаты полученные из задачи о рюкзаке
    k = 0
    for j, s in enumerate(areasres):
        for t in range(int(varres[j])):
            k += 1
            # ToDO s = 40, т.е. площади не учитываем, главное чтобы минимальное для квартиры
            s = 40
            compartments.append("flat" + str(k))
            rooms_weights.append(0)
            areaconstr.append(s * (1 - delta))
            areaconstrmax.append(2*s * (1 + delta))
            widthconstrmin.append(4.5)
            widthconstrmax.append(15)
            sides_ratio.append(1)
            comp_col[k + 1] = '#ACBFEC'
    comp_col[k + 2]='#ACBFEC' # костыль, после обработки планировки иногда не хватает цветов
    comp_col[k + 3]='#ACBFEC' # костыль, после обработки планировки иногда не хватает цветов
    tc_src = copy.deepcopy(tc_src_s)
    tc_src[0] += [envel_flat]*(len(compartments)-3)
    tc_src[1] += [podezd_flat]*(len(compartments)-3)
    tc_src[2] += [corr_other]*(len(compartments)-3)
    tc_src[0][3] = [(9,7)] # после введения порядка на множестве квартир ("В" ниже или правее), самую первую квартиру можно ставить всегда в левый верхний угол
    for i in range(3, (len(compartments))):
        tt = []
        tt += [[]] * (i + 1)
        tt += [other_room2] * (len(compartments)-1-i)
        tc_src.append(tt)
    return sum(varres) # возвращает количество квартир

def prepare_tc(tc_src):
    tc = copy.deepcopy(tc_src)
    global len_comp
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
    # Есть выход в любую квартиру из коридора или подъезда
    isentr = {(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(2,1),(2,11),(3,1),(3,11),(4,1),(4,11),(5,1),(5,11),
              (6,1),(6,11),(7,1),(7,11),(8,1),(8,11),(9,1),(9,11),(10,1),(10,11),(11,2),(11,3),(11,4),(11,5),(11,6),(11,7),
              (11,8),(11,9),(11,10),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,9),(2,10)}
    for i in range(3,len_comp):
        if (len((set(scen[2][i]) | set(scen[1][i])) & isentr)==0):
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
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2.,
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

def visual_place_simple(placement_all):
    H = max(placement_all[0])
    B = max(placement_all[1])
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    fig1 = plt.figure(figsize=(20,20*H/B) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111)
    for i in range(1, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B), placement_all[1][2*i]/float(H)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H), alpha=0.6, label='test '+str(i),
                                         facecolor='#73DD9B', linestyle='-'
            )
        )

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
    fig1 = plt.figure(figsize=(25,15) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111)
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
# pl = [[0,20,10,15,0,10,15,20,0,17,17,20], [0,20,0,10,0,10,0,10,10,20,10,20]]
# функция формирует матрицы для целевой функции

def makeconst(pl, discret=True):
    placemnt = copy.deepcopy(pl)
    global Ax, Ay, Bx, By, bx, by, bounds, x1ind, x2ind, hall_pos_constr, flats_outwalls_constr, section_out_walls
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
        return xlist, ylist

    xlist, ylist = makematr(placemnt)

    bounds = createbounds(pl, B, H)
    print B, H, bounds

    # проверка bounds на корректность интервалов
    # если интервалы некорректны, то возвращаем большое число
    if len(filter(lambda x: x[1] - x[0] < 0, bounds))>0:
        return False

    # bounds[x1ind] = (B/2. - B1/2., B/2. - B1/2.)
    # bounds[x2ind] = (B/2. + B1/2., B/2. + B1/2.)
    # фиксируем высоту подъезда

    # находим и фиксируем переменные в xlist, ylist, которые отвечают за размеры подъезда
    y1 = pl[1][3]
    x1 = pl[0][2]
    x2 = pl[0][3]
    y1ind = ylist.index(y1)
    x1ind = xlist.index(x1)
    x2ind = xlist.index(x2)
    bounds[y1ind + len(xlist) - 1] = (H1, H1)
    bounds[x1ind] = (B/2. - B1/2., B/2. - B1/2.)

    # нужно зафиксировать интервал для высоты коридора (2-3), т.к. высота подъезда фиксирована H1, то надо найти в
    # ylist переменную, которая отвечают за размеры подъезда и зафиксировать в bounds интервал изменения (B1+2,B1+3)
    y1corr = pl[1][5]
    y1indcorr = ylist.index(y1corr)
    bounds[y1indcorr + len(xlist) - 1] = (B1+2,B1+3)

    # удаляем правую границу подъезда из списка ограничений
    bounds.pop(x2ind)

    # делаем дополнительные ограничения для учета внешних стен и позиции коридора для этапа создания планировок
    hall_pos_constr = []
    scen = place2scen(pl)
    for i in range(3, len(scen)):
        hall_pos_constr.append(entrwall_hall_pos(scen[2][i], scen[1][i])[0])

    flats_outwalls_constr= flats_outwalls(pl, section_out_walls)

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
    global hall_pos_constr, flats_outwalls_constr

    #print xys

    x = xy[0:len(Ax[0]) - 2]
    # операция вставки требует много ресурсов, помноженная на количество вызовов ф-и func2_discret может сказаться в целом на производительности

    x = np.insert(x, x2ind, x[x1ind]+B1) # Добавляем элемент соотв-щий правой стенке подъезда, со значением левая стенка + ширина подъезда

    xb = np.append(x, B)
    y = xy[len(Ax[0]) - 2:len(Ax[0]) + len(Ay[0]) - 2]
    yb = np.append(y, H)

    # # Ограничение по площади снизу
    # #print x, y
    # res1 = Ax.dot(xb) * Ay.dot(yb) - areaconstr
    # # Ограничение по площади сверху
    # res1max = areaconstrmax - Ax.dot(xb) * Ay.dot(yb)

    # Ограничение на расположение соседних стен
    res2 = Bx.dot(x) - [min_margin]*len(Bx)#np.sign(Bx.dot(xy[0:len(Ax[0])-1]))*min_margin
    res3 = By.dot(y) - [min_margin]*len(By) #- np.sign(By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]))*min_margin
    # ограничение на соотношение сторон
    res4 = map(lambda d: int((d>=1./2.5)&(d<=2.5))-1, Ay.dot(yb)/Ax.dot(xb))*np.array(sides_ratio)
    # # ограничение на минимальную ширину
    # res5 = Ax.dot(xb) - widthconstrmin
    # res6 = Ay.dot(yb) - widthconstrmin

    # ограничение на максимальную ширину
    # res7 = np.array(widthconstrmax) - np.array(map(min, zip(Ax.dot(xb),Ay.dot(yb))))

    # res1sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res1))
    # res1maxsign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res1max))
    res2sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res2))
    #print "res2sign ", res2sign
    res3sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res3))
    #print "res3sign ", res3sign
    res4sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res4))
    #print "res4sign ", res4sign
    # res5sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res5))
    # res6sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res6))
    # res7sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res7))

    # параметры для базы/словаря планировок
    blist = Ax.dot(xb)[2:] #вектор ширины по всем квартирам кроме подъезда и коридора
    hlist = Ay.dot(yb)[2:] #вектор длины по всем квартирам кроме подъезда и коридора
    #print zip(blist, hlist, flats_outwalls_constr, hall_pos_constr)
    totalfuns = sum(map(lambda x: getplfun(((x[0], x[1]), tuple(x[2]), x[3])), zip(blist, hlist, flats_outwalls_constr, hall_pos_constr)))
    #print "totalfuns ", totalfuns
    return sum(res2sign)*50 + sum(res3sign)*50 + sum(res4sign) + totalfuns

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
        st = st + N[0][t] # TODO тут возможно ошибка
    st = set(st)
    for t in range(len(dct)):
        if dct[t] in st:
            s += korner[t]
    if s >= 4:
        return True
    else:
        return False

def my_differential_evolution(func2_discret, bounds):
    #res_fun = 10
    res = opt.differential_evolution(func2_discret, bounds, popsize=30, tol=0.01, strategy="randtobest1bin", init='random')
    # while (res_fun >=10):
    #     res = opt.differential_evolution(func2_discret, bounds, popsize=30, tol=0.01, strategy="randtobest1bin", init='random')
    #     res_fun = res.fun
    #     print res.fun
    res.x = np.insert(res.x, x2ind, res.x[x1ind] + B1)
    return res

# Поиск различных вариантов компоновки (топологий)
# ЗАГЛУШКА
def main_topology(max_results, B_, H_, printres = True, usetemplate = True):
    """
    >>> main_topology(10, ["envelope",  "hall", "corr", "room", "room2", "bath", "kitchen"], False)[0][1]
    [[(3, 6)], [(6, 6)], [(1, 7)], [(0, 9)], [(1, 9)], [(0, 9)], [(0, 9)]]
    """
    # global max_res, compartments, recur_int, nres, stop, rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col, len_comp, areaconstrmax
    # max_res = max_results
    #
    # # sc = [[[[(6, 6)], [(9, 9)], [(8, 8)], [(7, 9)], [(7, 8)], [(9, 7)], [(7, 7)]],
    # #  [[(3, 3)], [(6, 6)], [(1, 7)], [(1, 9)], [(0, 7)], [(3, 1)], [(0, 1)]],
    # #  [[(4, 4)], [(11, 5)], [(6, 6)], [(3, 11)], [(1, 6)], [(5, 1)], [(1, 1)]],
    # #  [[(5, 3)], [(11, 3)], [(9, 1)], [(6, 6)], [(7, 1)], [(10, 0)], [(7, 0)]],
    # #  [[(5, 4)], [(12, 5)], [(11, 6)], [(5, 11)], [(6, 6)], [(11, 1)], [(6, 1)]],
    # #  [[(3, 5)], [(9, 11)], [(7, 11)], [(2, 12)], [(1, 11)], [(6, 6)], [(1, 6)]],
    # #  [[(5, 5)], [(12, 11)], [(11, 11)], [(5, 12)], [(6, 11)], [(11, 6)], [(6, 6)]]]]
    # # return sc
    #
    # # подготовка списков и таблиц с ограничениями TODO добавить здесь новые ограничения
    # changing_lists = [rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col, areaconstrmax]
    # new_lists=[]
    # for i in range(len(changing_lists)): new_lists.append([])
    # for i in range(len(compartments[1:])):
    #     if (compartments[1:][i] in set(compartments_list)):
    #         for j in range(len(changing_lists)):
    #             new_lists[j].append(changing_lists[j][i])
    #
    # rooms_weights = new_lists[0]
    # areaconstr = new_lists[1]
    # areaconstr_opt = new_lists[2]
    # sides_ratio = new_lists[3]
    # comp_col = new_lists[4]
    #
    # k = 0
    # for i in range(len(compartments)):
    #     if (not (compartments[i] in set(compartments_list))):
    #         # удаляем строку i
    #         # print k
    #         tc_src.pop(k)
    #         # удаляем столбец i
    #         for j in range(len(tc_src)):
    #             tc_src[j].pop(k)
    #         k -= 1
    #     k += 1
    #
    # compartments = compartments_list
    # len_comp = len(compartments)
    # ГОТОВЫЕ СЦЕНАРИИ ДЛЯ РАЗЛИЧНОГО ЧИСЛА КВАРТИР

    #n=
    global len_comp, max_res, B, H, stop, tc_src
    max_res = max_results
    B = B_
    H = H_
    n = create_constr()
    len_comp = len(compartments)
    tc = prepare_tc(tc_src)

    if usetemplate:
        # загружаем шаблоны
        file = open("D:\YandexDisk\EnkiSoft\Evolution\dict_sect2flats.txt", "rb")
        dict_sect2flats = cPickle.load(file)
        file.close()
        # ЗАГЛУШКИ
        #print "dict_sect2flats[n]", n
        #print dict_sect2flats[n][0:min(max_results, len(dict_sect2flats[n]))]
        return dict_sect2flats[n][0:min(max_results, len(dict_sect2flats[n]))]

    # /ГОТОВЫЕ СЦЕНАРИИ ДЛЯ РАЗЛИЧНОГО ЧИСЛА КВАРТИР

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
    # import cPickle
    # file = open("d:\YandexDisk\EnkiSoft\Evolution\dump.txt", 'r')
    # scens = cPickle.load(file)
    # file.close()

    scens = EnumerateScenarios(N)
    t2 = time.clock()
    if printres:
        print "Найдено " + str(len(scens)) + " вариантов размещения комнат" + '\n' + "Время выполнения программы sec.- " + str(t2-t1)

    return scens

# Учет ограничений по площади/длине
def main_size(width, height, scens):
    global B, H, res_x
    B = width
    H = height
    t1 = time.clock()
    optim_scens=[]
    res_x=[]
    bestmin = 1000
    bestmini = 0
    for i in range(len(scens)):
        try:
            if not makeconst(quickplacement(scens[i])):
                continue
            #print quickplacement(scens[i])
            res = my_differential_evolution(func2_discret, bounds)
            res_x.append(func2_discret_results(res.x))
            #print res_x[-1]
            if (res.fun < bestmin) & (res_x[-1].find("dist_neib")==-1):
                bestmin = res.fun
                bestmini = i
                print 'bestmini', bestmini
            #print res.message, "nit: ", res.nit
            #print 'bounds', bounds
            xlistnew = list(res.x[0:len(Ax[0]) - 1])
            ylistnew = list(res.x[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2])
            #print i
            optim_scens.append(optim_placement(quickplacement(scens[i]), xlistnew, ylistnew))
        except ValueError:
            print('ОШИБКА: Планировка '+str(i)+' не была рассчитана!')
    t2 = time.clock()
    print "Расчет размеров комнат закончен! Время выполнения программы sec.- " + str(t2 - t1)
    res_tmp = []
    res_tmp.append(optim_scens[bestmini])
    return res_tmp, bestmini

# расчет внешних стен для квартир
def flats_outwalls(new_scen_res,section_out_walls):
    will_put_walls = {(7, 6): (0, 1, 1, 1), (7, 7): (0, 1, 1, 0), (7, 9): (0, 0, 1, 1), (8, 7): (0, 1, 0, 0),
                      (8, 9): (0, 0, 0, 1), (9, 7): (1, 1, 0, 0), (9, 9): (1, 0, 0, 1)}
    sc_tmp = place2scen(new_scen_res)
    flats_out_walls = []
    for i in range(3, len(sc_tmp)):  # не берем 3 служ. помещения (енвелоп, подъезд, коридор)
        flats_out_walls.append(map(lambda x: x[0] * x[1], zip(will_put_walls[sc_tmp[0][i][0]], section_out_walls)))
    return flats_out_walls

# Section2Flats(25, 15)
def Section2Flats(B_, H_, out_walls, showgraph = False, mode = 3):
    '''

    # Поиск топологий секции
    имеет 3 режима работы
    1 - считаем топологии и планировки с 0
    2 - топологии загружаем из базы и планировки рассчитываем с 0
    3 - топологии и планировки загружаем из базы (по умолчанию)
    :param B_:
    :param H_:
    :param out_walls:
    :param showgraph:
    :param mode: имеет 3 режима работы
    :return:
    '''

    global section_out_walls, B, H
    B,H = (B_,H_)
    section_out_walls = out_walls

    if mode < 3:
        usetemplate = True
        if mode == 1:
            usetemplate = False
        scens = main_topology(3, B_, H_, usetemplate = usetemplate)

        # # Визуализация
        # if showgraph:
        #     i=0
        #     n=1
        #     for t,pl in enumerate(scens):
        #         if i%(n**2)==0:
        #             fig1 = plt.figure(figsize=(20,20*float(H_)/B_))
        #         ax1 = fig1.add_subplot(n,n,i%(n**2)+1, title='scen '+str(i))
        #         visual2(quickplacement(pl),ax1)
        #         i+=1
        #         if (i>100):
        #             break
        #
        #     plt.show()
        # # print scens

        # Учет ограничений по площади
        # Параметры - ширина, высота, сценарии (топологические)
        optim_scens, bestmini = main_size(B_, H_, scens)

    else:
        optim_scens = get_dict_sect_res(((B_, H_), section_out_walls))
        if optim_scens == 0:
            return ([],[],[],[])

    new_scen_res, hall_pos_res, entrwall_res = check_pl(place2scen(optim_scens), optim_scens, active=False)


    # расчет внешних стен для квартир

    flats_out_walls = flats_outwalls(new_scen_res,out_walls)

    print "new_scen_res", new_scen_res
    # заглушка
    # new_scen_res =[[0,25,11.832458301964532,18.186082541575203,0,18.186082541575203,18.186082541575203,25,0,9.0930412707876016,
    #                 9.0930412707876016,18.186082541575203,0,5.9162291509822662,5.9162291509822662,11.832458301964532],
    #                [0,15,0,5.2908772211446049,5.2908772211446049,7.4294138335360795,0,15,7.4294138335360795,15,
    #                 7.4294138335360795,15,0,5.2908772211446049,0,5.2908772211446049]]

    # Визуализация
    if showgraph:
        i=0
        n=1
        tt= []
        tt.append(new_scen_res)
        for pl in tt:
            if i%n**2==0:
                fig1 = plt.figure(figsize=(20,20*float(H_)/B_))
            ax1 = fig1.add_subplot(n,n,i%n**2+1, title='scen '+str(i)+ " " + str(res_x[i]))
            visual(pl, ax1)
            i+=1
            if (i>30):
                break

        i = 0
        n = 1
        for pl in optim_scens:
            if i % n ** 2 == 0:
                fig1 = plt.figure(figsize=(20, 20 * float(H_) / B_))
            ax1 = fig1.add_subplot(n, n, i % n ** 2 + 1, title='scen ' + str(i) + " " + str(res_x[i]))
            visual(pl, ax1)
            i += 1
            if (i > 30):
                break

        plt.show()

    return new_scen_res, hall_pos_res, entrwall_res, flats_out_walls

# функция возвращает позицию угла и входную стену принимая отношения корр-комната, подъезд-комната
def entrwall_hall_pos(corr_flat, podezd_flat):
    # пример входных данных - [(2, 11)], [(0, 3)]
    noCorridEntr={(0, 10), (0, 3), (1, 11), (0, 11), (0, 4), (0, 0), (9, 0), (0, 12), (11, 0), (0, 5), (0, 8), (0, 1), (0, 6),
     (0, 9), (0, 7), (0, 2)}
    if corr_flat[0] in noCorridEntr:
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
            (5, 1): (0, (3,1)),
            (10, 1): (0, (3,0)),
            (3, 1): (0, (3,1)),
            (2, 1): (0, (3,1)),
            (1, 6): (0, (0,1)), #(1, 6): (2, (0,0))
            (1, 9): (2, (0,0)),
            (1, 8): (2, (0,0)),
            (1, 7): (0, (0,1)), #(1, 7): (2, (0,0))
            (7, 11): (0, (1,0)),
            (6, 11): (0, (1,0)),
            (8, 11): (0, (1,0)),
            (9, 11): (0, (1,0)),
            (11, 6): (2, (2,0)),
            (11, 9): (2, (2,0)),
            (11, 7): (2, (2,0)),
            (11, 8): (2, (2,0)),
            (8, 1): (0, (3,0)),
            (7, 1): (0, (3,0)),
            (6, 1): (0, (3,0)),
            (9, 1): (0, (3,0)),
            (4, 1): (1, (3,0)),
            (11, 4): (1, (2,1)),
            (1, 4): (1, (0,0)),
            (4, 11): (1, (1,0))}
    return dct[tmp[0]]

# Todo надо искать наверное другой метод оптимизации, очень плохо рассчитывает например такую топологию
# https://yadi.sk/i/0-wdAf5gxYKcL
# [[[(6, 6)], [(8, 9)], [(9, 8)], [(7, 6)], [(8, 9)], [(9, 9)], [(9, 7)]],
#  [[(4, 3)], [(6, 6)], [(5, 1)], [(1, 3)], [(11, 6)], [(12, 6)], [(5, 0)]],
#  [[(3, 4)], [(7, 11)], [(6, 6)], [(1, 4)], [(8, 11)], [(9, 11)], [(6, 1)]],
#  [[(5, 6)], [(11, 9)], [(11, 8)], [(6, 6)], [(12, 9)], [(12, 9)], [(11, 7)]],
#  [[(4, 3)], [(1, 6)], [(4, 1)], [(0, 3)], [(6, 6)], [(11, 6)], [(4, 0)]],
#  [[(3, 3)], [(0, 6)], [(3, 1)], [(0, 3)], [(1, 6)], [(6, 6)], [(3, 0)]],
#  [[(3, 5)], [(7, 12)], [(6, 11)], [(1, 5)], [(8, 12)], [(9, 12)], [(6, 6)]]]


# Todo объединять несколько блоков, считать площадь и снова разбивать
# Для подъезда надо ширину корректировать отдельно как вариант
# Todo как работать с однородными блоками?

# проверка и корректировка готовой планировки
def check_pl(scen, pl, active = True):
    '''
    функция обрабатывает готовую планировку секции (2 уровня - нижний и верхний)
    :param scen:
    :param pl:
    :param active: True - делаем корректировку секции, False - не делаем
    :return:
    '''
    new_scen = copy.deepcopy(pl)
    hall_pos = []
    entrwall = []
    for i in range(3, len(scen)):
        hall_pos.append(entrwall_hall_pos(scen[2][i], scen[1][i])[0])
        entrwall.append(entrwall_hall_pos(scen[2][i], scen[1][i])[1])
    # берем коридор и смотрим, что есть выше и ниже
    # если есть часть общей стены сверху коридора
    if active:
        up_corr = []
        down_corr = []
        for i in range(3, len(scen[0])):
            if scen[2][i][0] in {(2,1),(7,1),(8,1),(9,1),(10,1),(6,1)}:
                up_corr.append(i)
            else:
                # если есть часть общей стены снизу коридора
                if scen[2][i][0] in {(2,11),(7,11),(8,11),(9,11),(10,11),(6,11)}:
                    down_corr.append(i)
        # делаем предплоложение, что объединение всех комнат в up_corr и down_corr представляют прямоугольник
        # подсчет площади объед-х комнат
        will_deleted = []
        print up_corr, down_corr
        # проверка для up_corr
        a = 0
        b = 0
        for i in range(len(up_corr)):
            a += (pl[0][up_corr[i]*2+1]-pl[0][up_corr[i]*2])
            b = (pl[1][up_corr[i]*2+1]-pl[1][up_corr[i]*2])
        print "a,b", a, b
    # проверка площади объединения, ratio
        if (a*b < 60) & (a*b > 0): # объединяем все в одну квартиру
            for t, i in enumerate(up_corr):
                # new_scen[0].pop(2*i - t*2)
                # new_scen[0].pop(2*i - t*2)
                # new_scen[1].pop(2*i - t*2)
                # new_scen[1].pop(2*i - t*2)
                will_deleted.append(i)
            new_scen[0].append(min(map(lambda x: pl[0][2*x], up_corr)))
            new_scen[0].append(max(map(lambda x: pl[0][2*x+1], up_corr)))
            new_scen[1].append(pl[1][2*up_corr[0]])
            new_scen[1].append(pl[1][2*up_corr[0] + 1])
            hall_pos.append(1)
            entrwall.append((3,1))
        else:
            if a*b >= 60:
                if float(a)/b > 2.5:
                    # делим на 2
                    for t, i in enumerate(up_corr):
                        #print t, i
                        # new_scen[0].pop(2*i - t * 2)
                        # new_scen[0].pop(2*i - t * 2)
                        # new_scen[1].pop(2*i - t * 2)
                        # new_scen[1].pop(2*i - t * 2)
                        will_deleted.append(i)
                    tmp_min = min(map(lambda x: pl[0][2 * x], up_corr))
                    tmp_max = max(map(lambda x: pl[0][2 * x + 1], up_corr))
                    new_scen[0].append(tmp_min)
                    new_scen[0].append(tmp_min + (tmp_max-tmp_min)/2.)
                    new_scen[0].append(tmp_min + (tmp_max-tmp_min)/2.)
                    new_scen[0].append(tmp_max)
                    new_scen[1].append(pl[1][2 * up_corr[0]])
                    new_scen[1].append(pl[1][2 * up_corr[0] + 1])
                    new_scen[1].append(pl[1][2 * up_corr[0]])
                    new_scen[1].append(pl[1][2 * up_corr[0] + 1])
                    hall_pos.append(0)
                    hall_pos.append(0)
                    entrwall.append((3, 0))
                    entrwall.append((3, 0))
                else:
                    if float(2*b)/a <= 2.5:
                        # делим на 2
                        for t, i in enumerate(up_corr):
                            #print t, i
                            # new_scen[0].pop(2*i - t * 2)
                            # new_scen[0].pop(2*i - t * 2)
                            # new_scen[1].pop(2*i - t * 2)
                            # new_scen[1].pop(2*i - t * 2)
                            will_deleted.append(i)
                        tmp_min = min(map(lambda x: pl[0][2 * x], up_corr))
                        tmp_max = max(map(lambda x: pl[0][2 * x + 1], up_corr))
                        print tmp_min,tmp_max
                        new_scen[0].append(tmp_min)
                        new_scen[0].append(tmp_min + (tmp_max-tmp_min)/2.)
                        new_scen[0].append(tmp_min + (tmp_max-tmp_min)/2.)
                        new_scen[0].append(tmp_max)
                        new_scen[1].append(pl[1][2 * up_corr[0]])
                        new_scen[1].append(pl[1][2 * up_corr[0] + 1])
                        new_scen[1].append(pl[1][2 * up_corr[0]])
                        new_scen[1].append(pl[1][2 * up_corr[0] + 1])
                        hall_pos.append(0)
                        hall_pos.append(0)
                        entrwall.append((3, 0))
                        entrwall.append((3, 0))
                    else: # объединяем в одну квартиру
                        for t, i in enumerate(up_corr):
                            # new_scen[0].pop(i - t * 2)
                            # new_scen[0].pop(i - t * 2)
                            # new_scen[1].pop(i - t * 2)
                            # new_scen[1].pop(i - t * 2)
                            will_deleted.append(i)
                        new_scen[0].append(min(map(lambda x: pl[0][2 * x], up_corr)))
                        new_scen[0].append(max(map(lambda x: pl[0][2 * x + 1], up_corr)))
                        new_scen[1].append(pl[1][2 * up_corr[0]])
                        new_scen[1].append(pl[1][2 * up_corr[0] + 1])
                        hall_pos.append(1)
                        entrwall.append((3, 0))

        # # проверка для down_corr
        # a = 0
        # b = 0
        # for i in range(len(down_corr)):
        #     a += (pl[0][down_corr[i] * 2 + 1] - pl[0][down_corr[i] * 2])
        #     b = (pl[1][down_corr[i] * 2 + 1] - pl[1][down_corr[i] * 2])
        # print "a,b", a, b
        # # проверка площади объединения, ratio
        # if (a * b < 60) & (a*b > 0):  # объединяем все в одну квартиру
        #     for t, i in enumerate(down_corr):
        #         # new_scen[0].pop(2*i - t*2)
        #         # new_scen[0].pop(2*i - t*2)
        #         # new_scen[1].pop(2*i - t*2)
        #         # new_scen[1].pop(2*i - t*2)
        #         will_deleted.append(i)
        #     new_scen[0].append(min(map(lambda x: pl[0][2 * x], down_corr)))
        #     new_scen[0].append(max(map(lambda x: pl[0][2 * x + 1], down_corr)))
        #     new_scen[1].append(pl[1][2 * down_corr[0]])
        #     new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #     hall_pos.append(1)
        #     entrwall.append((1, 1))
        # else:
        #     if a * b >= 60:
        #         if float(a) / b > 2.5:
        #             # делим на 2
        #             for t, i in enumerate(down_corr):
        #                 #print t, i
        #                 # new_scen[0].pop(2*i - t * 2)
        #                 # new_scen[0].pop(2*i - t * 2)
        #                 # new_scen[1].pop(2*i - t * 2)
        #                 # new_scen[1].pop(2*i - t * 2)
        #                 will_deleted.append(i)
        #             tmp_min = min(map(lambda x: pl[0][2 * x], down_corr))
        #             tmp_max = max(map(lambda x: pl[0][2 * x + 1], down_corr))
        #             new_scen[0].append(tmp_min)
        #             new_scen[0].append(tmp_min + (tmp_max - tmp_min) / 2.)
        #             new_scen[0].append(tmp_min + (tmp_max - tmp_min) / 2.)
        #             new_scen[0].append(tmp_max)
        #             new_scen[1].append(pl[1][2 * down_corr[0]])
        #             new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #             new_scen[1].append(pl[1][2 * down_corr[0]])
        #             new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #             hall_pos.append(0)
        #             hall_pos.append(0)
        #             entrwall.append((1, 0))
        #             entrwall.append((1, 0))
        #         else:
        #             if float(2 * b) / a <= 2.5:
        #                 # делим на 2
        #                 for t, i in enumerate(down_corr):
        #                     #print t, i
        #                     # new_scen[0].pop(2*i - t * 2)
        #                     # new_scen[0].pop(2*i - t * 2)
        #                     # new_scen[1].pop(2*i - t * 2)
        #                     # new_scen[1].pop(2*i - t * 2)
        #                     will_deleted.append(i)
        #                 tmp_min = min(map(lambda x: pl[0][2 * x], down_corr))
        #                 tmp_max = max(map(lambda x: pl[0][2 * x + 1], down_corr))
        #                 print tmp_min, tmp_max
        #                 new_scen[0].append(tmp_min)
        #                 new_scen[0].append(tmp_min + (tmp_max - tmp_min) / 2.)
        #                 new_scen[0].append(tmp_min + (tmp_max - tmp_min) / 2.)
        #                 new_scen[0].append(tmp_max)
        #                 new_scen[1].append(pl[1][2 * down_corr[0]])
        #                 new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #                 new_scen[1].append(pl[1][2 * down_corr[0]])
        #                 new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #                 hall_pos.append(0)
        #                 hall_pos.append(0)
        #                 entrwall.append((1, 0))
        #                 entrwall.append((1, 0))
        #             else:
        #                 for t, i in enumerate(down_corr):
        #                     # new_scen[0].pop(2*i - t * 2)
        #                     # new_scen[0].pop(2*i - t * 2)
        #                     # new_scen[1].pop(2*i - t * 2)
        #                     # new_scen[1].pop(2*i - t * 2)
        #                     will_deleted.append(i)
        #                 new_scen[0].append(min(map(lambda x: pl[0][2 * x], down_corr)))
        #                 new_scen[0].append(max(map(lambda x: pl[0][2 * x + 1], down_corr)))
        #                 new_scen[1].append(pl[1][2 * down_corr[0]])
        #                 new_scen[1].append(pl[1][2 * down_corr[0] + 1])
        #                 hall_pos.append(1)
        #                 entrwall.append((1, 0))

        # удалить лишние элементы will_deleted

        will_deleted.sort()
        for t, i in enumerate(will_deleted):
            new_scen[0].pop(2*i - t * 2)
            new_scen[0].pop(2*i - t * 2)
            new_scen[1].pop(2*i - t * 2)
            new_scen[1].pop(2*i - t * 2)
            hall_pos.pop(i-3-t) # 3 - число служебных элементов envelop, podezd, corr
            entrwall.pop(i-3-t)

    # ToDo тут надо пересчитать hall_pos, entrwall
    return new_scen, hall_pos, entrwall




