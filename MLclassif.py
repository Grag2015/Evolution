
# подготовка данных
files_list = ["1_0100", "2_0100"]
plall_total
for fl in files_list:
    file = open("d:\YandexDisk\EnkiSoft\Evolution\plall" + fl + ".txt", "rb")
    plall_tmp = cPickle.load(file)
    plall_total += plall_tmp
outwalls = [x[1] for x in plall_total]
size = [(x[3],x[4]) for x in plall_total]
funs = []
for x in plall_total:
    if x[6]<=1:
        funs += 1
    else:
        if x[6]<=2:
            funs += 2
        else:
            if x[6] <= 3:
                funs += 3
            else:
                funs += 4
data = pd.DataFrame([outwalls,size,funs],columns=["outwalls","size","funs"])

pd.pivot_table(df, values='D', index=['B'], columns=['A', 'C'], aggfunc=np.sum)