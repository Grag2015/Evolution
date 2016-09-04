import itertools
import numpy as np
import time
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

timeout = 15
depth_recurs = 2000
recur_int = 0



# atomic relations block algebra
ARelBA = [[(y, x) for x in range(13)] for y in range(13)]

# комнаты
compartments = ["envelope", "hall", "room", "bath", "kitchen"]
comp_col = {0: '#F0CCAD',
           1: '#ECA7A7',
           2: '#73DD9B',
           3: '#ACBFEC',
           4: '#EAE234'
           }


# Ограничения
# смежные
adjacency = {ARelBA[0][11], ARelBA[0][1], ARelBA[1][1], ARelBA[2][1],ARelBA[3][1], ARelBA[4][1],ARelBA[5][1],ARelBA[6][1],ARelBA[6][11],ARelBA[7][1],ARelBA[8][1],ARelBA[9][1],ARelBA[10][1],ARelBA[11][1], \
        ARelBA[1][2], ARelBA[1][3], ARelBA[1][4], ARelBA[1][5], ARelBA[1][6], ARelBA[1][7], ARelBA[1][8], ARelBA[1][9], ARelBA[1][10], ARelBA[11][6], ARelBA[0][6],
             ARelBA[3][0], ARelBA[5][0], ARelBA[7][0], ARelBA[9][0], ARelBA[0][3], ARelBA[0][5], ARelBA[0][7], ARelBA[0][9]}

inclusion = {ARelBA[4][4]}
envel_hall = {(9,6),(9,7),(9,8),(9,9),(7,6),(7,7),(7,8),(7,9),(8,6),(8,7),(8,9),(6,9),(6,10),(2,6)}
envel_room = {(9,6),(9,7),(9,9),(7,6),(7,7),(7,9),(8,6),(6,9),(6,10), (6,7),(6,3)}
bath_kitchen = {(1,3),(1,5),(1,6),(1,7),(1,9),(3,1),(5,1),(6,1),(7,1),(9,1)}
# topologic constraints
tc_src=[[set(), envel_hall, envel_room, envel_room, envel_room],
    [set(),set(), adjacency, adjacency, adjacency],
    [set(),set(), set(), adjacency, adjacency],
    [set(), set(), set(), set(), bath_kitchen],
    [set(), set(), set(), set(), set()]]

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


tc = prepare_tc(tc_src)

def atomicIAcomp(IArel1, IArel2):
    # interval algebra composition matrix
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


def cartesProduct(set1, set2):
    cp=set()
    for i in set1:
        for j in set2:
            cp.add((i,j))
    return cp

def atomicBAcomp(atomicBArel1, atomicBArel2):
    return cartesProduct(atomicIAcomp(atomicBArel1[0],atomicBArel2[0]),atomicIAcomp(atomicBArel1[1],atomicBArel2[1]))

def noatomicBAcomp(noatomicBArel1, noatomicBArel2):
    res=set()
    for i in noatomicBArel1:
        for j in noatomicBArel2:
            res= res | atomicBAcomp(i,j)
    return res

def inverse(noatomicBArel):
    res=set()
    for elem in noatomicBArel:
        res.add((12-elem[0],12-elem[1]))
    return res

def Paths(i,j,k):
    # ищем пути из i в j xthtp 3-ю точку, но не k
    ls = range(len(compartments))
    ls.remove(k)
    ls.remove(i)
    ls.remove(j)
    res=set()
    for elem in ls:
        res.add((i,j,elem))
    return res

def PathConsistency(C): # проход не вычищает все несовместимые элементы, ф-ю надо запускать раза 3.
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


envel_other = {(9,6),(9,7),(9,8),(9,9),(7,6),(7,7),(7,8),(7,9),(8,6),(8,7),(8,8),(8,9),(6,9),(6,10),(2,6)}
hall_room={(1,2), (11,10), (1,10), (11,2)}
kitchen_bath={(11,0), (1,12)}
tc_test=[[{}, envel_other, envel_other, envel_other, envel_other],
    [{},{}, hall_room, {(1,3),(1,5),(1,7),(1,9),(11,3),(11,5),(11,7),(11,9)}, {(6,1),(11,6)}],
    [{},{}, {}, {(6,1),(11,6)}, {(1,3),(1,5),(1,7),(1,9),(11,3),(11,5),(11,7),(11,9)}],
    [{}, {}, {}, {}, kitchen_bath],
    [{}, {}, {}, {}, {}]] # - удалить первый столбец


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



def EnumerateScenarios(N):
    global recur_int
    recur_int+=1

    # input - matrix of constraints
    L = []
    ((i, j, k), N, NPathsChecked, NChanges) = PathConsistency(N)

    # begin base cases
    if ((i!=0)|(j!=0)):
        #print 1
        return L # if N is inconsistent, return the empty list
    if IsScenario(N):
        L.append(N)
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


# WORKING TEST EXAMPLE

# scenario pic1
tc_tmp1=[[{(6,6)}, {(9,9)}, {(7,6)}, {(8,9)}, {(9,7)}],
    [{(3,3)}, {(6,6)}, {(0,3)}, {(1,6)}, {(3,1)}],
    [{(5,6)}, {(12,9)}, {(6,6)}, {(11,9)}, {(11,7)}],
    [{(4,3)}, {(11,6)}, {(1,3)}, {(6,6)}, {(5,1)}],
    [{(3,5)}, {(9,11)}, {(1,5)}, {(7,11)}, {(6,6)}]]

# scenario pic2
tc_tmp2=[[{(6,6)}, {(9,9)}, {(7,7)}, {(7,9)}, {(9,7)}],
    [{(3,3)}, {(6,6)}, {(0,1)}, {(1,6)}, {(3,1)}],
    [{(5,5)}, {(12,11)}, {(6,6)}, {(5,11)}, {(11,6)}],
    [{(5,3)}, {(11,6)}, {(7,1)}, {(6,6)}, {(10,1)}],
    [{(3,5)}, {(9,11)}, {(1,6)}, {(2,11)}, {(6,6)}]]

# объединенный сценарий из 2-х рабочих - алгоритму удалось их разделить
tc_tmp3 = copy.deepcopy(tc_tmp1)
for i in range(5):
    for j in range(5):
        tc_tmp3[i][j].add(tc_tmp2[i][j].pop())

PathConsistency(tc_tmp3)

# scenario with noise
tc_tmp=[[{(6,6)}, {(9,9),(3,3)}, {(7,6),(3,3)}, {(8,9),(12,12)}, {(9,7)}],
   [{(3,3)}, {(6,6)}, {(0,3)}, {(1,6)}, {(3,1)}],
    [{(5,6)}, {(12,9), (12,12)}, {(6,6)}, {(11,9),(3,3)}, {(11,7),(5,6)}],
    [{(4,3),(5,6),(12,12)}, {(11,6)}, {(1,3),(5,6)}, {(6,6)}, {(5,1)}],
    [{(3,5)}, {(9,11),(5,6)}, {(1,5)}, {(7,11),(5,6)}, {(6,6),(12,12)}]]

tt=PathConsistency(tc_tmp)
tt2=PathConsistency(tt[1])

N = copy.deepcopy(tc_tmp3)
EnumerateScenarios(N)

N = copy.deepcopy(tc_tmp3)
AssignNextRelRest(N)

tt=[[{(6, 6)}, {(9, 8)}, {(7, 8)}, {(8, 7)}, {(7, 8)}],
  [{(3, 4)}, {(6, 6)}, {(1, 6)}, {(7, 1)}, {(1, 1)}],
  [{(5, 4)}, {(11, 6)}, {(6, 6)}, {(11, 1)}, {(6, 1)}],
  [{(4, 5)}, {(5, 11)}, {(1, 11)}, {(6, 6)}, {(1, 9)}],
  [{(5, 4)}, {(11, 11)}, {(6, 11)}, {(11, 3)}, {(6, 6)}]]

AfterTo(0,5, tt, 0)

PathConsistency(tt)

B=10
H=10

def dmin(i, j, scen, dim):
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

    dminm = [[0,B,0,1,0,1,0,1,0,1],
            [B,0,1,0,1,0,1,0,1,0],
            [0,1,0,1,0,0,0,0,0,0],
            [1,0,1,0,0,0,0,0,0,0],
            [0,1,0,0,0,1,0,0,0,0],
            [1,0,0,0,1,0,0,0,0,0],
            [0,1,0,0,0,0,0,1,0,0],
            [1,0,0,0,0,0,1,0,0,0],
            [0,1,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,0]]
    return dminm[i][j]

dmin(0, 2, scen, 0)

dmax = [[0, B, B - 1, B, B - 1, B, B - 1, B, B - 1, B],
        [B, 0, B, B - 1, B, B - 1, B, B - 1, B, B - 1],
        [B - 1, B, 0, B, B - 1, B, B - 1, B, B - 1, B],
        [B, B - 1, B, 0, B, B-1, B, B-1, B, B-1],
        [B - 1, B, B - 1, B, 0, B, B - 1, B, B - 1, B],
        [B, B - 1, B, B - 1, B, 0, B, B - 1, B, B - 1],
        [B - 1, B, B - 1, B, B - 1, B, 0, B, B - 1, B],
        [B, B - 1, B, B - 1, B, B - 1, B, 0, B, B - 1],
        [B - 1, B, B - 1, B, B - 1, B, B - 1, B, 0, B],
        [B, B - 1, B, B - 1, B, B - 1, B, B - 1, B, 0]]

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
                            if (p[k] < p[j] - dmax[j][k]):
                                done = False
                                #print j, k, 5
                                p[k] = p[j] - dmax[j][k]
                # print j, k
                # print p
        #done = True
    return p

def withoutgapes(plac_all): #[[0, 10, 0, 1, 1, 2, 3, 10, 2, 3], [0, 10, 0, 10, 0, 10, 0, 10, 0, 10]]
    s=0
    for i in range(1,len(compartments)):
       s+=(plac_all[0][2*i+1] - plac_all[0][2*i])*(plac_all[1][2*i+1] - plac_all[1][2*i])
    if (s==H*B):
        return True
    else:
        return False

def placement_all(dmin, dmax, scen):
    res=[]
    res.append(placement(0, dmin, dmax, scen))
    res.append(placement(1, dmin, dmax, scen))
    return res

scen=[[{(6, 6)}, {(8, 9)}, {(7, 9)}, {(9, 7)}, {(7, 7)}],
   [{(4, 3)}, {(6, 6)}, {(1, 6)}, {(5, 1)}, {(1, 1)}],
   [{(5, 3)}, {(11, 6)}, {(6, 6)}, {(11, 1)}, {(6, 1)}],
   [{(3, 5)}, {(7, 11)}, {(1, 11)}, {(6, 6)}, {(1, 6)}],
   [{(5, 5)}, {(11, 11)}, {(6, 11)}, {(11, 6)}, {(6, 6)}]]

placement(1, dmin, dmax, scen)

pl_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 1, 9, 0, 9, 9, 10, 9, 10]]
# pl_all = [[0, 10, 0, 3, 3, 6, 6, 10, 0, 3, 3, 6, 6, 10], [0, 10, 0, 6, 0, 3, 0, 6, 6, 10, 3, 10, 6, 10]]
def visual(placement_all):
    # placement_all = [[0, 10, 0, 1, 1, 10, 0, 1, 1, 10], [0, 10, 0, 1, 1, 10, 0, 1, 1, 10]]
    # fig1 = plt.figure(figsize=(10,10) )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    # ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(1, len(placement_all[0])/2): # объединяющий прямоугольник не отрисовываем
        ax1.add_patch(mpatches.Rectangle((placement_all[0][2*i]/float(B), placement_all[1][2*i]/float(H)),   # (x,y)
                                         abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B),          # width
                                         abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H), alpha=0.6, label='test '+str(i),
                                         facecolor=comp_col[i]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i])
    # plt.show()




placement_all(dmin, dmax, scen)

visual(placement_all(dmin, dmax, scens[16]))

# проверка на рабочем примере
N = copy.deepcopy(tc)
recur_int = 0
scens=EnumerateScenarios(N)
len(scens)

# получить все плэйсменты и проверить gape
wogapes_playsments=[]
wogapes_scens=[]
all_playsments=[]
i=0
for scen in scens:
    pl=placement_all(dmin, dmax, scen)
    all_playsments.append(pl)
    if (withoutgapes(pl)):
        wogapes_playsments.append(pl)
        wogapes_scens.append(i)
    i+=1
print "Yes"

# move walls
def movewalls(playsments_all):
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
        print ls2
        newplasit=playsments_all[dim]
        for i in range(len(compartments)*2):
            if ((playsments_all[dim][i]!=0) & (playsments_all[dim][i]!= dm[dim])):
                newplasit[i]=l*(ls2.index(playsments_all[dim][i])+1)
        newplas.append(newplasit)
    return newplas

movewalls(wogapes_playsments[0])

len(wogapes_playsments)

# отображение всех решений:
i=0
for pl in wogapes_playsments:
    if i%9==0:
        fig1 = plt.figure(figsize=(15, 15))
    ax1 = fig1.add_subplot(3,3,i%9+1, title='scen '+str(i), aspect='equal')
    visual(movewalls(pl))
    i+=1
    if (i>30):
        break
plt.show()


# за счет добавления симметричных элементов в одной ячейки матрицы ограничений. у нас возникло много "зеркальных" и "поворотных" вариантов.
# но при этом так и не удалось получить сценарий с холллом в центре


scen=[[{(6, 6)}, {(8, 9)}, {(9, 9)}, {(7, 9)}, {(6, 3)}],
   [{(4, 3)}, {(6, 6)}, {(11, 6)}, {(1, 6)}, {(4, 1)}],
   [{(5, 3)}, {(11, 6)}, {(6, 6)}, {(11, 1)}, {(6, 1)}],
   [{(3, 5)}, {(7, 11)}, {(1, 11)}, {(6, 6)}, {(1, 6)}],
   [{(5, 5)}, {(11, 11)}, {(6, 11)}, {(11, 6)}, {(6, 6)}]]


# 1. c