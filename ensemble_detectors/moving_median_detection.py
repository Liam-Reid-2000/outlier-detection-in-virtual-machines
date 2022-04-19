import pandas as pd
import statistics
from ensemble_detectors.ensemble_shared_methods import shared_methods

class moving_median_detection:
    """Methods for performing moving median detection"""


    def get_median(arr):
        if len(arr)==0:
            return 0
        return statistics.median(arr)


    def get_moving_median_coordinates(median_interval, data_points):
        """Get coordinates of median points calculated using data window"""
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
                median_point_y.append(moving_median_detection.get_median(previous_points))
                median_point_x.append(points_x[i])
            i = i + 1
        return pd.DataFrame({'points_median_x': median_point_x,'points_median_y': median_point_y})


    def detect_median_outliers(threshold, median_points, data_points):
        """Return coordinates of detected outliers using median detection"""
        detected_ouliters_x = []
        detected_ouliters_y = []
        median_points_x = median_points['points_median_x']
        median_points_y = median_points['points_median_y']
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        bound_mult = 3
        bound = (shared_methods.find_threshold(points_y)*bound_mult)
        i = 0
        while i < len(median_points_x):
            if ((points_y[i] < (median_points_y[i]-int(bound))) or (points_y[i] > (median_points_y[i]+int(bound)))):
                detected_ouliters_x.append(points_x[i])
                detected_ouliters_y.append(points_y[i])
            i += 1
        return pd.DataFrame({'timestamp': detected_ouliters_x,'data': detected_ouliters_y})
    

    def detect_median_outliers_labelled_prediction(threshold, median_points, data_points):
        """Return coordinates and confidence of detected outliers using median detection"""
        predictions_x = []
        predictions_y = []
        confidence = []
        median_points_x = median_points['points_median_x']
        median_points_y = median_points['points_median_y']
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        bound_mult = 3
        bound = (shared_methods.find_threshold(points_y)*bound_mult)
        i = 0
        while i < len(median_points_x):
            predictions_x.append(points_x[i])
            predictions_y.append(points_y[i])
            if (shared_methods.is_data_outside_bounds(points_y[i], median_points_y[i], int(bound))):
                confidence.append(-1 * shared_methods.calculate_confidence_outlier(points_y[i], median_points_y[i], bound))
            elif (points_y[i] > median_points_y[i]):
                confidence.append(((median_points_y[i]+int(bound)) - points_y[i])/bound)
            else:
                confidence.append((points_y[i] - (median_points_y[i]-int(bound)))/bound)
            i += 1
        return pd.DataFrame({'timestamp': predictions_x,'data': predictions_y,'confidence':confidence})
    

    def real_time_prediction(previous_data_values, next_data_value):
        """Return confidence of next outlier using moving median detection"""
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
        median = moving_median_detection.get_median(previous_data_values)
        if (shared_methods.is_data_outside_bounds(next_data_value, median, bound)):
            confidence = -1 * shared_methods.calculate_confidence_outlier(next_data_value, median, bound)
        elif (next_data_value > median):
            confidence = (((median+int(bound)) - next_data_value)/bound)
        else:
            confidence = ((next_data_value - (median-int(bound)))/bound)
        # return conf
        return (confidence)