from operator import itemgetter, attrgetter
import random
import sys
import os
import math
import re
import numpy as np
import time

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# GLOBAL VARIABLES

solution_found = False
popN =30 # n number of chromos per population
max_iterations = 500
target = 1111.0
crossover_rate = 0.95
mutation_rate = 0.1
Ki = 0.5 # коэффициент эммиграции
Parent_lvl = 1 # доля родителей
eps=0.01
classic =  ([(1,2),(1,2),(1,2),(1,2),(3,4),(3,4),(5,6),(5,6),(5,6),(3,2),(1,4),(2,6)]*4, 24,24) #- классич 24*24
ulitka_big = ([(15,5),(5,16),(17,4),(3,12),(13,3),(2,8),(8,3),(4,8),(5,2),(1,4),(3,1),(2,2),(1,3),(1,3),(1,3)],20,20) # 20*20 улитка крупная
ulitka_small = ([(6,4),(4,7),(7,3),(3,6),(2,2),(1,3),(2,1)], 10, 10) #- улитка мелкая
task = ulitka_big

flats = task[0]
size = len(flats)
B=task[1]
H=task[2]
K=2 # подкручиванием К до 100 дожимал классик, для улитки К нужен =2

math.factorial(15)

"""Generates random population of chromos"""
def generatePop (popN):
  chromos, chromo = [], []
  for eachChromo in range(popN):
    chromo= tuple(np.random.permutation(size))
    chromos.append(chromo)
  return chromos

#ранжирование
"""Takes a population of chromosomes and returns a list of tuples where each chromo is paired to its fitness scores and ranked accroding to its fitness"""
def rankPop (chromos):
  area = []
  i = 1
  # translate each chromo into mathematical expression (protein), evaluate the output of the expression,
  # calculate the inverse error of the output
  for chromo in chromos:
    res = decoder(chromo)[0]
    area.append(res)

  pairedPop = zip (chromos, area) # pair each chromo with its protein, ouput and fitness score
  rankedPop = sorted ( pairedPop, key = itemgetter(1), reverse = True ) # sort the paired pop by ascending fitness score
  return rankedPop



""" taking a ranked population selects two of the fittest members using roulette method"""
def selectFittest (fitnessScores, rankedChromos):
  while 1 == 1: # ensure that the chromosomes selected for breeding are have different indexes in the population
    index1 = roulette (fitnessScores, -1)
    index2 = roulette (fitnessScores, index1)
    if index1 == index2:
      continue
    else:
      break


  ch1 = rankedChromos[index1] # select  and return chromosomes for breeding
  ch2 = rankedChromos[index2]
  return ch1, ch2

"""Fitness scores are fractions, their sum = 1. Fitter chromosomes have a larger fraction.  """
def roulette (fitnessScores, delindex):
    return np.random.randint(0,int(len(fitnessScores)*Parent_lvl))

  # cumalativeFitness = 0.0
  # r = random.random()*B*H # это надо выносить в параметры
  #
  # for i in range(len(fitnessScores)): # for each chromosome's fitness score
  #     if (i!=delindex):
  #       cumalativeFitness += fitnessScores[i] # add each chromosome's fitness score to cumalative fitness
  #
  #       if cumalativeFitness > r: # in the event of cumalative fitness becoming greater than r, return index of that chromo
  #         return i

#скрещивание
def crossover (ch1, ch2):
# at a random chiasma
    r = random.randint(0,size-1) # начальная позиция
    d = random.randint(0,size-r) # сдвиг
    r2=r+d
    #print r, r2
    if r!=r2:
        tmp1  =  list(ch1[r:r2])
        tmp2  =  list(ch2[r:r2])
    else:
        tmp1=[]
        tmp2=[]
        tmp1.append(ch1[r])
        tmp2.append(ch2[r])
    tmp2_2 = list(ch2)
    tmp1_2 = list(ch1)
    #print tmp1
    for i in tmp1:
        tmp2_2.remove(i)

    for i in tmp2:
        tmp1_2.remove(i)

    tmp1.extend(tmp2_2)
    tmp2.extend(tmp1_2)

    return tmp1, tmp2

#мутация
def mutate (ch):
    mutatedCh = list(ch)
    if random.random() < mutation_rate:
        r = random.randint(0, size - 2)
        tmp = mutatedCh[r]
        mutatedCh[r]=mutatedCh[r+1]
        mutatedCh[r+1]=tmp
  #assert mutatedCh != ch
    return mutatedCh

"""Using breed and mutate it generates two new chromos from the selected pair"""
def breed (ch1, ch2):

  newCh1, newCh2 = [], []
  if random.random() < crossover_rate: # rate dependent crossover of selected chromosomes
    newCh1, newCh2 = crossover(ch1, ch2)
  else:
    newCh1, newCh2 = ch1, ch2
  newnewCh1 = mutate (newCh1) # mutate crossovered chromos
  newnewCh2 = mutate (newCh2)

  return newnewCh1, newnewCh2

""" Taking a ranked population return a new population by breeding the ranked one"""
def iteratePop (rankedPop):
    Chromos = rankedPop
    fitnessScores = [ item[1] for item in rankedPop ] # extract fitness scores from ranked population
    rankedChromos = [ item[0] for item in rankedPop ] # extract chromosomes from ranked population

    newpop = []
    while len(newpop) < popN:
        ch1, ch2 = [], []
        ch1, ch2 = selectFittest (fitnessScores, rankedChromos) # select two of the fittest chromos

        ch1, ch2 = breed (ch1, ch2) # breed them to create two new chromosomes
        newpop.append(ch1) # and append to new population
        newpop.append(ch2)

    # добавляем случайных мигрантов
    newpop.extend(generatePop(int(popN*Ki)))

    newpoprank=rankPop(newpop)
    Chromos.extend(newpoprank)
    Chromos = sorted(Chromos, key=itemgetter(1), reverse=True)

    return [ item[0] for item in Chromos[:popN] ]

def best_node(det, nodes):
    #k=100
    s=-400000
    i=0
    j=0
    nodes_res=[]
    res=0 # прирост целевой функции, площадь перекрытия
    res2=0
    for nd in nodes:
        nodes_res.append(list(nd))

    # оптимальный узел ищем в локальной системе координат
    for nd in nodes:
        #
        #(np.sign(nd[2]-det[0]+0.01)+np.sign(nd[3]-det[1]+0.01))/(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1]))
        # 1./(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))*(1+0.05*np.sign(nd[2]-det[0]))*(1+0.05*np.sign(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1]))
        delta = 0
        if ((nd[2]-det[0]<eps) & (nd[3] - det[1] < eps)):
            delta = 1
        # delta +
        delta2= (10 ** (-10)) * (1 + 0.05 * np.sign(nd[2] - det[0])) * (1 + 0.05 * np.sign(nd[3] - det[1]))
        delta3 = (10 ** (-10)) * (min(nd[2], det[0]) * min(nd[3], det[1])) / (float(det[0] * det[1]))
        val =   delta2 + delta3 +(np.sign(nd[2]-det[0]+0.01)+np.sign(nd[3]-det[1]+0.01))/(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1]))
        #print val
        if (val>s):
            s=val
            i=j
            if ((nd[2]<0)|(nd[3]<0)):
                res=0
            else:
                res = min(nd[2],det[0])*min(nd[3],det[1]) # абсолютный результат

            res2 =  res/(float(det[0])*det[1])  # относительный результат
        j+=1
    #
    # корректируем локальные координаты
    k=0
    for nd in nodes_res:
        if nd==nodes_res[i]:
            k+=1
            continue
            # корректировка локальной высоты
        if ((nd[1]>=nodes_res[i][1]) & (nodes_res[i][0]-det[0]<nd[0]) & (nodes_res[k][3] > nodes_res[k][1] - nodes_res[i][1]) & (nodes_res[i][0]>nd[0]-nd[2])):
            nodes_res[k][3] = nodes_res[k][1] - nodes_res[i][1]
        else: # корректировка локальной ширины
            if ((nd[0]>=nodes_res[i][0]) & (nodes_res[i][1]-det[1]<nd[1]) & (nodes_res[k][2]>nodes_res[k][0] - nodes_res[i][0]) & (nodes_res[i][1]>nd[1]-nd[3])):
                nodes_res[k][2]=nodes_res[k][0] - nodes_res[i][0]
        k+=1
    # print det, res
    return i, nodes_res, res, res2

def decoder(ch):
    # пока делаем без вращения - потом надо добавить
    nodes=[(B,H,B,H)] # координаты узлов в 1.глобальной и 2.локальной системе координат
    # проходим по деталям
    placement=[]
    flats_ch = []
    for i in range(len(ch)):
        flats_ch.append(flats[ch[i]])
    result_area=0
    result_area2=0
    for flat in flats_ch:
        # ищем наилучший узел для детали
        # print "деталь - ", flat
        nd, new_nodes, res, res2 = best_node(flat, nodes)
        result_area+=res
        result_area2+=res2
        # print "прирост цел.ф-и - ", res, res2
        # print "лучший узел - ", nodes[nd]
        # print "все узлы - ", nodes
        nodes = new_nodes
        # удаляем этот узел и добавляем новый узел
        # print "узлы до обработки ", nodes
        #print nodes, nd
        nodes.append((nodes[nd][0], nodes[nd][1]-flat[1], nodes[nd][2], nodes[nd][3]-flat[1]))
        nodes.append((nodes[nd][0]-flat[0], nodes[nd][1], nodes[nd][2]-flat[0], nodes[nd][3]))
        #placement.append((B-nodes[nd][0], H - nodes[nd][0], B-nodes[nd][0]+flat[0], H - nodes[nd][0]+flat[1]))
        nodes.pop(nd)
        # убрать нулевые узлы
        t=len(nodes)
        while (t>0):
            if ((nodes[t-1][2]==0) | (nodes[t-1][3]==0)):
                nodes.pop(t-1)
            t-=1

        # проверка на одинаковые узлы
        t = len(nodes)-1
        while (t > 0):
            k=t-1
            while (k >= 0):
                if ((nodes[t][0]==nodes[k][0]) & (nodes[t][1]==nodes[k][1])):
                    nodes.pop(t)
                    break
                k-=1
            t-=1
        # print "узлы после обработки", nodes
    # if  (result_area/(float(H)*B)>0.99):
    #     solution_found=True
    #     print "НАЙДЕНО ОПТИМАЛЬНОЕ РЕШЕНИЕ!"
    return result_area, result_area2, result_area/(float(H)*B)


def placement(ch):
    # пока делаем без вращения - потом надо добавить
    nodes = [(B, H, B, H)]  # координаты узлов в 1.глобальной и 2.локальной системе координат
    # проходим по деталям

    placement = []
    flats_ch = []
    for i in range(len(ch)):
        flats_ch.append(flats[ch[i]])
    result_area = 0
    result_area2 = 0
    for flat in flats_ch:
        # ищем наилучший узел для детали
        # print "деталь - ", flat
        nd, new_nodes, res, res2 = best_node(flat, nodes)
        result_area += res
        result_area2 += res2
        # print "прирост цел.ф-и - ", res, res2
        # print "лучший узел - ", nodes[nd]
        # print "все узлы - ", nodes
        nodes = new_nodes
        # удаляем этот узел и добавляем новый узел
        # print "узлы до обработки ", nodes
        nodes.append((nodes[nd][0], nodes[nd][1] - flat[1], nodes[nd][2], nodes[nd][3] - flat[1]))
        nodes.append((nodes[nd][0] - flat[0], nodes[nd][1], nodes[nd][2] - flat[0], nodes[nd][3]))
        placement.append((B - nodes[nd][0], H - nodes[nd][1], B - nodes[nd][0] + flat[0], H - nodes[nd][1] + flat[1]))
        nodes.pop(nd)
        # убрать нулевые узлы
        t = len(nodes)
        while (t > 0):
            if ((nodes[t - 1][2] == 0) | (nodes[t - 1][3] == 0)):
                nodes.pop(t - 1)
            t -= 1

        # проверка на одинаковые узлы
        t = len(nodes) - 1
        while (t > 0):
            k = t - 1
            while (k >= 0):
                if ((nodes[t][0] == nodes[k][0]) & (nodes[t][1] == nodes[k][1])):
                    nodes.pop(t)
                    break
                k -= 1
            t -= 1

    return placement

def main():
    chromos = generatePop(popN) #generate new population of random chromosomes
    iterations = 0

    while iterations != max_iterations and solution_found != True:
        # take the pop of random chromos and rank them based on their fitness score/proximity to target output
        rankedPop = rankPop(chromos)

        print '\nCurrent iterations:', iterations

        if solution_found != True:
            # if solution is not found iterate a new population from previous ranked population
            chromos = []
            chromos = iteratePop(rankedPop)

            iterations += 1
        else:
            break
    print "Расчет закончен!"
    return chromos

def visual():
    fig1 = plt.figure(figsize=(10,10), )
    # plt.axis([-0.1, 1.1, -0.1, 1.1])
    ax1 = fig1.add_subplot(111, aspect='equal')
    i=0
    for pl in place:
        if (i % 2 ==0):
            hatch = '\\'
        else:
            hatch = '//'
        ax1.add_patch(mpatches.Rectangle((pl[0]/float(B), pl[1]/float(H)),   # (x,y)
                                         (pl[2]-pl[0])/float(B),          # width
                                         (pl[3]- pl[1])/float(H),  hatch=hatch, alpha=0.6        # height
            )
        )
        i+=1
    plt.show()


# ТЕСТИРОВАНИЕ

res=main()
decoder(res[0])
place=placement(res[0])
visual()


# наилучший результат для улитки, правда целевая функция считается некорректно
ch=[0, 1, 4, 3, 7, 2, 8, 5, 9, 12, 6, 13, 14, 11, 10]
decoder(ch)

place=placement(ch)
visual()

t1=time.clock()
for k in range(0,200,2):
    K=k/100.
    print k, decoder(ch)
t2=time.clock()
t2-t1

K=1000
decoder(ch)

det = (17, 4)
nd=(17, 4, 12, 4)
nd=[7, 15, 2, 15]
nd=[5, 4, 5, 4]

delta2 = (10 ** (-10)) * (1 + 0.05 * np.sign(nd[2] - det[0])) * (1 + 0.05 * np.sign(nd[3] - det[1]))
delta3 = (10 ** (-10))*(min(nd[2],det[0])*min(nd[3],det[1]))/(float(det[0]*det[1]))
delta3+delta2 + (np.sign(nd[2] - det[0] + 0.01) + np.sign(nd[3] - det[1] + 0.01)) / (abs(min(B - nd[2], (nd[2] - det[0])) * (nd[3] - det[1])) + 0.01 + K * (B - nd[0] + H - nd[1]))

((np.sign(nd[2]-det[0]+0.01)+np.sign(nd[3]-det[1]+0.01))/(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1])))
(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1]))

(1/(abs(min(B-nd[2],(nd[2]-det[0]))*(nd[3]-det[1]))+0.01+K*(B-nd[0]+H-nd[1])))

# http://matthiaseisen.com/pp/patterns/p0203/
# все 50 особей очень похожи, мы будто бы уперлись в локальный минимум, как из него выйти?
# алгоритм с доп.параметрами работает медленнее, при этом приходится подкручивать К до 100 и убирать delta 2 и 3  чтобы получить качество 1 на 50 итерациях на классик