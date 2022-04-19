import matplotlib.pyplot as plt
import pandas as pd

from ensemble_detectors.ensemble_shared_methods import shared_methods

class moving_histogram_detection:
    """Methods for performing moving histogram"""

    def get_histogram(subset_y):
        """Return histogram data"""
        plt.hist(subset_y)
        ax = plt.gca()
        return ax.patches


    def get_outlier_ranges(heights, x_left_corners, bin_widths, threshold):
        """Return outlier ranges"""
        outlier_ranges = []
        i = 0
        while i < len(heights):
            outlier = False
            if (heights[i] < int(threshold)):
                outlier = True
                if ((outlier) and (i >= 1)):
                    if (heights[i-1] >= int(threshold)):
                        outlier = False
                if ((outlier) and (i < len(heights)-1)):
                    if (heights[i+1] >= int(threshold)):
                        outlier = False
                if ((outlier) and (i >= 2)):
                    if (heights[i-2] >= int(threshold)):
                        outlier = False
                if ((outlier) and (i < len(heights)-2)):
                    if (heights[i+2] >= int(threshold)):
                        outlier = False
                if outlier:
                    outlier_range = []
                    outlier_range.append(x_left_corners[i])
                    outlier_range.append(x_left_corners[i] + bin_widths[i])
                    outlier_ranges.append(outlier_range)
            i += 1
        return outlier_ranges


    def detect_histogram_outliers_for_subset(subset_y, threshold, points_x, points_y):
        """Return coordinates of outliers detected by histogram based outlier detection in subset"""
        histogram_data = moving_histogram_detection.get_histogram(subset_y)
        heights = []
        x_left_corners = []
        bin_widths = [] 
        for bin in histogram_data:
            heights.append(bin.get_height())
            x_left_corners.append(bin.get_xy()[0])
            bin_widths.append(bin.get_width())
        outlier_ranges = moving_histogram_detection.get_outlier_ranges(heights, x_left_corners, bin_widths, threshold)
        outliers_x = []
        outliers_y = []
        i = 0
        while (i < len(points_x)):
            for range in outlier_ranges:
                if ((points_y[i] > range[0]) and (points_y[i] <= range[1])):
                    outliers_x.append(points_x[i])
                    outliers_y.append(points_y[i])
            i += 1
        return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})


    def detect_histogram_outliers(threshold,interval,data_points):
        """Return coordinates of outliers detected by histogram based outlier detection"""
        outliers_x = []
        outliers_y = []
        if (int(threshold)<0 or int(interval)<0):
            print('invalid parameters passed')
            return pd.DataFrame({'timestamp':outliers_x,'data':outliers_y})
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        subset_size = int(len(points_y)/interval)
        if (interval == 1):
            subset_size = (len(points_y) - 1)
        i = 0
        while (i < len(points_y) - subset_size):
            subset = shared_methods.create_subset_dataframe(data_points, subset_size, i)
            outliers = moving_histogram_detection.detect_histogram_outliers_for_subset(subset['data'], threshold, points_x, points_y)
            for outlier_x in outliers['timestamp']:
                outliers_x.append(outlier_x)
            for outlier_y in outliers['data']:
                outliers_y.append(outlier_y)
            i += subset_size
        return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})


    def is_outlier(point_x, outliers_x):
        for outlier in outliers_x:
            if point_x == outlier:
                return True
        return False


    def detect_histogram_outliers_predictions_confidence(threshold,interval,data_points):
        """Return coordinates of outliers detection by histogram based outlier detection with confidence"""
        confidence = []
        outliers_x = []
        points_x = data_points['points_x']
        points_y = data_points['points_y']
        if (threshold<0 or interval<0):
            print('invalid parameters passed')
            return []
        subset_size = int(len(points_y)/interval)
        if (interval == 1):
            subset_size = (len(points_y) - 1)
        i = 0
        while (i < len(points_y) - subset_size):
            subset = shared_methods.create_subset_dataframe(data_points, subset_size, i)
            outliers = moving_histogram_detection.detect_histogram_outliers_for_subset(subset['data'], threshold, points_x, points_y)
            for outlier_x in outliers['timestamp']:
                outliers_x.append(outlier_x)
            i += subset_size
        i = 0
        while (i < len(points_y)):
            if moving_histogram_detection.is_outlier(points_x[i], outliers_x):
                confidence.append(-0.9)
            else:
                confidence.append(0.7)
            i += 1
        return pd.DataFrame({'timestamp': points_x,'data': points_y,'confidence':confidence})

    
    def real_time_prediction(previous_data_values, next_data_value):
        """Return confidence of next data value using histogram"""
        confidence = 0
        # get last 10 items in previous data
        i = len(previous_data_values)-2
        if (i <= 45):
            return confidence
        temp = []
        while (i > len(previous_data_values)-42):
            temp.append(previous_data_values[i])
            i -= 1
        previous_data_values = temp
        histogram_data = moving_histogram_detection.get_histogram(previous_data_values)
        heights = []
        x_left_corners = []
        bin_widths = [] 
        for bin in histogram_data:
            heights.append(bin.get_height())
            x_left_corners.append(bin.get_xy()[0])
            bin_widths.append(bin.get_width())
        outlier_ranges = moving_histogram_detection.get_outlier_ranges(heights, x_left_corners, bin_widths, 1)
        for range in outlier_ranges:
            if ((next_data_value < range[0]) and (next_data_value >= range[1])):
                return(-0.5)
        return 0.5