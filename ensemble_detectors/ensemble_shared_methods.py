import numpy as np

class shared_methods:
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

    def find_threshold(arr):
        if (len(arr)==0):
            print('No data in list passed')
            return 0
        return np.std(arr)
