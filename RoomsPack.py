import itertools
import numpy as np
import time
import copy

timeout = 15
depth_recurs = 500
recur_int = 0

# atomic relations block algebra
ARelBA = [[(y, x) for x in range(13)] for y in range(13)]

# комнаты
compartments = {"envelope", "hall", "room", "bath", "kitchen"}



# Ограничения
# смежные
adjacency = {ARelBA[2][1],ARelBA[3][1],ARelBA[4][1],ARelBA[5][1],ARelBA[6][1],ARelBA[7][1],ARelBA[8][1],ARelBA[9][1],ARelBA[10][1], \
             ARelBA[1][2], ARelBA[1][3], ARelBA[1][4], ARelBA[1][5], ARelBA[1][6], ARelBA[1][7], ARelBA[1][8], ARelBA[1][9], ARelBA[1][10],\
            ARelBA[2][11],ARelBA[3][11],ARelBA[4][11],ARelBA[5][11],ARelBA[6][11],ARelBA[7][11],ARelBA[8][11],ARelBA[9][11],ARelBA[10][11], \
             ARelBA[11][2], ARelBA[11][3], ARelBA[11][4], ARelBA[11][5], ARelBA[11][6], ARelBA[11][7], ARelBA[11][8], ARelBA[11][9], ARelBA[11][10]}
inclusion = {ARelBA[4][4]}
envel_other = {(9,6),(9,7),(9,8),(9,9),(7,6),(7,7),(7,8),(7,9),(8,6),(8,7),(8,8),(8,9),(6,9),(6,10),(2,6)}

# topologic constraints
tc_src=[[set(), envel_other, envel_other, envel_other, envel_other],
    [set(),set(), adjacency, adjacency, adjacency],
    [set(),set(), set(), adjacency, adjacency],
    [set(), set(), set(), set(), adjacency],
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

inverse({(1,2),(3,4),(0,12)})

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

Paths(3,2,0)

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
                tmp.add(copy.copy(TmpN[i][j]).pop())
                TmpN[i][j] = tmp
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
                return TmpN



def EnumerateScenarios(N):
    global recur_int
    recur_int+=1

    # input - matrix of constraints
    L = []
    ((i, j, k), N, NPathsChecked, NChanges) = PathConsistency(N)

    # begin base cases
    if ((i!=0)|(j!=0)):
        print 1
        return L # if N is inconsistent, return the empty list
    if IsScenario(N):
        L.append(N)
        print 2
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
    L.append(TmpL)
    # end recursive case 1

    # begin recursive case 1
    TmpN = copy.deepcopy(N)
    TmpN = AssignNextRelRest(TmpN) #rest of the assignments
    TmpL = EnumerateScenarios(TmpN)  # recursive call
    L.append(TmpL)
    # end recursive case 2
    print 3
    return L

# проверка на рабочем примере
N = copy.deepcopy(tc)
recur_int = 0
EnumerateScenarios(N)

IsScenario(tc_tmp)



tt=EnumerateScenarios(N)


# WORKING TEST EXAMPLE

# scenario pic1
tc_tmp=[[{(6,6)}, {(9,9)}, {(7,6)}, {(8,9)}, {(9,7)}],
    [{(3,3)}, {(6,6)}, {(0,3)}, {(1,6)}, {(3,1)}],
    [{(5,6)}, {(12,9)}, {(6,6)}, {(11,9)}, {(11,7)}],
    [{(4,3)}, {(11,6)}, {(1,3)}, {(6,6)}, {(5,1)}],
    [{(3,5)}, {(9,11)}, {(1,5)}, {(7,11)}, {(6,6)}]]

# scenario pic2
tc_tmp=[[{(6,6)}, {(9,9)}, {(7,7)}, {(7,9)}, {(9,7)}],
    [{(3,3)}, {(6,6)}, {(0,1)}, {(1,6)}, {(3,1)}],
    [{(5,5)}, {(12,11)}, {(6,6)}, {(5,11)}, {(11,6)}],
    [{(5,3)}, {(11,6)}, {(7,1)}, {(6,6)}, {(10,1)}],
    [{(3,5)}, {(9,11)}, {(1,6)}, {(2,11)}, {(6,6)}]]

# scenario with noise
tc_tmp=[[{(6,6)}, {(9,9),(7,7)}, {(7,6),(3,3)}, {(8,9),(12,12)}, {(9,7)}],
    [{(3,3)}, {(6,6)}, {(0,3)}, {(1,5)}, {(3,1)}],
    [{(5,5)}, {(12,9), (12,12)}, {(6,6)}, {(11,9),(3,3)}, {(11,7),(5,6)}],
    [{(4,3),(5,6),(12,12)}, {(11,6)}, {(1,3),(5,6)}, {(6,6)}, {(5,1)}],
    [{(3,5)}, {(9,11),(1,6)}, {(1,5)}, {(7,11),(5,6)}, {(6,6),(12,12)}]]

PathConsistency(tc_tmp)
tt=EnumerateScenarios(N)