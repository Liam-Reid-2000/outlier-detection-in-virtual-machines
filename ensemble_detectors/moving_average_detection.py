import pandas as pd
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

    bound_mult = 2.5
    bound = (find_threshold(points_y)*bound_mult)

    i = 0
    while i < len(average_points_x):
        if ((points_y[i] < (average_points_y[i]-int(bound))) or (points_y[i] > (average_points_y[i]+int(bound)))):
            detected_ouliters_x.append(points_x[i])
            detected_ouliters_y.append(points_y[i])
        i += 1
        
    return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})



def is_data_outside_bounds(data_y, average_point, bound):
    if ((data_y < average_point-bound) or (data_y > average_point+bound)):
        return True
    return False


def calculate_confidence_outlier(data_y, average_point, bound):
    distance_to_threshold = 0
    if (data_y > average_point+bound):
        distance_to_threshold = abs(data_y - (average_point+bound))
    else:
        distance_to_threshold = abs(data_y - (average_point-bound))
    confidence = distance_to_threshold/bound
    if confidence > 1:
        return 1
    return confidence



def detect_average_outliers_labelled_prediction(threshold, average_points, data_points):

    predictions_x = []
    predictions_y = []
    confidence = []

    average_points_x = average_points['points_average_x']
    average_points_y = average_points['points_average_y']

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    bound_mult = 2.5
    bound = (find_threshold(points_y)*bound_mult)

    i = 0
    while i < len(average_points_x):
        predictions_x.append(points_x[i])
        predictions_y.append(points_y[i])
        if (is_data_outside_bounds(points_y[i], average_points_y[i], int(bound))):
            confidence.append(-1 * calculate_confidence_outlier(points_y[i], average_points_y[i], bound))
        elif (points_y[i] > average_points_y[i]):
            confidence.append(((average_points_y[i]+int(bound)) - points_y[i])/bound)
        else:
            confidence.append((points_y[i] - (average_points_y[i]-int(bound)))/bound)
        i += 1
        
    return pd.DataFrame({'timestamp': predictions_x,'data': predictions_y,'confidence':confidence})