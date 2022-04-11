import pandas as pd
from ensemble_detectors.ensemble_shared_methods import shared_methods

class moving_average_detection:
    def get_average(arr):
        if len(arr)==0:
            print('Empty list passed')
            return 0
        total = 0
        count = 0
        for num in arr:
            total = total + num
            count += 1
        return total/count


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
                average_point_y.append(moving_average_detection.get_average(previous_points))
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
        bound_mult = 3
        bound = (shared_methods.find_threshold(points_y)*bound_mult)

        i = 0
        while i < len(average_points_x):
            if ((points_y[i] < (average_points_y[i]-int(bound))) or (points_y[i] > (average_points_y[i]+int(bound)))):
                detected_ouliters_x.append(points_x[i])
                detected_ouliters_y.append(points_y[i])
            i += 1
            
        return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})


    def detect_average_outliers_labelled_prediction(threshold, average_points, data_points):

        predictions_x = []
        predictions_y = []
        confidence = []
        average_points_x = average_points['points_average_x']
        average_points_y = average_points['points_average_y']
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        bound_mult = 3
        bound = (shared_methods.find_threshold(points_y)*bound_mult)
        i = 0
        while i < len(average_points_x):
            predictions_x.append(points_x[i])
            predictions_y.append(points_y[i])
            if (shared_methods.is_data_outside_bounds(points_y[i], average_points_y[i], int(bound))):
                confidence.append(-1 * shared_methods.calculate_confidence_outlier(points_y[i], average_points_y[i], bound))
            elif (points_y[i] > average_points_y[i]):
                confidence.append(((average_points_y[i]+int(bound)) - points_y[i])/bound)
            else:
                confidence.append((points_y[i] - (average_points_y[i]-int(bound)))/bound)
            i += 1
        
        return pd.DataFrame({'timestamp': predictions_x,'data': predictions_y,'confidence':confidence})


    def real_time_prediction(previous_data_values, next_data_value):
        confidence = 0
        # get last 10 items in previous data
        i = len(previous_data_values)-2
        if (i <= 15):
            return confidence
        temp = []
        while (i > len(previous_data_values)-12):
            temp.append(previous_data_values[i])
            i -= 1
        previous_data_values = temp
        
        # get threshold
        threshold = shared_methods.find_threshold(previous_data_values)

        # get bound
        bound_mult = 3
        bound = (threshold*bound_mult)

        # next data within bounds?
        # calculate confidence
        average = moving_average_detection.get_average(previous_data_values)

        if (shared_methods.is_data_outside_bounds(next_data_value, average, bound)):
            confidence = -1 * shared_methods.calculate_confidence_outlier(next_data_value, average, bound)
        elif (next_data_value > average):
            confidence = (((average+int(bound)) - next_data_value)/bound)
        else:
            confidence = ((next_data_value - (average-int(bound)))/bound)

        # return conf
        return (confidence)