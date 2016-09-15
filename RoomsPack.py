import itertools
import numpy as np
import time
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re

# настройки алгоритма
timeout = 15
depth_recurs = 10000
recur_int = 0
B=5
H=6
max_res = 10 #максимальное количество результатов, важно ограничивать для скорости работы
min_margin = 0.5
# atomic relations block algebra
ARelBA = [[(y, x) for x in range(13)] for y in range(13)]

# комнаты
# TODO удалить лишние элементы в списке (коридор)
compartments = ["envelope",  "hall", "corr", "room", "room2", "bath", "kitchen"]
rooms_weights = [1, 1, 2, 2, 1, 1.5] # веса комнат, используются для придания ограничений по каждому типу комнат
areaconstr = [1,1,14,14,3.6,9] # минимальные без оболочки
areaconstr_opt = [3,1,16,16,4,12] # оптимальные без оболочки
sides_ratio = [0, 0, 1, 1, 1, 1] # вкл/выкл ограничение на соотношение сторон, без оболочки
#цвета для визуализации, без оболочки
comp_col = {0: '#ECA7A7',
            1: '#73DD9B',
            2: '#ACBFEC',
            3: '#ACBFEC',
            4: '#EAE234',
            5: '#ECA7A7'
           }


# Ограничения
all_const = set()
for i in range(13):
    for j in range(13):
        all_const.add(ARelBA[i][j])


# часть общей стены + минимум одна смежная стена
partcommon_adjacency = {(1,3),(1,5),(1,6),(1,7),(1,9),(3,1),(5,1),(6,1),(7,1),(9,1)}
# часть общей стены
partcommon = partcommon_adjacency | {(1,2),(1,4),(1,8),(1,10),(2,1),(4,1),(8,1),(10,1), (11,6),(6,11)}
# А содержит В и есть 1,2 общая часть стены
inclusion_partcommon = {(9,6),(9,7),(9,8),(9,9),(7,6),(7,7),(7,8),(7,9),(8,6),(8,7),(8,9),(6,9),(6,10)}

# смежные
adjacency = {ARelBA[1][1], ARelBA[2][1],ARelBA[3][1], ARelBA[4][1],ARelBA[5][1],ARelBA[6][1],ARelBA[6][11],ARelBA[7][1],ARelBA[8][1],ARelBA[9][1],ARelBA[10][1],ARelBA[11][1], \
        ARelBA[1][2], ARelBA[1][3], ARelBA[1][4], ARelBA[1][5], ARelBA[1][6], ARelBA[1][7], ARelBA[1][8], ARelBA[1][9], ARelBA[1][10], ARelBA[11][6],
        ARelBA[0][1], ARelBA[0][2], ARelBA[0][3], ARelBA[0][4], ARelBA[0][5],ARelBA[0][6], ARelBA[0][7],ARelBA[0][8], ARelBA[0][9], ARelBA[0][10], ARelBA[0][11],
        ARelBA[1][0], ARelBA[2][0], ARelBA[3][0], ARelBA[4][0], ARelBA[5][0], ARelBA[6][0], ARelBA[7][0], ARelBA[8][0], ARelBA[9][0], ARelBA[10][0], ARelBA[11][0]}

def inverse(noatomicBArel):
    res=set()
    for elem in noatomicBArel:
        res.add((12-elem[0],12-elem[1]))
    return res

envel_hall = inclusion_partcommon
envel_room = inclusion_partcommon #- {(7, 8), (8, 7), (8, 9), (9, 8)}
bath_kitchen = partcommon_adjacency
# hall_other = partcommon #Для случая без коридора
hall_corr = partcommon - {(1,6),(6,1)} #Для случая c коридор
envel_corr = inclusion_partcommon | {(8,8)}
corr_other = partcommon | inverse(partcommon)

# topologic constraints
# TODO эту матрицу тоже надо чистить
tc_src=[[set(), envel_hall, envel_corr, envel_room, envel_room, envel_room, envel_room],
    [set(),set(), hall_corr , adjacency, adjacency, adjacency , adjacency],
    [set(),set(), set(), corr_other, corr_other, corr_other, corr_other],
    [set(), set(), set(), set(), adjacency, adjacency, adjacency],
    [set(), set(), set(), set(), set(), adjacency, adjacency],
    [set(), set(), set(), set(), set(), set(), bath_kitchen],
    [set(), set(), set(), set(), set(), set(), set()]]

# envel_hall | envel_corr | envel_room



def prepare_tc(tc_src):
    tc = copy.deepcopy(tc_src)
    # верхний треугольник оставляем без изменений
    # диагональ заполняем значением (6,6)
    for i in range(len(compartments)):
        tc[i][i].add((6,6))

    # нижний треугольник заполняем симметричными элементами преобразованными ф-ей inverse
    for i in range(0,len(compartments)): # go along rows
        for j in range(i+1, len(compartments)): # go along columns
            tc[j][i] = inverse(tc[i][j])
    return tc

# Подготовка матрицы ограничений tc_src
tc = prepare_tc(tc_src)

# interval algebra composition matrix
def atomicIAcomp(IArel1, IArel2):
    IAcomp=[[{0},{0},{0},{0},{0,1,2,3,4},{0,1,2,3,4},{0},{0},{0},{0},{0,1,2,3,4},{0,1,2,3,4},{0,1,2,3,4,5,6,7,8,9,10,11,12}],
            [{0},{0},{0},{1},{2,3,4},{2,3,4},{1},{0},{0},{1},{0,1,2,3,4},{5,6,7},{8,9,10,11,12}],
            [{0},{0},{0,1,2},{0},{2,3,4},{2,3,4},{2},{0,1,2},{0,1,2,7,8},{2,7,8},{2,3,4,5,6,7,8,9,10},{8,9,10},{8,9,10,11,12}],
            [{0},{0},{0,1,2},{3},{4},{4},{3},{0,1,2},{0,1,2,7,8},{3,6,9},{4,5,10},{11},{12}],
            [{0},{0},{0,1,2,3,4},{4},{4},{4},{4},{0,1,2,3,4},{0,1,2,3,4,5,6,7,8,9,10,11,12},{4,5,10,11,12},{4,5,10,11,12},{12},{12}],
            [{0},{1},{2,3,4},{4},{4},{5},{5},{5,6,7},{8,9,10,11,12},{10,11,12},{10,11,12},{12},{12}],
            [{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}],
            [{0},{1},{2},{2},{2,3,4},{5,6,7},{7},{7},{8},{8},{8,9,10},{8,9,10},{8,9,10,11,12}],
            [{0,1,2,7,8},{2,7,8},{2,7,8},{2,7,8},{2,3,4,5,6,7,8,9,10},{8,9,10},{8},{8},{8},{8},{8,9,10},{8,9,10},{8,9,10,11,12}],
            [{0,1,2,7,8},{2,7,8},{2,7,8},{3,6,9},{4,5,10},{10},{9},{8},{8},{9},{10},{11},{12}],
            [{0,1,2,7,8},{2,7,8},{2,3,4,5,6,7,8,9,10},{4,5,10},{4,5,10},{10},{10},{8,9,10},{8,9,10,11,12},{10,11,12},{10,11,12},{12},{12}],
            [{0,1,2,7,8},{3,6,9},{4,5,10},{4,5,10},{4,5,10},{11},{11},{11},{12},{12},{12},{12},{12}],
            [{0,1,2,3,4,5,6,7,8,9,10,11,12},{4,5,10,11,12},{4,5,10,11,12},{4,5,10,11,12},{4,5,10,11,12},{12},{12},{12},{12},{12},{12},{12},{12}]]
    return IAcomp[IArel1][IArel2]

# декартово произведение множеств
def cartesProduct(set1, set2):
    cp=set()
    for i in set1:
        for j in set2:
            cp.add((i,j))
    return cp

# композиция атомарных элементов блочной алгебры
def atomicBAcomp(atomicBArel1, atomicBArel2):
    return cartesProduct(atomicIAcomp(atomicBArel1[0],atomicBArel2[0]),atomicIAcomp(atomicBArel1[1],atomicBArel2[1]))

# композиция НЕатомарных элементов блочной алгебры
def noatomicBAcomp(noatomicBArel1, noatomicBArel2):
    res=set()
    for i in noatomicBArel1:
        for j in noatomicBArel2:
            res= res | atomicBAcomp(i,j)
    return res

# ищем пути из i в j xthtp 3-ю точку, но не k
def Paths(i,j,k):
    ls = range(len(compartments))
    ls.remove(k)
    ls.remove(i)
    ls.remove(j)
    res=set()
    for elem in ls:
        res.add((i,j,elem))
    return res

# Функция поиска допустимых подмножеств
def PathConsistency(C):
    LPathsToVisit = set()
    NPathsChecked = 0
    NChanges = 0

    # begin first loop
    samples_3 = set(itertools.permutations(range(len(compartments)),3))
    for elem in samples_3:
        NPathsChecked+=1
        if (elem in LPathsToVisit):
            LPathsToVisit.remove(elem)
        TmpCij = C[elem[0]][elem[1]] & noatomicBAcomp(C[elem[0]][elem[2]],C[elem[2]][elem[1]])
        if (len(TmpCij)==0):
            # print C[elem[0]][elem[1]]
            # print noatomicBAcomp(C[elem[0]][elem[2]],C[elem[2]][elem[1]])
            return (elem, C, NPathsChecked, NChanges)
        if (TmpCij != C[elem[0]][elem[1]]):
            NChanges += 1
            # print C[elem[0]][elem[1]]
            # print TmpCij
            C[elem[0]][elem[1]] = TmpCij
            C[elem[1]][elem[0]] = inverse(TmpCij)
            # print 'union',  C[elem[0]][elem[1]]
            LPathsToVisit = LPathsToVisit | Paths(elem[0],elem[1],elem[2])
    # end first loop

    # begin second loop
    while len(LPathsToVisit)>0:
        NPathsChecked += 1
        (i, j, k) = LPathsToVisit.pop()

        TmpCij = C[elem[0]][elem[1]] & noatomicBAcomp(C[elem[0]][elem[2]],C[elem[2]][elem[1]])
        if (len(TmpCij)==0):
            return (elem, C, NPathsChecked, NChanges)
        if (TmpCij != C[elem[0]][elem[1]]):
            NChanges += 1
            # print C[elem[0]][elem[1]]
            # print TmpCij
            C[elem[0]][elem[1]] = TmpCij
            C[elem[1]][elem[0]] = inverse(TmpCij)
            # print 'union', C[elem[0]][elem[1]]
            LPathsToVisit = LPathsToVisit | Paths(elem[0],elem[1],elem[2])
    # end second loop

    return ((0, 0, 0), C, NPathsChecked, NChanges) #

#
def IsScenario(N):
    for i in range(0,len(compartments)): # go along rows
        for j in range(i+1, len(compartments)): # go along columns
            if (len(N[i][j])!=1):
                return False
    return True

# ctrl+j - insert template
# ctrl+K - commit

def AssignNextRelFirst(TmpN):
    tmp=set()
    for i in range(0,len(compartments)): # go along rows
        for j in range(i+1, len(compartments)): # go along columns
            if (len(TmpN[i][j])>1):
                # удалить некоторый элемент из множества
                tmp.add(copy.copy(TmpN[i][j]).pop())  # кусок быдло-кода
                TmpN[i][j] = tmp
                tmp2 = copy.copy(tmp)
                tt = tmp2.pop()
                tmp2.add((12-tt[0], 12-tt[1]))
                TmpN[j][i] = tmp2
                return TmpN

def AssignNextRelRest(TmpN):
    tmp=set()
    for i in range(0,len(compartments)): # go along rows
        for j in range(i+1, len(compartments)): # go along columns
            if (len(TmpN[i][j])>1):
                # удалить некоторый элемент из множества
                tmp = copy.copy(TmpN[i][j])
                tmp.pop()
                TmpN[i][j] = tmp
                TmpN[j][i] = inverse(tmp)
                return TmpN


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

    ((i, j, k), N, NPathsChecked, NChanges) = PathConsistency(N)

    # begin base cases
    if ((i!=0)|(j!=0)):
        #print 1
        return L # if N is inconsistent, return the empty list
    if IsScenario(N):
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
    TmpN = copy.deepcopy(N)
    TmpN = AssignNextRelFirst(TmpN) #assign next relation
    TmpL = EnumerateScenarios(TmpN) # recursive call
    #print TmpL
    if (len(TmpL)!=0):
        L+=TmpL

    # end recursive case 1

    # begin recursive case 1
    TmpN = copy.deepcopy(N)
    TmpN = AssignNextRelRest(TmpN) #rest of the assignments
    TmpL = EnumerateScenarios(TmpN)  # recursive call
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

def AfterTo(j,k, scen, dim):
    # возвращает -1, если стены совпадают, 1 - если j правее k, и 0 - если j левее k
    if ((j/2 == k/2) & (abs(j - k) == 1)):
        return j%2
    tmp = copy.deepcopy(scen)
    IAatom = tmp[j/2][k/2].pop()[dim] #проверить редактируется ли оригинал scen
    matr = [[[0,0],[0,0]],
            [[0,0],[-1,0]],
            [[0,0],[1,0]],
            [[-1,0],[1,0]],
            [[1,0],[1,0]],
            [[1,0],[1,-1]],
            [[-1,0],[1,-1]],
            [[0, 0], [1, -1]],
            [[0, 0], [1, 1]],
            [[-1, 0], [1, 1]],
            [[1, 0], [1, 1]],
            [[1, -1], [1, 1]],
            [[1,1],[1,1]]]
    return matr[IAatom][j%2][k%2] # остаток от деления на 2 указывает правая ли стена


# функция используется для быстрой оценки наличия пустот
def quickplacement(scen):
    BH=[B,H]
    def quickplacementdim(dim, dmin, dmax, scen):
        matr=np.zeros(((len(compartments)) * 2,(len(compartments)) * 2))
        for i in range(1,len(compartments)*2):
            for j in range(i+1,len(compartments)*2):
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
    p = [0,10]+[0]*(len(compartments)-1)*2 # координаты одной размерности, левая стена i-го помещения, правая стена i-го помещения, i=[0,n]
    # [0,10,0,2,2,10,0,2,2,10]
    # tt=0
    while (not(done)):
        #print p
        done = True
        # tt+=1
        # print tt
        for j in range(2*len(compartments)):
            for k in range(j+1, 2*len(compartments)):
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

# Неточная проверка на наличие пустот
    # вначале проверяем эвристикой, и если она не дает результата, то делаем точную проверку.
    dct = [(6, 9), (6, 10), (7, 6), (7, 7), (7, 8), (7, 9), (8, 6), (8, 7), (8, 8), (8, 9), (9, 6), (9, 7), (9, 8), (9, 9)]
    korner =[2, 0, 2, 1, 0, 1, 0, 0, 0, 0, 2, 1, 0, 1]

    s = 0
    st = set()
    for t in range(1, len(compartments)):
        st = st | (N[0][t])
    for t in range(len(dct)):
        if dct[t] in st:
            s += korner[t]
    if s == 4:
        return withoutgapes2(quickplacement(N))
    else:
        return False

# проверяет содержит ли планировка пустоты
def withoutgapes2(plac_all): #[[0, 10, 0, 1, 1, 2, 3, 10, 2, 3], [0, 10, 0, 10, 0, 10, 0, 10, 0, 10]]
    s=0
    for i in range(1,len(compartments)):
       s+=(plac_all[0][2*i+1] - plac_all[0][2*i])*(plac_all[1][2*i+1] - plac_all[1][2*i])
    if (abs(s-H*B)<10**(-3)):
        return True
    else:
        return False #

def placement_all(dmin, dmax, scen):
    res=[]
    res.append(placement(0, dmin, dmax, scen))
    res.append(placement(1, dmin, dmax, scen))
    return res

def visual(placement_all):
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

# move walls
def movewalls(playsments_a):
    playsments_all=copy.deepcopy(playsments_a)
    dm=[B,H]
    newplas=[]
    for dim in [0,1]:
        ls=[]
        for i in range(len(compartments)*2):
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
        for i in range(len(compartments)*2):
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
    global Ax, Ay, Bx, By, bounds
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
        Ax = np.zeros((len(compartments) - 1, len(xlist)))
        Ay = np.zeros((len(compartments) - 1, len(ylist)))

        # ограничение по взаимному расположению
        Bx = np.zeros((len(xlist) - 2, len(xlist)-1))
        By = np.zeros((len(ylist) - 2, len(ylist)-1))

        for i in range(len(Bx)):
            Bx[i,i] = -1
            Bx[i,i+1] = 1

        for i in range(len(By)):
            By[i,i] = -1
            By[i,i+1] = 1

        for i in range(len(compartments)-1):
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

    #print xys

    x = xy[0:len(Ax[0]) - 1]
    x = np.append(x, B)
    y = xy[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2]
    y = np.append(y, H)

    res1 = Ax.dot(x) * Ay.dot(y) - areaconstr
    res2 = Bx.dot(xy[0:len(Ax[0])-1]) - np.sign(Bx.dot(xy[0:len(Ax[0])-1]))*min_margin
    res3 = By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]) - np.sign(By.dot(xy[len(Ax[0])-1:len(Ax[0]) + len(Ay[0])-2]))*min_margin
    # ограничение на соотношение сторон
    res4 = map(lambda d: int((d>=1./3)&(d<=3))-1, Ay.dot(y)/Ax.dot(x))*np.array(sides_ratio)

    res1sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res1))
    res2sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res2))
    res3sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res3))
    res4sign = np.array(map(lambda x: np.sign(x)*(np.sign(x)-1)/2, res4))

    return res1sign.dot(rooms_weights) + sum(res2sign)*5 + sum(res3sign)*5 + sum(res4sign)*1


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
        #print i
        plac_new[0][i]=xlistnew[xlist.index(placemnt[0][i])]

    ylist = list(set(placemnt[1]))
    ylist.sort()
    ylistnew = [0] + ylistnew + [H]
    # ylist.remove(0)
    for i in range(len(placemnt[1])):
        plac_new[1][i] = ylistnew[ylist.index(placemnt[1][i])]

    return plac_new

# Поиск различных вариантов компоновки (топологий)
def main_topology(max_results, compartments_list):
    global max_res, compartments, recur_int, nres, stop, rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col
    max_res = max_results

    # подготовка списков и таблиц с ограничениями
    changing_lists = [rooms_weights, areaconstr, areaconstr_opt, sides_ratio, comp_col]
    new_lists = [[],[],[],[],[]]
    for i in range(len(compartments[1:])):
        if (compartments[1:][i] in set(compartments_list)):
            for j in range(len(changing_lists)):
                new_lists[j].append(changing_lists[j][i])

    rooms_weights = new_lists[0]
    areaconstr = new_lists[1]
    areaconstr_opt = new_lists[2]
    sides_ratio = new_lists[3]
    comp_col = new_lists[4]

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
    prepare_tc(tc_src)

    # topology
    t1 = time.clock()
    N = copy.deepcopy(tc)
    recur_int = 0
    nres = 0
    stop = False
    scens = EnumerateScenarios(N)
    t2 = time.clock()
    print "Найдено " + str(len(scens)) + " вариантов размещения комнат" + '\n' + "Время выполнения программы sec.- " + str(t2-t1)

    return scens

# Учет ограничений по площади/длине
def main_size(height, width, scens):
    global B, H, res_x
    B = width
    H = height
    t1 = time.clock()
    optim_scens=[]
    res_x=[]
    for i in range(len(scens)):
        makeconst(quickplacement(scens[i]))
        res = opt.differential_evolution(func2_discret, bounds)
        xlistnew = list(res.x[0:len(Ax[0]) - 1])
        ylistnew = list(res.x[len(Ax[0]) - 1:len(Ax[0]) + len(Ay[0]) - 2])
        #print i
        optim_scens.append(optim_placement(quickplacement(scens[i]), xlistnew, ylistnew))
        res_x.append(res.fun)
    t2 = time.clock()
    print "Расчет размеров комнат закончен! Время выполнения программы sec.- " + str(t2 - t1)

    return optim_scens



# Поиск топологий
# Параметры - количество результатов, список комнат
scens = main_topology(5, ["envelope",  "hall", "room", "bath", "kitchen"])

# Визуализация
i=0
for pl in scens:
    if i%9==0:
        fig1 = plt.figure(figsize=(15, 15))
    ax1 = fig1.add_subplot(3,3,i%9+1, title='scen '+str(i)+ " " + str(res_x[i]), aspect='equal')
    visual(quickplacement(pl))
    i+=1
    if (i>30):
        break

# Учет ограничений по площади
# Параметры - ширина, высота, сценарии (топологические)
optim_scens = main_size(7, 8, scens)
# Визуализация
i=0
n=2
for pl in optim_scens:
    if i%n**2==0:
        fig1 = plt.figure(figsize=(15, 15))
    ax1 = fig1.add_subplot(n,n,i%n**2+1, title='scen '+str(i)+ " " + str(res_x[i]), aspect='equal')
    visual(pl)
    i+=1
    if (i>30):
        break

