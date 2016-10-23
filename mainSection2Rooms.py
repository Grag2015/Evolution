from Section2Flats import Section2Flats

def Section2Rooms(n, B_, H_):
    scens, flats = Section2Flats(n, B_, H_)
    prepflats = prepareflats(scens, flats)

    res=[]
    for fl in prepflats:
        res.append([(fl[0],fl[1]), Flat2Rooms(fl[2], fl[3], fl[4], fl[5], fl[6])])

    # visualization
    for rs in res:
        globplac = [list(np.array(rs[1][0]) + x1), list(np.array(rs[1][1]) + y1)]
        visual()

def prepareflats(scen, flats):
    # output - x1,y1, H,B, entrwall, hall_pos, count_rooms
    prepflats = []
    for i in range(3, len(scen)):
        x1 = flats[0][i*2]
        y1 = flats[1][i*2]
        H = flats[0][i*2+1] - flats[0][i*2]
        B = flats[0][i*2+1] - flats[0][i*2]
        hall_pos, entrwall = entrwall_hall_pos(scen[2,i], scen[1,i])
        if B*H<44:
            count_rooms = 1
        else:
            if B*H<60:
                count_rooms = 2
            else:
                if B*H<90:
                    count_rooms = 3
                else:
                    count_rooms = 4
        prepflats.append((x1, y1, B, H, entrwall, hall_pos, count_rooms))
    return prepflats


def entrwall_hall_pos(corr_flat, podezd_flat):
    # пример входных данных - [(2, 11)], [(0, 3)]
    noCorridEntr={(0, 10), (0, 3), (1, 11), (0, 11), (0, 4), (0, 0), (9, 0), (0, 12), (11, 0), (0, 5), (0, 8), (0, 1), (0, 6),
     (0, 9), (0, 7), (0, 2)}
    if set(corr_flat) in noCorridEntr:
        tmp = podezd_flat
    else:
        tmp = corr_flat

    dct = {(1, 3): (0, (0,0)),
            (1, 2): (0, (0,0)),
            (1, 5): (0, (0,1)),
            (1, 10): (0, (0,1)),
            (3, 11): (0, (1,0)),
            (5, 11): (0, (1,0)),
            (2, 11): (0, (1,0)),
            (10, 11): (0, (1,1)),
            (11, 10): (0, (2,0)),
            (11, 5): (0, (2,0)),
            (11, 2): (0, (2,1)),
            (11, 3): (0, (2,1)),
            (5, 1): (0, (3,0)),
            (10, 1): (0, (3,0)),
            (3, 1): (0, (3,1)),
            (2, 1): (0, (3,1)),
            (1, 6): (2, (0,0)),
            (1, 9): (2, (0,0)),
            (1, 8): (2, (0,0)),
            (1, 7): (2, (0,0)),
            (7, 11): (2, (1,0)),
            (6, 11): (2, (1,0)),
            (8, 11): (2, (1,0)),
            (9, 11): (2, (1,0)),
            (11, 6): (2, (2,0)),
            (11, 9): (2, (2,0)),
            (11, 7): (2, (2,0)),
            (11, 8): (2, (2,0)),
            (8, 1): (2, (3,0)),
            (7, 1): (2, (3,0)),
            (6, 1): (2, (3,0)),
            (9, 1): (2, (3,0)),
            (4, 1): (1, (3,1)),
            (11, 4): (1, (2,1)),
            (1, 4): (1, (0,0)),
            (4, 11): (1, (1,0))}
    return dct[tmp[0]]
