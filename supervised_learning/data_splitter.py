import csv
import datetime
import json
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest


all_points_x = []
all_points_y = []

train_points_x = []
train_points_y = []

test_points_x = []
test_points_y = []

def load_data(csv_file_name, split_ratio):
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        if (split_ratio <= 0 or split_ratio >= 1):
            print('Error: Split ratio must be greater than 0 and less than 1')
        else:
            i = 0
            for row in lines:
                try:
                    all_points_y.append(float(row[1]))
                    all_points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    print("Error loading data")
                i += 1

            no_data_points = i
            train_test_point = split_ratio * no_data_points

            i = 0
            while (i < int(train_test_point)):
                train_points_x.append(all_points_x[i])
                train_points_y.append(all_points_y[i])
                i+=1
            
            i = int(train_test_point)
            while (i < len(all_points_x)):
                test_points_x.append(all_points_x[i])
                test_points_y.append(all_points_y[i])
                i+=1

### SPLIT THE OUTLIER DATA AND LABEL ###

train_outliers = []
test_outliers = []

all_outliers = []

def split_outliers(target_data, split_date):
    f = open(target_data)
    data = json.load(f)
    for i in data['realTraffic/speed_7578.csv']:
        if (datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') < split_date):
            train_outliers.append(i)
        else:
            test_outliers.append(i)
        all_outliers.append(i)


def pair_outliers():
    outlier_y = []
    i = 0
    while (i < len(all_points_x)):
        for j in all_outliers:
            if (str(j) == str(all_points_x[i])):
                outlier_y.append(all_points_y[i])
        i+=1
    return pd.DataFrame({'timestamp': all_outliers,'data': outlier_y})


labels = []
def label_data():
    for i in all_points_x:
        label = 0
        for j in all_outliers:
            if (str(i) == j):
                label = 1
        labels.append(label)
    
    return pd.DataFrame({'timestamp': all_points_x,'data': all_points_y,'label':labels})



load_data('resources/speed_7578.csv', 0.5)
split_outliers('resources/combined_labels.json',test_points_x[0])
mydata = label_data()


import matplotlib.pyplot as plt
from datetime import *

points_x_as_minute_of_day = []
i = 0
while (i < len(all_points_x)):
    time = all_points_x[i]
    points_x_as_minute_of_day.append(time.hour * 60 + time.minute)
    i+=1

plt.scatter(points_x_as_minute_of_day, all_points_y)
plt.title('plot')
plt.xlabel('x')
plt.ylabel('y')

#plt.show()

pair_outliers()

def get_x_train_data():
    train_points_x_as_minutes = []
    for i in train_points_x:
        train_points_x_as_minutes.append(i.hour * 60 + i.minute)
    return(np.r_['1,2,0', train_points_x_as_minutes, train_points_y])

def get_x_test_data():
    test_points_x_as_minutes = []
    for i in test_points_x:
        test_points_x_as_minutes.append(i.hour * 60 + i.minute)
    return(np.r_['1,2,0', test_points_x_as_minutes, test_points_y])

def get_outliers():
    outlier_points_x_as_minutes = []
    df = pair_outliers()
    for i in df['timestamp']:
        time = datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
        outlier_points_x_as_minutes.append(time.hour * 60 + time.minute)
    return(np.r_['1,2,0', outlier_points_x_as_minutes, df['data']])

rng = np.random.RandomState(42)
X_train = get_x_train_data()
X_test = get_x_test_data()
X_outliers = get_outliers()

# fit the model
clf = IsolationForest(max_samples=100, random_state=rng)
clf.fit(X_train)
y_pred_test = clf.predict(X_test)
y_pred_outliers = clf.predict(X_outliers)


new_data_to_predict_x = []
new_data_to_predict_y = []

new_data_to_predict_x.append(700)
new_data_to_predict_y.append(0)
to_predict = np.r_['1,2,0', new_data_to_predict_x, new_data_to_predict_y]

print(clf.predict(to_predict))

print(y_pred_outliers)

# plot the line, the samples, and the nearest vectors to the plane
xx, yy = np.meshgrid(np.linspace(0,1440, 50), np.linspace(0, 100, 50))
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.title("IsolationForest")
plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c="white", s=20, edgecolor="k")
b2 = plt.scatter(X_test[:, 0], X_test[:, 1], c="green", s=20, edgecolor="k")
c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c="red", s=20, edgecolor="k")
plt.axis("tight")
plt.xlim((0, 1440))
plt.ylim((0, 100))
plt.legend(
    [b1, b2, c],
    ["training observations", "new regular observations", "new abnormal observations"],
    loc="upper left",
)
plt.show()