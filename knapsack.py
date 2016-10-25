# -*- coding: utf-8 -*-
# импортируем функции PuLP
from pulp import *

B=20
H=20
B1=2.5
H1=15
# коридор горизонтальный
B2=B/2
H2=2

def Knapsack(B, H, B1, H1, B2, H2):
    # Создаем новую задачу Линейного программирования (LP) с максимизацией целевой функции
    prob = LpProblem("Knapsack problem", LpMaximize)

    # Переменные оптимизации, целые
    x1 = LpVariable("x1", 0, 2, 'Integer')
    x2 = LpVariable("x2", 0, 2, 'Integer')
    x3 = LpVariable("x3", 0, 2, 'Integer')
    x4 = LpVariable("x4", 0, 2, 'Integer')

    # Целевая функция ("ценность рюкзака")
    areas = [45, 60, 90, 110]
    prob += areas[0] * x1 + areas[1] * x2 + areas[2] * x3 + areas[3] * x4, "obj"

    # Ограничение ("вес рюкзака")
    prob += areas[0] * x1 + areas[1] * x2 + areas[2] * x3 + areas[3] * x4 <= B*H-B1*H1-B2*H2, "c1"

    # Запускаем решатель
    prob.solve()

    # Выводим статус задачи
    #print "Status:", LpStatus[prob.status]

    # # Выводим получившиеся оптимальные значения переменных
    # for v in prob.variables():
    #     print v.name, "=", v.varValue
    # # Выводим оптимальное значение целевой функции
    # print ("objective = %s$" % value(prob.objective))

    # возвращаем список Количество квартир, Список площадей
    varres=[]
    areasres=[]
    for i, var in enumerate(prob.variables()):
        if var.varValue!=0:
            varres.append(var.varValue)
            areasres.append(areas[i])

    return varres, areasres
