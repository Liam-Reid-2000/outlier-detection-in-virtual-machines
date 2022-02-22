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
    while (i < (len(points_y)-average_interval)):
        previous_five_y = []
        j = 0
        while (j < average_interval):
            previous_five_y.append(points_y[i+j])
            j += 1
        average_point_y.append(get_average(previous_five_y))
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

    bound = (find_threshold(points_y))

    i = 0
    while i < len(average_points_x):
        #if ((points_y[i] < (average_points_y[i]-int(threshold))) or (points_y[i] > (average_points_y[i]+int(threshold)))):
        if ((points_y[i] < (average_points_y[i]-int(bound))) or (points_y[i] > (average_points_y[i]+int(bound)))):
            print('---------------------------------------------')
            print('This comparison')
            print('point x = ' + str(points_x[i]))
            print('point_y = ' + str(points_y[i]))
            print('std = ' + str(bound))
            print('average point y = ' + str(average_points_y[i]))
            print('average point x = ' + str(average_points_x[i]))
            print('upper bound = ' + str(average_points_y[i] + bound))
            print('lower bound = ' + str(average_points_y[i] - bound))


            print('This comparison')
            print('---------------------------------------------')
            detected_ouliters_x.append(points_x[i])
            detected_ouliters_y.append(points_y[i])
        i += 1
    
    ##########################################################################################
    ##########################################################################################
    plt.plot(points_x,points_y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title("A simple line graph")
    plt.plot(average_points_x, average_points_y)

    bound = (find_threshold(points_y))

    new_point_y = []
    for i in average_points_y:
        new_point_y.append(i + bound)
    plt.plot(average_points_x, new_point_y)
    
    
    new_point_y = []
    for i in average_points_y:
        new_point_y.append(i - bound)
    plt.plot(average_points_x, new_point_y)
    
    plt.scatter(detected_ouliters_x, detected_ouliters_y, color='red')

    #plt.show()
    ##########################################################################################
    ##########################################################################################

    return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})