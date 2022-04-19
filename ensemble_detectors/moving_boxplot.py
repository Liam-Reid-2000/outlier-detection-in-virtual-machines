from this import s
import numpy as np
import pandas as pd

from app_helper_scripts.app_exceptions import InvalidValueForCalculationError
from ensemble_detectors.ensemble_shared_methods import shared_methods

class moving_boxplot_detection:
    """Methods for performing moving boxplot detection"""

    
    def calculate_lower_bound(q1, iqr, threshold):
        """Returns lower bound. Calculating from lower quartile, iqr and threshold. Returns 0 if negative."""
        if (int(iqr)<=0 or int(threshold) <=0):
            raise InvalidValueForCalculationError([iqr, threshold])
        if (q1 - iqr*float(threshold) > 0):
            return q1 - iqr*float(threshold)
        return 0

    
    def detect_boxplot_outliers(threshold, boxplot_dataset_size, data_points):
        """Return coordinates of outliers detecting using boxplot detecion"""
        outliers_x = []
        outliers_y = []
        if (int(threshold)<=0 or int(boxplot_dataset_size)<=0):
            print('Invalid parameters passed')
            return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y}) 
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        i = 0
        if (i >= len(points_x) - boxplot_dataset_size):
            boxplot_dataset_size = int(len(points_x)/3)

        while (i<len(points_x) - boxplot_dataset_size):
            subset_data = shared_methods.create_subset_dataframe(data_points, boxplot_dataset_size, i)
            #find quartile values and interquartile range
            #define array of data
            dataArr = np.array(subset_data['data'])
            #calculate interquartile range 
            q3, q1 = np.percentile(dataArr, [75 ,25])
            iqr = q3 - q1

            #calculate class boundaries
            lower_bound = moving_boxplot_detection.calculate_lower_bound(q1, iqr, threshold)
            upper_bound = q3 + iqr*float(threshold)

            #is next data item an outlier?
            data_point = points_y[i + boxplot_dataset_size]
            if ((data_point < lower_bound) or (data_point > upper_bound)):
                outliers_x.append(points_x[i + boxplot_dataset_size])
                outliers_y.append(points_y[i + boxplot_dataset_size])
            i = i + 1
        return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})


    def calculate_confidence(next_data_value, lower_bound, upper_bound, q1, q3):
        """Calculated and returns ratio of distance from thresholds (confidence)"""
        if (next_data_value < lower_bound):
            distance_to_threshold = lower_bound - next_data_value
            conf = distance_to_threshold/lower_bound
            if (conf > 1):
                conf = 1
            return (-1 * conf)
        elif (next_data_value > upper_bound):
            distance_to_threshold = next_data_value - upper_bound
            conf = distance_to_threshold/upper_bound
            if (conf > 1):
                conf = 1
            return (-1 * conf) 
        elif (next_data_value > q3):
            distance_to_threshold = next_data_value - q3
            return (distance_to_threshold/upper_bound)
        elif (next_data_value < q1):
            distance_to_threshold = q1 - next_data_value
            return (distance_to_threshold/lower_bound)
        else:
            return (1)


    def detect_boxplot_outliers_predictions_confidence(threshold, boxplot_dataset_size, data_points):    
        """Return coordinates and confidence of outliers detecting using boxplot detecion"""
        predictions_x = []
        predictions_y = []
        confidence = []
        if (int(threshold)<0 or int(boxplot_dataset_size)<0):
            print('invalid parameters passed')
            return []
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        i = 0
        if (i >= len(points_x) - boxplot_dataset_size):
            boxplot_dataset_size = int(len(points_x)/3)
        while (i<len(points_x) - boxplot_dataset_size):
            subset_data = shared_methods.create_subset_dataframe(data_points, boxplot_dataset_size, i)
            #find quartile values and interquartile range
            #define array of data
            dataArr = np.array(subset_data['data'])
            #calculate interquartile range 
            q3, q1 = np.percentile(dataArr, [75 ,25])
            iqr = q3 - q1
            lower_bound = moving_boxplot_detection.calculate_lower_bound(q1, iqr, threshold)
            upper_bound = q3 + iqr*float(threshold)
            # confidence of next prediction
            data_point = points_y[i + boxplot_dataset_size]
            data_point_x = points_x[i + boxplot_dataset_size]
            predictions_x.append(data_point_x)
            predictions_y.append(data_point)
            confidence.append(moving_boxplot_detection.calculate_confidence(data_point, lower_bound, upper_bound, q1, q3))
            i += 1
        return pd.DataFrame({'timestamp': predictions_x,'data': predictions_y,'confidence':confidence})


    def real_time_prediction(previous_data_values, next_data_value):
        """Return confidence of next data value using moving boxplot"""
        confidence = 0
        threshold = 5
        # get last 10 items in previous data
        i = len(previous_data_values)-2
        if (i <= 15):
            return confidence
        temp = []
        while (i > len(previous_data_values)-12):
            temp.append(previous_data_values[i])
            i -= 1
        previous_data_values = temp
        #define array of data
        dataArr = np.array(previous_data_values)
        #calculate interquartile range 
        q3, q1 = np.percentile(dataArr, [75 ,25])
        iqr = q3 - q1
        #calculate boundaries
        lower_bound = moving_boxplot_detection.calculate_lower_bound(q1, iqr, threshold)
        upper_bound = q3 + iqr*float(threshold)
        return moving_boxplot_detection.calculate_confidence(next_data_value, lower_bound, upper_bound, q1, q3)