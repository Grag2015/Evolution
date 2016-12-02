# -*- coding: utf-8 -*-
# Найденные планировки в JSON
import json
# преобразует список планировок КВАРТИР в список словарей, который конвертится в json
def pl2json(pl, addshift = (0,0,0,0)):

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
    compartments = ["envelope", "staircase", "lift", "toilet", "shaft", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office"
        , "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office"
        , "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office"
        , "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office", "office"]
    newres = []
    locd = {}
    locd_room = []

    for t in range(len(pl[0]) / 2):
        deep = round(pl[1][2 * t + 1] - pl[1][2 * t], 2)
        width = round(pl[0][2 * t + 1] - pl[0][2 * t], 2)
        locd_room.append({"BimType": "functionalzone", 'name': compartments[t + 1], "Deep": deep, "Width": width,
                          "Position": {"X": round(pl[0][2 * t] + addshift[0],2), "Z": round(pl[1][2 * t] + addshift[1],2),
                             "Y": addshift[2]}})

    locd["BimType"] = "section"
    locd["Position"] = {"X": 0, "Z": 0, "Y": 0}
    locd["ParentId"] = addshift[3]
    locd["functionalzones"] = locd_room
    return locd #json.dumps(newres)


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