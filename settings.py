# -*- coding: utf-8 -*-
# файл с настройками проекта

# максимальное количество результатов при расчете топологии секции
sett_max_results_sect_topol = 1

# сдвиг подъезда по горизонтали
podezd_position_x_delta = 1

# изменение высоты подъезда
podezd_height_delta = 1

# шаг сетки колонн
sett_grid_columns = [6,7,8]

#  коэффициент влияние отклонений стен секции от сетки колонн на целевую функцию
sett_grid_columns_influence = 150

# настройки генетического алгоритма для планировок секции
sett_popsize=30
sett_tol=0.01
sett_strategy="randtobest1bin"
sett_init='latinhypercube'
sett_mutation = 1 # it should be in the range [0, 2].
sett_recombination = 0.5 # should be in the range [0, 1]

# Включение/выкл. доводчика секции под сетку колонн
sett_isActive_sect_closer = True
