import itertools
import numpy as np
import time

# atomic relations block algebra
ARelBA = [[(y, x) for x in range(13)] for y in range(13)]

# комнаты
compartments = {"envelope", "hall", "room", "bath", "kitchen"}

timeout = 15

# Ограничения
# смежные
adjacency = {ARelBA[2][1],ARelBA[3][1],ARelBA[4][1],ARelBA[5][1],ARelBA[6][1],ARelBA[7][1],ARelBA[8][1],ARelBA[9][1],ARelBA[10][1], \
             ARelBA[1][2], ARelBA[1][3], ARelBA[1][4], ARelBA[1][5], ARelBA[1][6], ARelBA[1][7], ARelBA[1][8], ARelBA[1][9], ARelBA[1][10],\
            ARelBA[2][11],ARelBA[3][11],ARelBA[4][11],ARelBA[5][11],ARelBA[6][11],ARelBA[7][11],ARelBA[8][11],ARelBA[9][11],ARelBA[10][11], \
             ARelBA[11][2], ARelBA[11][3], ARelBA[11][4], ARelBA[11][5], ARelBA[11][6], ARelBA[11][7], ARelBA[11][8], ARelBA[11][9], ARelBA[11][10]}
inclusion = {ARelBA[4][4]}

# topologic constraints
tc=[[{}, adjacency, adjacency, adjacency, inclusion],
    [{},{}, adjacency, adjacency, inclusion],
    [{},{}, {}, adjacency, inclusion],
    [{}, {}, {}, {}, adjacency],
    [{}, {}, {}, {}, {}]] # - удалить первый столбец

def atomicIAcomp(IArel1, IArel2):
    # interval algebra composition matrix
    IAcomp=[[{0},{0},{0},{0},{0,1,2,3,4},{0,1,2,3,4},{0},{0},{0},{0},{0,1,2,3,4},{0,1,2,3,4},{0,1,2,3,4,5,6,7,8,9,10,11,12}],
            [{0},{0},{0},{1},{2,3,4},{2,3,4},{1},{0},{0},{1},{0,1,2,3,4},{5,6,7},{8,9,10,11,12}],
            [{0},{0},{0,1,2},{0},{2,3,4},{2,3,4},{2},{0,1,2},{0,1,2,7,8},{2,7,8},{2,3,4,5,6,7,8,9,10},{8,9,10},{8,9,10,11,12}],
            [{0},{0},{0,1,2},{3},{4},{4},{3},{0,1,2},{0,1,2,7,8},{3,6,9},{4,5,10},{11},{12}],
            [{0},{0},{0,1,2,3,4},{4},{4},{4},{4},{0,1,2,3,4},{0,1,2,3,4,5,6,7,8,9,10,11,12},{4,5,10,11,12},{4,5,10,11,12},{12},{12}],
            [{0},{5},{2,3,4},{4},{4},{5},{5},{5,6,7},{8,9,10,11,12},{10,11,12},{10,11,12},{12},{12}],
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

def Paths(i,j,k):
    # ищем пути из i в j xthtp 3-ю точку, но не k
    ls = range(len(compartments))
    ls.remove(k)
    restm = set(itertools.combinations(ls, 3))
    res=set()
    for elem in restm:
        if (i in elem) & (j in elem):
            res.add(elem)
    return res


def PathConsistency(C):
    LPathsToVisit = set()
    NPathsChecked = 0
    NChanges = 0

    # begin first loop
    samples_3 = set(itertools.combinations(range(len(compartments)),3))
    for elem in samples_3:
        NPathsChecked+=1
        if (elem in LPathsToVisit):
            LPathsToVisit.remove(elem)
        TmpCij = C[elem[0]][elem[1]] & noatomicBAcomp(C[elem[0]][elem[2]],C[elem[1]][elem[2]]) # intersection в оригинале C[elem[2]][elem[1]]
        if (len(TmpCij)==0):
            print C[elem[0]][elem[1]]
            print noatomicBAcomp(C[elem[0]][elem[2]],C[elem[1]][elem[2]])
            return (elem, C, NPathsChecked, NChanges)
        if (TmpCij != C[elem[0]][elem[1]]):
            NChanges += 1
            C[elem[0]][elem[1]] = TmpCij
            LPathsToVisit = LPathsToVisit | Paths(elem[0],elem[1],elem[2])
    # end first loop

    # begin second loop
    while len(LPathsToVisit)>0:
        NPathsChecked += 1
        (i, j, k) = LPathsToVisit.pop()

        TmpCij = C[elem[0]][elem[1]] & noatomicBAcomp(C[elem[0]][elem[2]],C[elem[1]][elem[2]]) # intersection в оригинале C[elem[2]][elem[1]]
        if (len(TmpCij)==0):
            return (elem, C, NPathsChecked, NChanges)
        if (TmpCij != C[elem[0]][elem[1]]):
            NChanges += 1
            C[elem[0]][elem[1]] = TmpCij
            LPathsToVisit = LPathsToVisit | Paths(elem[0],elem[1],elem[2])
    # end second loop

    return ((0, 0, 0), C, NPathsChecked, NChanges)


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


def EnumerateScenarios(N):
    t1 = time.clock()
    # input - matrix of constraints
    L = []
    ((i, j, k), N, NPathsChecked, NChanges) = PathConsistency(N)

    # begin base cases
    if ((i!=0)|(j!=0)):
        return L # if N is inconsistent, return the empty list
    if IsScenario(N):
        L.append(N)
        return L # if N is a scenario, return a list only with N
    # end base cases

    # begin recursive case 1
    TmpN = N
    #TmpN = AssignNextRelFirst(TmpN) #assign next relation
    TmpL = EnumerateScenarios(TmpN) # recursive call
    L.append(TmpL)
    # end recursive case 1

    t2 = time.clock()
    if ((t2-t1) > timeout):
        print "timeout"
        return L

    # begin recursive case 1
    TmpN = N
    # TmpN = AssignNextRelRest(TmpN) #rest of the assignments
    TmpL = EnumerateScenarios(TmpN)  # recursive call
    L.append(TmpL)
    # end recursive case 2

    return L

