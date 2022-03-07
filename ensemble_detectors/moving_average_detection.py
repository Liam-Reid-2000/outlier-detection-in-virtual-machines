import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_average(arr):
    total = 0
    count = 0
    for num in arr:
        total = total + num
        count += 1
    return total/count

def find_threshold(arr):
    return np.std(arr)

def get_moving_average_coordinates(average_interval, data_points):
    
    points_x = data_points['points_x']
    points_y = data_points['points_y']
    
    average_point_y = []
    average_point_x = []

    i = 0
    while (i < (len(points_y))):
        previous_points = []
        j = 0
        while (j < average_interval):
            if (i-j>0):
                previous_points.append(points_y[i-j])
            j += 1
        if len(previous_points)>0:
            average_point_y.append(get_average(previous_points))
            average_point_x.append(points_x[i])
        i = i + 1
    

    return pd.DataFrame({'points_average_x': average_point_x,'points_average_y': average_point_y})


def detect_average_outliers(threshold, average_points, data_points):
    detected_ouliters_x = []
    detected_ouliters_y = []

    average_points_x = average_points['points_average_x']
    average_points_y = average_points['points_average_y']

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    bound_mult = 1.5
    bound = (find_threshold(points_y)*bound_mult)

    i = 0
    while i < len(average_points_x):
        if ((points_y[i] < (average_points_y[i]-int(bound))) or (points_y[i] > (average_points_y[i]+int(bound)))):
            detected_ouliters_x.append(points_x[i])
            detected_ouliters_y.append(points_y[i])
        i += 1
        
    return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})