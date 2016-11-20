#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Алгоритм Дейкстры
#   Находит кратчайшее расстояние от одной из вершин графа до всех остальных.
#   Алгоритм работает только для графов без рёбер отрицательного веса.
#   Матрица задается как список словарей смежности вершин
# Описание алгоритма http://goo.gl/KsqC

# U — множество посещённых вершин
# d[u] — по окончании работы алгоритма равно длине кратчайшего пути из {\displaystyle a} a до вершины {\displaystyle u} u
# p[u] — по окончании работы алгоритма содержит кратчайший путь из {\displaystyle a} a в {\displaystyle u} u

def dijkstra_shortest_path2(graph, start, p={}, u=[], d={}):
    if len(p) == 0: p[start] = 0; print "инициализация начального пути"
    print p
    # print "start V: %d, " % (start)
    for x in graph[start]:
        if (x not in u and x != start):
            if (x not in p.keys() or (graph[start][x] + p[start]) < p[x]):
                p[x] = graph[start][x] + p[start]

    u.append(start)

    min_v = 0
    min_x = None
    for x in p:
        # print "x: %d, p[x]: %d, mv %d" % (x, p[x], min_v)
        if (p[x] < min_v or min_v == 0) and x not in u:
                min_x = x
                min_v = p[x]

    if(len(u) < len(graph) and min_x):
        return dijkstra_shortest_path2(graph, min_x, p, u)
    else:
        return p

def dijkstra_shortest_path(graph, start, p={}, u=[], d={}):
    # p - метки вершин
    # u - список посещенных вершин
    # d - ?
    infinity = 100000 # заведомо большое число
    # Инициализация. Метка самой вершины a полагается равной 0, метки остальных вершин — бесконечности.
    if len(p) == 0:
        print "инициализация"
        for i in range(len(graph)):
            p[i] = infinity
        p[start] = 0

    # Шаг алгоритма

    for x in graph[start]: # для всех соседей выбранной вершины
        if (x not in u and x != start): # рассматриваем только неокрашенных соседей
            if (graph[start][x] + p[start] < p[x]):
                p[x] = graph[start][x] + p[start]

    u.append(start)

    # из ещё не посещённых вершин выбирается вершина u, имеющая минимальную метку.
    min_v = infinity
    min_x = None
    for x in p:
        # print "x: %d, p[x]: %d, mv %d" % (x, p[x], min_v)
        if (p[x] < min_v ) and (x not in u):
                min_x = x
                min_v = p[x]
    print "p: ", p
    print "min_x: ", min_x
    print "u: ", u
    print "NEXT"
    # если нет непосещенных вершин, то завершаем работу
    if(len(u) < len(graph)):
        return dijkstra_shortest_path(graph, min_x, p, u)
    else:
        return p

def dijkstra_shortest_path_general(graph, start, p={}, u=[], d={}):
    # p - метки вершин
    # u - список посещенных вершин
    # d - ?
    infinity = 100000 # заведомо большое число
    # Инициализация. Метка самой вершины a полагается равной 0, метки остальных вершин — бесконечности.
    if len(p) == 0:
        print "инициализация"
        for i in range(len(graph)):
            p[i] = infinity
        p[start] = 0

    # Шаг алгоритма

    startnode_will_uncolor = False
    for x in graph[start]: # для всех соседей выбранной вершины
        if (x != start): # рассматриваем ТАКЖЕ окрашенных соседей
            if (graph[start][x] + p[start] < p[x]):
                if x in u:
                    u.remove(x)
                    #startnode_will_uncolor = True
                p[x] = graph[start][x] + p[start]

    if (not startnode_will_uncolor):
        u.append(start)

    # из ещё не посещённых вершин выбирается вершина u, имеющая минимальную метку.
    min_v = infinity
    min_x = None
    for x in p:
        # print "x: %d, p[x]: %d, mv %d" % (x, p[x], min_v)
        if (p[x] < min_v ) and (x not in u):
                min_x = x
                min_v = p[x]
    print "p: ", p
    print "min_x: ", min_x
    print "u: ", u
    print "NEXT"
    # если нет непосещенных вершин, то завершаем работу
    if(len(u) < len(graph)):
        return dijkstra_shortest_path_general(graph, min_x, p, u)
    else:
        return p

def optimGraphPath(graph, start, p={}, u=[], minim = True):
    # p - метки вершин
    # u - список посещенных вершин
    # d - ?

    infinity = 100000 # заведомо большое число
    # Инициализация. Метка самой вершины a полагается равной 0, метки остальных вершин — бесконечности.
    if len(p) == 0:
        print "инициализация"
        for i in range(len(graph)):
            p[i] = infinity
        p[start] = 0
        # если minim != True, то надо все веса ребер умножить на -1
        if not minim:
            for dct in graph:
                for k in dct:
                    dct[k] = -dct[k]

    # Шаг алгоритма

    startnode_will_uncolor = False
    for x in graph[start]: # для всех соседей выбранной вершины
        if (x != start): # рассматриваем ТАКЖЕ окрашенных соседей
            if (graph[start][x] + p[start] < p[x]):
                if x in u:
                    u.remove(x)
                    #startnode_will_uncolor = True
                p[x] = graph[start][x] + p[start]

    if (not startnode_will_uncolor):
        u.append(start)

    # из ещё не посещённых вершин выбирается вершина u, имеющая минимальную метку.
    min_v = infinity
    min_x = None
    for x in p:
        # print "x: %d, p[x]: %d, mv %d" % (x, p[x], min_v)
        if (p[x] < min_v ) and (x not in u):
                min_x = x
                min_v = p[x]
    print "p: ", p
    print "min_x: ", min_x
    print "u: ", u
    print "NEXT"
    # если нет непосещенных вершин, то завершаем работу
    if(len(u) < len(graph)):
        return optimGraphPath(graph, min_x, p, u, minim)
    else:
        if not minim:
            for k in p:
                p[k] = -p[k]
        return p

if __name__ == '__main__':
    # инициализация графа с помощью словаря смежности
    a, b, c, d, e, f, g, h = range(8)
    N = [
        {b: 7, c: 9, f: 14},
        {a: 7, c: 10, d: 15},
        {a: 9, b: 10, d: 11, f: 2},
        {b: 15, c: 11, e: 6},
        {d: 6, f: 9},
        {a: 14, c: 2, e: 9},
        {h: 2},
        {g: 2},
    ]
    for i in range(1):
        print dijkstra_shortest_path(N, a)
# b in N[a] - смежность
# len(N[f]) - степень
# N[a][b] - вес (a,b)
# print N[a][b]



# граф смежности
from Flat2Rooms import place2scen
import numpy as np

def pl2graph(pl, maxwidth, minwidth, left2right = True, maxim = True, dim = 0):
    #left2right = True - граф строится слева направо, при этом длина ребра (i,j) равна размеру помещения i
    #left2right = False - граф строится справа налево, при этом длина ребра (i,j) равна размеру помещения j
    if maxim:
        optwidth = maxwidth
    else:
        optwidth = minwidth

    def pl2graphloc(vertex_iter, dim, optwidth, graphmin=[], processed = set()):
        if len(vertex_iter) == 0:
            return graphmin

        # для каждой вершины найти все смежные с ней
        vertex_iter_new = set()
        for v in vertex_iter:
            # все смежные с v вершины
            v_adj = filter(lambda x: sc[v][x][0] in adj_list, range(len(pl[dim])/2))
            for vi in v_adj:
                if left2right:
                    graphmin[v][vi] = optwidth[v]
                else:
                    graphmin[v][vi] = optwidth[vi]
            # вершины примыкающие к правой стороне оболочки
            if sc[0][v][0] in adj_right_envel:
                if left2right:
                    graphmin[v][len(pl[dim])/2] = optwidth[v]
                else:
                    graphmin[v][len(pl[dim]) / 2] = 0
            vertex_iter_new = vertex_iter_new | set(v_adj)
        vertex_iter_new = vertex_iter_new - processed
        processed = processed | vertex_iter

        return pl2graphloc(vertex_iter_new, dim, optwidth, graphmin, processed)

    # елси left2right = False, то планировку надо отразить относительно вертикали/горизонтали
    plnew = [[],[]]
    if not left2right:
        if dim == 0:
            plnew[1] = pl[1]
            for i in range(len(pl[0])/2):
                plnew[0].append(min(max(pl[0])-pl[0][i*2], max(pl[0])-pl[0][i*2 + 1]))
                plnew[0].append(max(max(pl[0])-pl[0][i*2], max(pl[0])-pl[0][i*2 + 1]))
            pl = plnew
        else:
            plnew[0] = pl[0]
            for i in range(len(pl[1]) / 2):
                plnew[1].append(min(max(pl[1]) - pl[1][i * 2], max(pl[1]) - pl[1][i * 2 + 1]))
                plnew[1].append(max(max(pl[1]) - pl[1][i * 2], max(pl[1]) - pl[1][i * 2 + 1]))
            pl = plnew

    sc = place2scen(pl)
    # надо 4 графа - для миним/макс * вертикал/горизонтал
    xlist = list(set(pl[dim]))
    xlist.sort()
    xlist.remove(0) #?
    graphmin = [{} for x in range((len(pl[dim])/2+1))]

    # примыкающие слева/сверху
    if dim == 0:
        adj_list = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12)]
    else:
        adj_list = [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1)]

    # примыкающие к правой/верхней границе оболочки
    if dim == 0:
        adj_right_envel = [(7, 6), (7, 7), (7, 8), (7, 9)]
    else:
        adj_right_envel = [(6, 7), (7, 7), (8, 7), (9, 7)]

    # обработанные вершины
    processed = set()
    # вершины для следующих итераций
    vertex_iter = set()

    if dim == 0:
        inenvelop_list = [(9,6),(9,7),(9,8),(9,9)]
    else:
        inenvelop_list = [(6,9),(7,9),(8,9),(9,9)]

    v = 0
    v_adj = filter(lambda x: sc[v][x][0] in inenvelop_list, range(len(pl[dim]) / 2))

    # для стартового элемента добавляем смежные с ним вершины с ребрами веса 0
    for i in v_adj:
        if left2right:
            graphmin[0][i] = 0
        else:
            graphmin[0][i] = optwidth[i]


    processed.add(0)
    vertex_iter = vertex_iter | set(v_adj)

    return pl2graphloc(vertex_iter, dim, optwidth, graphmin, processed)

G = pl2graph(pl2)

pl = [[0,10,2,4,1,5,0,1,1,3,3,5,5,10,0,2,4,10],[0,10,0,1,1,2,1,10,2,10,2,10,1,10,0,1,0,1]]

pl2 = [[0,10,2,4,1,5,0,1,1,3,3,5,5,10,0,1,1,2,4,5,5,10],[0,10,0,1,1,3,2,10,3,10,3,10,2,10,0,2,0,1,0,1,0,2]]
len(pl2[0])
len(pl2[1])

G = [{3: 0, 7: 0}, #0
 {9: 10}, #1
 {6: 10, 10: 10}, #2
 {2: 10, 4: 10, 8: 10}, #3
 {5: 10}, #4
 {6: 10, 10: 10}, #5
 {11: 10}, #6
 {2: 10, 4: 10, 8: 10}, #7
 {1: 10}, #8
 {6: 10, 10: 10}, #9
 {11: 10}, #10
 {}] #11

Gnegative = [{3: 0, 7: 0}, #0
 {9: -10}, #1
 {6: -10, 10: -10}, #2
 {2: -10, 4: -10, 8: -10}, #3
 {5: -10}, #4
 {6: -10, 10: -10}, #5
 {11: -10}, #6
 {2: -10, 4: -10, 8: -10}, #7
 {1: -10}, #8
 {6: -10, 10: -10}, #9
 {11: -10}, #10
 {}] #11

[{3: 0, 7: 0},
 {9: 10},
 {6: 10, 10: 10},
 {2: 10, 4: 10, 8: 10},
 {5: 10},
 {6: 10, 10: 10},
 {11: 10},
 {2: 10, 4: 10, 8: 10},
 {1: 10},
 {6: 10, 10: 10},
 {11: 10},
 {}]

dijkstra_shortest_path(Gtest2, 0)
dijkstra_shortest_path(G, 0)

Gtest = [{1: 1, 2: 3, 5: 3, 3: 5},
 {2: 3, 3: 2},
 {3: 4, 2: 4},
 {4: 1, 5: 5},
 {5: 2},
         {}
 ]

Gtest2 = [{1: 1, 2: 7, 5: 3, 3: 5},
 {2: 3, 3: 2},
 {4: 4},
 {2: 0.2, 5: 5, 4: 1},
 {5: 2},
{}
 ]
maxwidth = [10]*(len(Gtest2))
dijkstra_shortest_path(Gtest2, 0)

# граф диодный мостик
Gtest3 = [{1: 1, 2: 3},
 {2: 1, 3: 2},
 {3: 4},
{}
 ]
Gtest4 = [{1: 1, 2: 3},
 {3: 2},
 {1:3, 3: 4},
{}
 ]
Gtest4negative = [{1: -20, 2: -20},
 {3: 2},
 {3: 4},
{}
 ]

Gtest5negative = [{1: 2, 2: 1},
 {2: -2},
{}
 ]


dijkstra_shortest_path(Gtest3, 0)
dijkstra_shortest_path(Gtest4, 0)
dijkstra_shortest_path2(Gtest3, 0, {}, [])
dijkstra_shortest_path2(G, 0, {}, [])
dijkstra_shortest_path(G, 0, {}, [])
dijkstra_shortest_path_general(Gnegative, 0, {}, [])

def createbounds(pl, B, H):
    # ToDo выносить в настройки
    maxwidth_x = [30, 6, 20] + [15]*(len(pl[0]) / 2 - 3)  # максимальные ширины
    minwidth_x = [30, 6, 6]+ [4.5]*(len(pl[0]) / 2 - 3) # минимальные ширины
    maxwidth_y = [30, 6, 3] + [15]*(len(pl[0]) / 2 - 3)  # максимальные ширины
    minwidth_y = [30, 6, 2]+ [4.5]*(len(pl[0]) / 2 - 3) # минимальные ширины
    # на входе планировка pl
    def createboundsdim(pl, B, H, dim, maxwidth, minwidth):
        if dim == 0:
            BH = B
        else:
            BH = H
        print "BH: ", BH
        # готовим графы
        Gminleft = pl2graph(pl, maxwidth, minwidth, left2right=True, maxim=False, dim=dim) # граф с минимальными ширинами на ребрах, старт слева
        Gminright = pl2graph(pl, maxwidth, minwidth, left2right=False, maxim=False, dim=dim)
        Gmaxleft = pl2graph(pl, maxwidth, minwidth, left2right=True, maxim=True, dim=dim)
        Gmaxright = pl2graph(pl, maxwidth, minwidth, left2right=False, maxim=True, dim=dim)

        # список мин/макс путей
        p00 = optimGraphPath(Gminleft, start=0, p={}, u=[], minim = False)
        p01 = optimGraphPath(Gmaxright, start=0, p={}, u=[], minim = True)
        p10 = optimGraphPath(Gmaxleft, start=0, p={}, u=[], minim = True)
        p11 = optimGraphPath(Gminright, start=0, p={}, u=[], minim = False)

        # выделим уровни, кроме крайних
        xlist = list(set(pl[dim]))
        xlist.sort()
        xlist.remove(0)
        xlist.remove(max(xlist))

        plnp = np.array(pl[dim])
        levmin = []
        levmax = []
        for lev in xlist:
        # для каждого уровня берем все правые смежные элементы
            plnptmp = np.array(range(len(plnp)))[plnp==lev]
            plnptmp = filter(lambda x: x%2 == 0, plnptmp)
            plnptmp = map(lambda x: x//2, plnptmp)
        # и для каждого элемента рассчитываем pxx
            mininterdown = []
            mininterup = []
            maxinterdown = []
            maxinterup = []
            for i in plnptmp:
                mininterdown.append(p00[i])
                mininterup.append(p01[i])
                maxinterdown.append(p10[i])
                maxinterup.append(p11[i])
            print "mininterdown: ", mininterdown
            print "mininterup: ", mininterup
            print "maxinterdown: ", maxinterdown
            print "maxinterup: ", maxinterup
            print BH
            levmin.append(max(max(mininterdown),BH - min(mininterup)))
            levmax.append(min(min(maxinterdown),BH - max(maxinterup)))
        return zip(levmin, levmax)
    bounds = createboundsdim(pl, B, H, 0, maxwidth_x, minwidth_x)
    bounds += createboundsdim(pl, B, H, 1, maxwidth_y, minwidth_y)
    return bounds

def testf(x):
    print x**3

copyf = testf
pl= [[0,30,0,15,15,30,0,15,15,30],[0,20,10,20,10,20,0,10,0,10]]