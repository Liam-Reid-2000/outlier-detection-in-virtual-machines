import pandas as pd
import statistics
import numpy as np


def get_median(arr):
    return statistics.median(arr)

def find_threshold(arr):
    return np.std(arr)

def get_moving_median_coordinates(median_interval, data_points):
    
    points_x = data_points['points_x']
    points_y = data_points['points_y']
    
    median_point_y = []
    median_point_x = []

    i = 0
    while (i < (len(points_y))):
        previous_points = []
        j = 0
        while (j < median_interval):
            if (i-j>0):
                previous_points.append(points_y[i-j])
            j += 1
        if len(previous_points)>0:
            median_point_y.append(get_median(previous_points))
            median_point_x.append(points_x[i])
        i = i + 1

    return pd.DataFrame({'points_median_x': median_point_x,'points_median_y': median_point_y})


def detect_median_outliers(threshold, median_points, data_points):

    detected_ouliters_x = []
    detected_ouliters_y = []

    median_points_x = median_points['points_median_x']
    median_points_y = median_points['points_median_y']

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    bound = (find_threshold(points_y))

    i = 0
    while i < len(median_points_x):
        #if ((points_y[i] < median_points_y[i]-int(threshold)) or (points_y[i] > median_points_y[i]+int(threshold))):
        if ((points_y[i] < (median_points_y[i]-int(bound))) or (points_y[i] > (median_points_y[i]+int(bound)))):
            detected_ouliters_x.append(points_x[i])
            detected_ouliters_y.append(points_y[i])
        i += 1
    return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})