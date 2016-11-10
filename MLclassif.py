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
funs = []
# разбиваем количество нарушенных ограничений на классы
for x in plall_total:
    if x[6]<=1:
        funs += [1]
    else:
        if x[6]<=2:
            funs += [2]
        else:
            if x[6] <= 3:
                funs += [3]
            else:
                funs += [4]
data = pd.DataFrame(data=zip(outwalls,size,funs),columns=["outwalls","size","funs"])

grouped = data.groupby(["outwalls","size"], as_index=False)
data_agg = grouped.aggregate(np.min)

# разбить тюплы "outwalls","size" по отдельным колонкам
outw0 = [x[0] for x in data_agg["outwalls"]]
outw1 = [x[1] for x in data_agg["outwalls"]]
outw2 = [x[2] for x in data_agg["outwalls"]]
outw3 = [x[3] for x in data_agg["outwalls"]]
sizeb = [x[0] for x in data_agg["size"]]
sizeh = [x[1] for x in data_agg["size"]]

# данные для обучения
# outw0 - не берем
X = np.array(pd.DataFrame(data=zip(outw1,outw2,outw3,sizeb,sizeh),columns=['outw1','outw2','outw3','sizeb','sizeh']))
y = np.array(pd.DataFrame(data=data_agg["funs"], columns=["funs"]))
y = y.reshape(y.shape[0],)

from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 11)

from sklearn.svm import SVC
svc = SVC()
svc.fit(X_train, y_train)
err_train = np.mean(y_train != svc.predict(X_train))
err_test  = np.mean(y_test  != svc.predict(X_test))
print err_train, err_test

# Радиальное ядро
# Вначале попробуем найти лучшие значения параметров для радиального ядра.
from sklearn.grid_search import GridSearchCV
C_array = np.logspace(-3, 3, num=7)
gamma_array = np.logspace(-5, 2, num=8)
svc = SVC(kernel='rbf')
grid = GridSearchCV(svc, param_grid={'C': C_array, 'gamma': gamma_array})
grid.fit(X_train, y_train)
print 'CV error    = ', 1 - grid.best_score_
print 'best C      = ', grid.best_estimator_.C
print 'best gamma  = ', grid.best_estimator_.gamma

C_array = np.logspace(-3, 3, num=7)
svc = SVC(kernel='linear')
grid = GridSearchCV(svc, param_grid={'C': C_array})
grid.fit(X_train, y_train)
print 'CV error    = ', 1 - grid.best_score_
print 'best C      = ', grid.best_estimator_.C

C_array = np.logspace(-5, 2, num=8)
gamma_array = np.logspace(-5, 2, num=8)
degree_array = [2, 3, 4]
svc = SVC(kernel='poly')
grid = GridSearchCV(svc, param_grid={'C': C_array, 'gamma': gamma_array, 'degree': degree_array})
grid.fit(X_train, y_train)
print 'CV error    = ', 1 - grid.best_score_
print 'best C      = ', grid.best_estimator_.C
print 'best gamma  = ', grid.best_estimator_.gamma
print 'best degree = ', grid.best_estimator_.degree