from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import cross_validate
from sklearn.datasets import load_digits
from sklearn.feature_selection import RFE
import data
import time
import copy
import csv
import matplotlib.pyplot as plt

NUM_TRIALS = 1000

inputs, labels = data.get_shuffled()
headers = list(range(1,55))
headers_history = []

rank_history = {}
for i in range(1, 55):
    rank_history[i] = 0

def getColumns():
    return len(inputs[0])

def getAccuracy(X,y):
    clf = svm.SVC()
    cv_results = cross_validate(clf, X, y, cv=5)
    results = data.assess_results(cv_results)
    average_accuracy = sum(cv_results['test_score'])/len(cv_results['test_score'])
    return average_accuracy

def getWorstColumn(X,y):
    svc = SVC(kernel="linear", C=1)
    rfe = RFE(estimator=svc, n_features_to_select=getColumns()-1, step=1)
    rfe.fit(X, y)
    support = list(rfe.support_)
    #return worst
    for i in range(len(support)):
        if not support[i]:
            return i

def removeColumn(X,col):
    q_num = headers.pop(col)
    rank_history[q_num] += len(headers)
    for r in range(len(X)):
        X[r].pop(col)
    return q_num

def trial():
    results = []
    x_axis = []
    y_axis = []
    while getColumns() > 1:
        worst_column = getWorstColumn(inputs,labels)
        removeColumn(inputs, worst_column)
        accuracy = getAccuracy(inputs,labels)
        point = (getColumns(),accuracy)
        x_axis.append(point[0])
        y_axis.append(point[1])
        headers_history.append(headers[:])
        #print(headers,len(headers))
        #print(point)
        results.append(point)
    rank_history[headers[0]] += 1
    return results

family = dict()
for t in range(NUM_TRIALS):
    print("Trial",t)
    results = trial()
    for point in results:
        x = point[0]
        y = point[1]
        if x not in family:
            family[x] = []
        family[x].append(y)
    #regenerate
    inputs, labels = data.get_shuffled()
    headers = list(range(1,55))


## nums qs
x_axis = []
y_axis = []
for key,values in family.items():
    x_axis.append(key)
    average = sum(values)/len(values)
    y_axis.append(average)

with open('numQs_vs_accuracy.csv', mode='w') as results_file:
    writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in range(len(x_axis)):
        x = x_axis[i]
        y = y_axis[i]*100
        writer.writerow([x,y])


## ranking
ranking = []
for i in range(1, 55):
    ranking.append((rank_history[i]/NUM_TRIALS, i))
ranking.sort()

with open('average_rank_of_qs.csv', mode='w') as results_file:
    writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for el in ranking:
        print(el)
        x = el[1]
        y = el[0]
        writer.writerow([x,y])

plt.plot(x_axis,y_axis)
plt.show()
