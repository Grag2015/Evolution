

def pl2json(list_pl, compartments, posx_ls, posy_ls, id_ls):

    """
    >>> compartments = ["envelope",  "hall", "corr", "bath", "kitchen", "room", "room2"]
    >>> tt=[[0.0,1.3636363636363635,0.0,3.1818181818181817,1.3636363636363635,2.2727272727272729,2.2727272727272729,3.1818181818181817,0.0,3.1818181818181817,3.1818181818181817,5.0],
    ... [0.0,2.3999999999999999,2.3999999999999999,4.7999999999999998,0.0,2.3999999999999999,0.0,2.3999999999999999,4.7999999999999998,6.0,0.0,6.0]]
    >>> ss=pl2json(tt, compartments)
    >>> (ss['BimType'], ss['rooms'][0]['Deep'], ss['rooms'][0]['Position']['X'])
    ('functionalzone', 2.4, 1.36)
    """
    newres = []
    for pl, id in list_pl, id_ls:
        locd = {}
        locd_room = []

        for t in range(len(pl[0]) / 2):
            deep = round(pl[1][2 * t + 1] - pl[1][2 * t], 2)
            width = round(pl[0][2 * t + 1] - pl[0][2 * t], 2)
            locd_room.append({"BimType": "room", 'name': compartments[t + 1], "Deep": deep, "Width": width,
                              "Position": {"X": posx_ls[t] + width, "Y": posy_ls[t] + deep}})

        locd["BimType"] = "functionalzone"
        locd["Id"] = id_ls[id]
        locd["rooms"] = locd_room
        newres.append(locd)
    return newres

