import pandas as pd
import cPickle
import numpy as np

# подготовка данных
# список файлов для загрузки
files_list = ["1_0001","1_0010", "1_0100", "1_0110", "2_0001", "2_0010", "2_0100", "3_0001", "3_0100"]
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

data = pd.DataFrame(data=zip(outwalls,size,funs,pls),columns=["outwalls","size","funs","pls"])

grouped = data[["outwalls","size","funs"]].groupby(["outwalls","size"], as_index=False)
data_agg = grouped.aggregate(np.min)

dict_res={}
for i in range(len(data_agg)):
    dict_res[(data_agg.ix[i,1],data_agg.ix[i,0])] = data[(data["outwalls"] == data_agg.ix[i,0]) & (data["size"] == data_agg.ix[i,1]) & (data["funs"] == data_agg.ix[i,2])].ix[0,3]


