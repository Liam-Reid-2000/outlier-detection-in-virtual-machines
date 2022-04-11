import datetime
import json
import pandas as pd
from datetime import *
import numpy as np

def load_data(dataset, split_ratio):
    
    all_points_x = []
    all_points_y = []

    j = 0
    while j < len(dataset['timestamp']):
        all_points_y.append(dataset['data'][j])
        all_points_x.append(dataset['timestamp'][j])
        j += 1

    no_data_points = len(dataset)
    train_test_point = split_ratio * no_data_points

    train_points_x = []
    train_points_y = []

    test_points_x = []
    test_points_y = []

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

    split_data = []
    split_data.append(all_points_x)
    split_data.append(all_points_x)
    split_data.append(train_points_x)
    split_data.append(train_points_y)
    split_data.append(test_points_x)
    split_data.append(test_points_y)

    return split_data



def split_outliers(target_data, split_date):

    train_outliers = []
    test_outliers = []

    all_outliers = []

    f = open('resources/combined_labels.json')
    data = json.load(f)
    for i in data[target_data]:
        if (datetime.strptime(i, '%Y-%m-%d %H:%M:%S') < split_date):
            train_outliers.append(i)
        else:
            test_outliers.append(i)
        all_outliers.append(i)
    outlier_data = []
    outlier_data.append(all_outliers)
    outlier_data.append(train_outliers)
    outlier_data.append(test_outliers)
    f.close()
    return outlier_data


def pair_outliers(test_points_x, test_points_y, all_outliers):
    outlier_y = []
    i = 0
    while (i < len(test_points_x)):
        for j in all_outliers:
            if (str(j) == str(test_points_x[i])):
                outlier_y.append(test_points_y[i])
        i+=1
    return pd.DataFrame({'timestamp': all_outliers,'data': outlier_y})



def convert_time_data_to_minutes_of_day(points_x):
    points_x_as_minutes = []
    for i in points_x:
        points_x_as_minutes.append(i.hour * 60 + i.minute)
    return points_x_as_minutes



def get_data_as_matrix(points_x, points_y):
    return(np.r_['1,2,0', points_x, points_y])

    

def get_outliers(test_points_x, test_points_y, test_outliers):
    outlier_points_x = []
    df = pair_outliers(test_points_x, test_points_y, test_outliers)
    for i in df['timestamp']:
        time = datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
        outlier_points_x.append(time)
    return(np.r_['1,2,0', outlier_points_x, df['data']])


def get_outlier_areas(outliers_x, target_data):
    f = open('resources/combined_windows.json')
    data = json.load(f)
    arrX1 = []
    arrX2 = []
    for i in data[target_data]:
        x1 = datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
        x2 = datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f')
        for j in outliers_x:
            j = datetime.strptime(j, '%Y-%m-%d %H:%M:%S')
            if (j > x1 and j < x2):
                arrX1.append(x1)
                arrX2.append(x2)
    f.close()
    return pd.DataFrame({'first_x': arrX1, 'second_x': arrX2})


def remove_outliers_from_training_data(train_outliers, train_points_x, train_points_y):
    data_without_outliers_x = []
    data_without_outliers_y = []

    k = 0
    for i in train_points_x:
        for j in train_outliers:
            if (str(i) != j):
                data_without_outliers_x.append(i)
                data_without_outliers_y.append(train_points_y[k])
            else:
                print('Outlier removed')
        k += 1
    
    return pd.DataFrame({'timestamp':data_without_outliers_x,'data':data_without_outliers_y})