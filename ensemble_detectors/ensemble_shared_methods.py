import numpy as np
import pandas as pd

class shared_methods:
    """Methods shared among ensemble detectors"""

    def is_data_outside_bounds(data_y, average_point, bound):
        if ((data_y < average_point-bound) or (data_y > average_point+bound)):
            return True
        return False


    def calculate_confidence_outlier(data_y, average_point, bound):
        """Calculates distance of outlier to threshold (confidence)"""
        distance_to_threshold = 0
        if (data_y > average_point+bound):
            distance_to_threshold = abs(data_y - (average_point+bound))
        else:
            distance_to_threshold = abs(data_y - (average_point-bound))
        confidence = distance_to_threshold/bound
        if confidence > 1:
            return 1
        return confidence


    def find_threshold(arr):
        """Calculates threshold based on standard devaited of values passed."""
        if (len(arr)==0):
            return 0
        return np.std(arr)

    
    def create_subset_dataframe(data_points, boxplot_dataset_size, i):
        """Returns a dataframe representing a window of data"""
        subset_x = []
        subset_y = []
        j = i
        while (j < i + boxplot_dataset_size):
            subset_x.append(data_points['points_x'][j])
            subset_y.append(data_points['points_y'][j])
            j+=1
        return pd.DataFrame({'timestamp': subset_x, 'data': subset_y})
