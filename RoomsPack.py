import itertools
import numpy as np
import time
import copy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# настройки алгоритма
timeout = 15
depth_recurs = 5000
recur_int = 0
B=10
H=10
max_res = 10 #максимальное количество результатов, важно ограничивать для скорости работы


# atomic relations block algebra
ARelBA = [[(y, x) for x in range(13)] for y in range(13)]

# комнаты
compartments = ["envelope",  "hall", "corr", "room", "bath", "kitchen"]
areaconstr = [1,1,14,3.6,9] # без оболочки
comp_col = {0: '#F0CCAD',
            1: '#ECA7A7',
            2: '#73DD9B',
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
tc_src=[[set(), envel_hall, envel_corr, envel_room, envel_room, envel_room],
    [set(),set(), hall_corr , adjacency , adjacency , adjacency],
    [set(),set(), set(), corr_other, corr_other, corr_other],
    [set(), set(), set(), set(), adjacency, adjacency],
    [set(), set(), set(), set(), set(), bath_kitchen],
    [set(), set(), set(), set(), set(), set()]]

# envel_hall | envel_corr | envel_room

dct = [(6, 9), (6, 10), (7, 6), (7, 7), (7, 8), (7, 9), (8, 6), (8, 7), (8, 8), (8, 9), (9, 6), (9, 7), (9, 8), (9, 9)]
korner =[2, 0, 2, 1, 0, 1, 0, 0, 0, 0, 2, 1, 0, 1]

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
        s=0
        st=set()
        for t in range(1,len(compartments)):
           st = st | (N[0][t])

        for t in range(len(dct)):
            if dct[t] in st:
                s += korner[t]

        if s==4:
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

    dminm = [[0,B,0,1,0,1,0,1,0,1,0,1],
            [B,0,1,0,1,0,1,0,1,0,1,0],
            [0,1,0,1,0,0,0,0,0,0,0,0],
            [1,0,1,0,0,0,0,0,0,0,0,0],
            [0,1,0,0,0,1,0,0,0,0,0,0],
            [1,0,0,0,1,0,0,0,0,0,0,0],
            [0,1,0,0,0,0,0,1,0,0,0,0],
            [1,0,0,0,0,0,1,0,0,0,0,0],
            [0,1,0,0,0,0,0,0,0,1,0,0],
            [1,0,0,0,0,0,0,0,1,0,0,0],
            [0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0]]
    return dminm[i][j]


dmax = [[0, B, B - 1, B, B - 1, B, B - 1, B, B - 1, B, B-1, B],
        [B, 0, B, B - 1, B, B - 1, B, B - 1, B, B - 1, B, B-1],
        [B - 1, B, 0, B, B - 1, B, B - 1, B, B - 1, B, B-1, B],
        [B, B - 1, B, 0, B, B-1, B, B-1, B, B-1, B, B-1],
        [B - 1, B, B - 1, B, 0, B, B - 1, B, B - 1, B, B-1 , B],
        [B, B - 1, B, B - 1, B, 0, B, B - 1, B, B - 1, B, B-1],
        [B - 1, B, B - 1, B, B - 1, B, 0, B, B - 1, B, B-1, B],
        [B, B - 1, B, B - 1, B, B - 1, B, 0, B, B - 1, B, B-1],
        [B - 1, B, B - 1, B, B - 1, B, B - 1, B, 0, B, B-1, B],
        [B, B - 1, B, B - 1, B, B - 1, B, B - 1, B, 0, B, B-1],
        [B - 1, B, B - 1, B, B - 1, B, B - 1, B, B-1, B, 0, B],
        [B, B - 1, B, B - 1, B, B - 1, B, B - 1, B, B-1, B, 0]]

# TODO реализовать этот метод
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
                            #print j, k, 5
                            if (p[k] < p[j] - dmax[j][k]):
                                done = False
                                #print j, k, 5
                                p[k] = p[j] - dmax[j][k]
                # print j, k
                # print p
        #done = True
    return p

# проверяет содержит ли планировка пустоты
def withoutgapes(plac_all): #[[0, 10, 0, 1, 1, 2, 3, 10, 2, 3], [0, 10, 0, 10, 0, 10, 0, 10, 0, 10]]
    s=0
    for i in range(1,len(compartments)):
       s+=(plac_all[0][2*i+1] - plac_all[0][2*i])*(plac_all[1][2*i+1] - plac_all[1][2*i])
    if (s==H*B):
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
                                         facecolor=comp_col[i]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i])
    # plt.show()




# проверка на рабочем примере
# Расчет времени выполнения - import time
t1=time.clock()

N = copy.deepcopy(tc)
recur_int = 0
nres = 0
stop = False
scens=EnumerateScenarios(N)
print "Yes"
len(scens)

t2=time.clock()
t2-t1

# получить все плэйсменты и проверить gape
wogapes_playsments=[]
wogapes_scens=[]
all_playsments=[]
i=0
t1=time.clock()
for scen in scens:
    # print i
    pl=placement_all(dmin, dmax, scen)
    all_playsments.append(pl)
    if (withoutgapes(pl)):
        wogapes_playsments.append(pl)
        wogapes_scens.append(i)
    i+=1
print "Yes"
t2=time.clock()
t2-t1

len(wogapes_scens)

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


# отображение всех решений без пропусков:
i=0
for pl in wogapes_playsments:
    if i%9==0:
        fig1 = plt.figure(figsize=(15, 15))
    ax1 = fig1.add_subplot(3,3,i%9+1, title='scen '+str(i), aspect='equal')
    visual(movewalls(pl))
    i+=1
    if (i>30):
        break

# отображение всех решений:
i=0
for pl in all_playsments:
    if i%9==0:
        fig1 = plt.figure(figsize=(15, 15))
    ax1 = fig1.add_subplot(3,3,i%9+1, title='scen '+str(i), aspect='equal')
    visual(pl)
    i+=1
    if (i>30):
        break

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
                                         facecolor=comp_col[i]
            )
        )
        ax1.text(placement_all[0][2*i]/float(B)+(abs(placement_all[0][2*i] - placement_all[0][2*i+1])/float(B))/2.,
                 placement_all[1][2 * i] / float(H) + (abs(placement_all[1][2*i] - placement_all[1][2*i + 1])/float(H))/2., compartments[i])
    # plt.show()

visual_pl(placement_all(dmin, dmax,sc2))

sc2=copy.deepcopy(scens[10])
for i in range(6):
    for j in range(6):
        if (not(sc2[i][j].pop() in tc[i][j])):
            print i,j




sc2[0][0].pop in tc[0][0]

scen

s = 0
st = set()
for t in range(1, len(compartments)):
    st = st | (scen[0][t])

for t in range(len(dct)):
    if dct[i] in st:
        s += korner[t]


# Решение уравнение

import scipy.optimize.fsolve as fsol
import scipy.optimize as opt

def equations(p):
    y,z,t = p
    f1 = -10*z*t + 4*y*z*t - 5*y*t + 4*t*(z**2) - 7
    f2 = 2*y*z*t + 5*y*t - 3
    f3 = - 10*t + 2*y*t + 4*z*t - 1
    return (f1,f2,f3)


y,z,t = opt.fsolve(equations, x0, maxfev =10000)
print equations((y,z,t))

x0=np.array([0, 0, 0])
type(x0)

def func(p):
    y,z,t = p

    f1 = -10*z*t + 4*y*z*t - 5*y*t + 4*t*(z**2)# - 7
    f2 = 2*y*z*t + 5*y*t# - 3
    f3 = - 10*t + 2*y*t + 4*z*t #- 1
    return np.sqrt(f1**2 + f2**2 + f3**2)

bounds = [(0,2), (0, 2), (0, 2)]
res=opt.differential_evolution(func, bounds)
func(res.x)

minroom =50
minkitch = 40
minhall = 5
minbath = 5

def func(p):
    x,y,z,s1,s2,s3,s4,s5 = p
    f1 = x-z-s1
    f2 = y*z-s2-minroom
    f3 = y*(B-x)-s3-minkitch
    f4 = z*(H-y)-s4-minhall
    f5 = (B-z)*(H-y)-s5-minbath

    return np.sqrt(f1**2 + f2**2 + f3**2 + f4**2 + f5**2)

bounds = [(1,B), (0, H), (0, B), (0,100), (0,100), (0,100), (0, 100), (0, 100)]
res=opt.differential_evolution(func, bounds)

func(res.x)

# placement example
placemnt = [[0, 10, 0, 10, 1, 2, 0, 1, 0, 2, 2, 10], [0, 10, 0, 1, 1, 4, 2, 3, 4, 10, 3, 10]]
def makematr(placemnt):

    global Ax, Ay, Bx, By, bounds

    xlist = list(set(placemnt[0]))
    xlist.sort()
    xlist.remove(0)
    xlist.remove(B)

    ylist = list(set(placemnt[1]))
    ylist.sort()
    ylist.remove(0)
    ylist.remove(H)

    # ограничение по площади
    Ax = np.zeros((len(compartments) - 1, len(xlist)))
    Ay = np.zeros((len(compartments) - 1, len(ylist)))

    # ограничение по взаимному расположению
    Bx = np.zeros((len(xlist) - 1, len(xlist)))
    By = np.zeros((len(ylist) - 1, len(ylist)))

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
            if (placemnt[0][2*i]==ylist[yl]):
                Ay[i,yl] = -1
                Ay[i,ylist.index(placemnt[0][2*i+1])] = 1
            # если стенка правая
            if (placemnt[0][2*i+1]==ylist[yl]):
                Ay[i, yl] = 1
                if (placemnt[0][2 * i] != 0):
                    Ay[i, ylist.index(placemnt[0][2 * i])] = -1
    bounds = []
    matrlist =  [Ax[0], Ay[0], Ax, Bx, By]
    boundslist = [(0, B), (0, H), (0,100), (0,100), (0,100)]
    for matr in range(len(matrlist)):
        for i in range(len(matrlist[matr])):
            bounds.append(boundslist[matr])
    return True

x=[0,0,0]
y=[0,0,0,0,0]
s=[0,0,0,0,0]

def func2(xys):
    # добавить В и Х в конце векторов у и х
    global Ax
    global Ay
    global Bx
    global By
    global areaconstr

    #print xys

    x = xys[0:len(Ax[0])]
    np.append(x,B)
    y = xys[len(Ax[0]):len(Ax[0])+len(Ay[0])]
    np.append(y,H)
    s = xys[len(Ax[0])+len(Ay[0]):len(Ax[0])+len(Ay[0])+len(Ax)]
    sx = xys[len(Ax[0])+len(Ay[0])+len(Ax):len(Ax[0])+len(Ay[0])+len(Ax)+len(Bx)]
    sy = xys[len(Ax[0])+len(Ay[0])+len(Ax)+len(Bx):]

    res1 = Ax.dot(x)*Ay.dot(y)- s - areaconstr
    res2 = Bx.dot(xys[0:len(Ax[0])]) - sx
    res3 = By.dot(xys[len(Ax[0]):len(Ax[0])+len(Ay[0])]) - sy

    return sum(np.absolute(res1))+sum(np.absolute(res2))+sum(np.absolute(res3))


def summ(x):
    return sum(x)

def summ(x,y):
    return x+y

summ(10,20)

t1=time.clock()
func2(x,y,s)
t2=time.clock()
t2-t1

def optim_placement(placemnt, xlistnew, ylistnew):

    xlist = list(set(placemnt[0]))
    xlist.sort()
    xlistnew = [0]+xlistnew
    # xlist.remove(0)
    # xlist.remove(B)
    plac_new = copy.copy(placemnt)
    for i in range(len(placemnt[0])):
        plac_new[0][i]=xlistnew[xlist.index(placemnt[0][i])]

    ylist = list(set(placemnt[1]))
    ylist.sort()
    ylistnew = [0] + ylistnew
    # ylist.remove(0)
    for i in range(len(placemnt[1])):
        plac_new[1][i] = ylistnew[ylist.index(placemnt[1][i])]

    return plac_new


xlistnew = [1.85560736e+00, 7.61048607e+00, 8.43569489e+00]
ylistnew = [2.38739016e+00, 5.05108607e+00, 5.24403547e+00, 5.25532927e+00, 5.29781274e+00]
optim_placement(placemnt, xlistnew, ylistnew)

res=opt.differential_evolution(func2, bounds)
res
# При визуализации, можно указать, сколько можно еще добавитть метража для каждой комнаты (при сохранении данной топологии)

def summ(x, y):
    return sum(x)-sum(y)

y=[0,0,0]
bounds = [(1,B), (0, H), (0, B), (1,B), (0, H), (0, B)]
res=opt.differential_evolution(summ, bounds)
1

import scipy.optimize

A = np.zeros((3, 3))
A[0][0]=1
A[0][1]=2
A[0][2]=3
A[1][0]=1
A[1][1]=1
A[1][2]=1
A[2][0]=2
A[2][1]=4
A[2][2]=6

A=np.ndarray([[1, 2, 3],[3, 3, 3],[2, 4, 6]])

def F(x):
    return A.dot(x)

makematr(wogapes_playsments[0])
bounds
x = scipy.optimize.broyden1(func2,(0,0,0,0,0,0,0,0,0,0,0))
x
F(x)
array([ 4.04674914,  3.91158389,  2.71791677,  1.61756251])
np.cos(x) + x[::-1]
array([ 1.,  2.,  3.,  4.])
