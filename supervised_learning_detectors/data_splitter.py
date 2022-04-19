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


def convert_time_data_to_minutes_of_day(points_x):
    points_x_as_minutes = []
    for i in points_x:
        points_x_as_minutes.append(i.hour * 60 + i.minute)
    return points_x_as_minutes



def get_data_as_matrix(points_x, points_y):
    return(np.r_['1,2,0', points_x, points_y])



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