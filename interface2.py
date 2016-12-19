# -*- coding: utf-8 -*-
# Найденные планировки в JSON
import json
# преобразует список планировок КВАРТИР в список словарей, который конвертится в json
def pl2json(list_pl, StartPosId, col_list, flats_out_walls, entrwall, addshift = (0,0,0,0)):

    """
    list_pl - список планировок квартир для секции
    StartPosId - список координат левого нижнего угла для каждой квартиры
    addshift - координаты нижнего левого угла секции
    >>> compartments = ["envelope",  "hall", "corr", "bath", "kitchen", "room", "room2"]
    >>> tt=[[0.0,1.3636363636363635,0.0,3.1818181818181817,1.3636363636363635,2.2727272727272729,2.2727272727272729,3.1818181818181817,0.0,3.1818181818181817,3.1818181818181817,5.0],
    ... [0.0,2.3999999999999999,2.3999999999999999,4.7999999999999998,0.0,2.3999999999999999,0.0,2.3999999999999999,4.7999999999999998,6.0,0.0,6.0]]
    >>> ss=pl2json(tt, compartments)
    >>> (ss['BimType'], ss['rooms'][0]['Deep'], ss['rooms'][0]['Position']['X'])
    ('functionalzone', 2.4, 1.36)
    """
    compartments = ["envelope", "hall", "corr", "bath", "kitchen", "room", "room", "room", "room", "room"]
    newres = []
    col_list = ['#73DD9B','#73DD9B','#73DD9B', '#EAE234', '#ECA7A7', '#ACBFEC','#ACBFEC','#ACBFEC','#ACBFEC','#ACBFEC','#ACBFEC','#ACBFEC']
    def calcul_door(walls, wall_num, adj_part = []):
        '''
        функция на стену с номером wall_num вешает дверь и прикрепляет ее в словарь walls
        :param walls:
        :param wall_num:
        :return:
        '''
        if len(adj_part) == 0:
            x1 = walls[-1][wall_num]["x1"]
            x2 = walls[-1][wall_num]["x2"]
            y1 = walls[-1][wall_num]["y1"]
            y2 = walls[-1][wall_num]["y2"]
        else:
            x1 = adj_part[0]
            y1 = adj_part[1]
            x2 = adj_part[2]
            y2 = adj_part[3]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        dx1 = mx + (x1 - x2) * 0.45 / (((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
        dx2 = mx - (x1 - x2) * 0.45 / (((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
        dy1 = my + (y1 - y2) * 0.45 / (((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
        dy2 = my - (y1 - y2) * 0.45 / (((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
        walls[-1][wall_num]["door"] = {}
        walls[-1][wall_num]["door"]["x1"] = round(dx1,2)
        walls[-1][wall_num]["door"]["x2"] = round(dx2,2)
        walls[-1][wall_num]["door"]["y1"] = round(dy1,2)
        walls[-1][wall_num]["door"]["y2"] = round(dy2,2)

    def get_adj_wall(walls, j, hall_lev, corr_lev):
        '''
        возвращает номер стены смежной с прихожей или (при его отсутствии) с коридором и номер стены прихожей/коридора
        :param walls: словарь стен
        :param j:  порядковый номер комнаты для которой ищем стену
        :param hall_lev: тьюпл с уровнями прихожей
        :param corr_lev:
        :return:
        '''
        if walls[-1][3]["y1"] == hall_lev[3]:  # нижняя стена
            wall_num_room, wall_num_hall = 3, 1
            is_horiz = True
            hall_corr = 0
        elif walls[-1][2]["x1"] == hall_lev[0]:
            wall_num_room, wall_num_hall = 2, 0
            is_horiz = False
            hall_corr = 0
        elif walls[-1][1]["y1"] == hall_lev[2]:
            wall_num_room, wall_num_hall = 1, 3
            is_horiz = True
            hall_corr = 0
        elif walls[-1][0]["x1"] == hall_lev[1]:
            wall_num_room, wall_num_hall = 0, 2
            is_horiz = False
            hall_corr = 0
        elif walls[-1][3]["y1"] == corr_lev[3]:  # нижняя стена
            wall_num_room, wall_num_hall = 3, 1
            is_horiz = True
            hall_corr = 1
        elif walls[-1][2]["x1"] == corr_lev[0]:
            wall_num_room, wall_num_hall = 2, 0
            is_horiz = False
            hall_corr = 1
        elif walls[-1][1]["y1"] == corr_lev[2]:
            wall_num_room, wall_num_hall = 1, 3
            is_horiz = True
            hall_corr = 1
        elif walls[-1][0]["x1"] == corr_lev[1]:
            wall_num_room, wall_num_hall = 0, 2
            is_horiz = False
            hall_corr = 1
        else:
            return -1, -1, []

        # расчет отрезка ниже только для горизонтальныйх или вертикальных отрезков
        if is_horiz:
            points_list = [walls[-1][wall_num_room]["x1"], walls[-1][wall_num_room]["x2"], walls[hall_corr][wall_num_hall]["x1"], walls[hall_corr][wall_num_hall]["x2"]]
            points_list.sort()
            adj_part = [points_list[1], walls[-1][wall_num_room]["y1"], points_list[2], walls[-1][wall_num_room]["y1"]]
        else:
            points_list = [walls[-1][wall_num_room]["y1"], walls[-1][wall_num_room]["y2"], walls[hall_corr][wall_num_hall]["y1"], walls[hall_corr][wall_num_hall]["y2"]]
            points_list.sort()
            adj_part = [walls[-1][wall_num_room]["x1"], points_list[1], walls[-1][wall_num_room]["x1"], points_list[2]]


        return wall_num_room, wall_num_hall, adj_part

    for pl, i in zip(list_pl, range(len(StartPosId))):
        locd = {}
        locd_room = []

        # подготовка списка стен и флага внешняя/внутренняя IsOut = True
        Bt = max(pl[0])
        Ht = max(pl[1])
        walls = []
        for j in range(1, len(pl[0]) / 2):
            room_out_walls = []
            # левая стена
            dicttmp = {}
            dicttmp["isOut"] = False
            if (pl[0][2 * j] == 0) and (flats_out_walls[i][0] == 1):
                dicttmp["isOut"] = True
            dicttmp["x1"] = round(StartPosId[i][0] + pl[0][2 * j],2)
            dicttmp["y1"] = round(StartPosId[i][1] + pl[1][2 * j],2)
            dicttmp["x2"] = round(StartPosId[i][0] + pl[0][2 * j],2)
            dicttmp["y2"] = round(StartPosId[i][1] + pl[1][2 * j + 1],2)
            room_out_walls.append(dicttmp)

            # верхняя стена
            dicttmp = {}
            dicttmp["isOut"] = False
            if (pl[1][2 * j + 1] == Ht) and (flats_out_walls[i][1] == 1):
                dicttmp["isOut"] = True
            dicttmp["x1"] = round(StartPosId[i][0] + pl[0][2 * j],2)
            dicttmp["y1"] = round(StartPosId[i][1] + pl[1][2 * j + 1],2)
            dicttmp["x2"] = round(StartPosId[i][0] + pl[0][2 * j + 1],2)
            dicttmp["y2"] = round(StartPosId[i][1] + pl[1][2 * j + 1],2)
            room_out_walls.append(dicttmp)

            # правая стена
            dicttmp = {}
            dicttmp["isOut"] = False
            if (pl[0][2 * j + 1] == Bt) and (flats_out_walls[i][2] == 1):
                dicttmp["isOut"] = True
            dicttmp["x1"] = round(StartPosId[i][0] + pl[0][2 * j + 1],2)
            dicttmp["y1"] = round(StartPosId[i][1] + pl[1][2 * j + 1],2)
            dicttmp["x2"] = round(StartPosId[i][0] + pl[0][2 * j + 1],2)
            dicttmp["y2"] = round(StartPosId[i][1] + pl[1][2 * j],2)
            room_out_walls.append(dicttmp)

            # нинжняя стена
            dicttmp = {}
            dicttmp["isOut"] = False
            if (pl[1][2 * j] == 0) and (flats_out_walls[i][3] == 1):
                dicttmp["isOut"] = True
            dicttmp["x1"] = round(StartPosId[i][0] + pl[0][2 * j + 1],2)
            dicttmp["y1"] = round(StartPosId[i][1] + pl[1][2 * j],2)
            dicttmp["x2"] = round(StartPosId[i][0] + pl[0][2 * j],2)
            dicttmp["y2"] = round(StartPosId[i][1] + pl[1][2 * j],2)
            room_out_walls.append(dicttmp)

            walls.append(room_out_walls)

            # Подготовка данных для дверей
            # уровни прихожей
            if j ==1:
                levx1_hall = walls[0][0]["x1"]
                levx2_hall = walls[0][2]["x1"]
                levy1_hall = walls[0][3]["y1"]
                levy2_hall = walls[0][1]["y1"]
                levs_hall = (levx1_hall, levx2_hall, levy1_hall, levy2_hall)
            # уровни коридора
            if j == 2:
                levx1_corr = walls[1][0]["x1"]
                levx2_corr = walls[1][2]["x1"]
                levy1_corr = walls[1][3]["y1"]
                levy2_corr = walls[1][1]["y1"]
                levs_corr = (levx1_corr, levx2_corr, levy1_corr, levy2_corr)

            if j == 1: # hall, вешаем дверь на входную стену
                entry = entrwall[i][0]
                calcul_door(walls, entry)
            elif j in [3, 4, 5]:  # bath, kitchen, room1 вешаем дверь смежную с прихожей и коридором
                wall_num, wall_num_hall, adj_part = get_adj_wall(walls, j, levs_hall, levs_corr)
                calcul_door(walls, wall_num, adj_part)
            elif j > 5:  # room2+, вешаем дверь смежную с прихожей и коридором или если такой нет, то на стену смежную с room1
                wall_num, wall_num_hall, adj_part = get_adj_wall(walls, j, levs_hall, levs_corr)
                if wall_num != -1:
                    calcul_door(walls, wall_num, adj_part)
                else:
                    t = j-1
                    while t >=5:
                        levx1_room = walls[t][0]["x1"]
                        levx2_room = walls[t][2]["x1"]
                        levy1_room = walls[t][3]["y1"]
                        levy2_room = walls[t][1]["y1"]
                        levs_room = (levx1_room, levx2_room, levy1_room, levy2_room)
                        wall_num, wall_num_hall, adj_part = get_adj_wall(walls, j, levs_room, levs_corr)
                        calcul_door(walls, wall_num, adj_part)
                        t -= 1

        for t in range(1,len(pl[0]) / 2):
            deep = round(pl[1][2 * t + 1] - pl[1][2 * t], 2)
            width = round(pl[0][2 * t + 1] - pl[0][2 * t], 2)
            locd_room.append({"BimType": "room", 'name': compartments[t], "color": col_list[t], "Deep": deep, "Width": width,
                              "Position": {"X": round(StartPosId[i][0] + pl[0][2 * t] + addshift[0],2), "Z": round(StartPosId[i][1] + pl[1][2 * t] + addshift[1],2),
                                 "Y": addshift[2]}, "walls": walls[t-1]})

        locd["BimType"] = "functionalzone"
        locd["name"] = "flat"
        locd["Position"] = {"X": round(StartPosId[i][0],2), "Z": round(StartPosId[i][1],2), "Y": round(addshift[2],2)}
        locd["ParentId"] = addshift[3]
        locd["rooms"] = locd_room
        newres.append(locd)


    return newres #json.dumps(newres)


# Преобразует входные данные о секциях во вход для алгоритма.
def json2params(json_data):
    """
    >>> js = {u'BimType': u'functionalzone',
    ... u'Deep': 20,
    ... u'Height': 3,
    ... u'Id': 6050,
    ... u'ParentId': 4,
    ... u'Position': {u'X': 50, u'Y': 0, u'Z': 0},
    ... u'Width': 10}
    >>> s1, s2 = json2params(js)
    >>> (s1[0],s2[5])
    ((20, 3),[50, 0, 6050])
    """

    Sizes = map(lambda x: (x['Width'], x['Deep']), json_data)
    # X - координата ширины, Z - глубины, Y - высоты
    StartPosId = map(lambda x: [x['Position']['X'], x['Position']['Z'], x['Id'], x['Position']['Y']], json_data)
    # Первая и последняя секция имеют внешние стены (1,1,0,1)/(0,1,1,1), остальные - (0,1,0,1)
    out_walls = [(1,1,0,1)] + [(0,1,0,1)]*(len(Sizes)-2) + [(0,1,1,1)]
    return Sizes, StartPosId, out_walls

def json_colomns2params(json_data):
    """
    На входе словарь с Ширина, Глубина, список колонн с координатами центра
    >>> js = {"Width":20, "Deep":20, "Columns":[{"BimType":"column","Deep":0.4,"Height":2.8,"Id":94,"Position":{"X":0.3,"Y":0.6,"Z":0.3},"Width":0.4,"ParentId":4},
    ... {"BimType":"column","Deep":0.4,"Height":2.8,"Id":95,"Position":{"X":6.3,"Y":0.6,"Z":0.3},"Width":0.4,"ParentId":4},
    ... {"BimType":"column","Deep":0.4,"Height":2.8,"Id":96,"Position":{"X":12.3,"Y":0.6,"Z":0.3},"Width":0.4,"ParentId":4},
    ... {"BimType":"column","Deep":0.4,"Height":2.8,"Id":97,"Position":{"X":18.3,"Y":0.6,"Z":0.3},"Width":0.4,"ParentId":4},
    ... {"BimType":"column","Deep":0.4,"Height":2.8,"Id":252,"Position":{"X":85.3,"Y":0.6,"Z":33.3},"Width":0.4,"ParentId":4},
    ... {"BimType":"column","Deep":0.4,"Height":2.8,"Id":253,"Position":{"X":89.3,"Y":0.6,"Z":33.3},"Width":0.4,"ParentId":4}]}
    >>> s1, s2 = json2params(js)
    >>> (s1[0],s2[5])
    ((20, 3),[50, 0, 6050])
    """

    Size = (json_data['Width'], json_data['Deep'])
    # X - координата ширины, Z - глубины, Y - высоты
    # извлекаем сетку колонн,
    grid_columns = map(lambda x: (x["Position"]["X"],x["Position"]["Z"]) , json_data['Columns'])

    return Size, grid_columns