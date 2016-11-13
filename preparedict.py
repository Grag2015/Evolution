import pandas as pd
import cPickle
import numpy as np
import time

# подготовка данных
# список файлов для загрузки
files_list = ["1_0001","1_0010", "1_0011", "1_0100", "1_0101", "1_0110", "1_0111", "2_0001", "2_0010", "2_0011", "2_0100",
              "2_0101", "2_0110", "2_0111", "3_0001", "3_0010", "3_0011", "3_0100"]
plall_total = []
for fl in files_list:
    file = open("d:\YandexDisk\EnkiSoft\Evolution\plall" + fl + ".txt", "rb")
    plall_tmp = cPickle.load(file)
    print len(plall_tmp)
    plall_total += plall_tmp
outwalls = [x[1] for x in plall_total]
size = [(x[3],x[4]) for x in plall_total]
funs = [x[6] for x in plall_total]
pls = [x[5][0] for x in plall_total]
hall_pos_dict = {(9,9):0, (9,8):1}
hall_pos = [hall_pos_dict[x[0][0][1][0]] for x in plall_total]


data = pd.DataFrame(data=zip(outwalls,size,hall_pos, funs,pls),columns=["outwalls","size","hall_pos","funs","pls"])

grouped = data[["outwalls","size","hall_pos","funs"]].groupby(["outwalls","size","hall_pos"], as_index=False)
data_agg = grouped.aggregate(np.min)

dict_res={}
for i in range(len(data_agg)):
    dict_res[(data_agg.ix[i,1],data_agg.ix[i,0],data_agg.ix[i,2])] = data[(data["outwalls"] == data_agg.ix[i,0]) &
                                                                          (data["size"] == data_agg.ix[i,1]) &
                                                                          (data["funs"] == data_agg.ix[i,3]) &
                                                                          (data["hall_pos"] == data_agg.ix[i,2])].reset_index().ix[0,5]

# проверка времени обращения к словарю
t1 = time.time()
dict_res[((4.5, 6.0), (0, 0, 0, 1), 0)] # нет варианта для hall_pos = 1
pl=dict_res[((8.5, 6.0), (0, 1, 0, 1), 1)]
t2 = time.time()
t2-t1

file = open("d:\YandexDisk\EnkiSoft\Evolution\dict_res.txt", 'wb')
cPickle.dump(dict_res, file)
file.close()
