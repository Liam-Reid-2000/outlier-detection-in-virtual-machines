import matplotlib.pyplot as plt
import pandas as pd


def create_subset(index_of_start_of_subset, subset_size, points_x, points_y):
    subset_x = []
    subset_y = []
    i = index_of_start_of_subset
    while (i < index_of_start_of_subset + subset_size):
        subset_x.append(points_x[i])
        subset_y.append(points_y[i])
        i += 1
    return pd.DataFrame({'timestamp':subset_x,'data':subset_y})


def get_histogram(subset_y):
    plt.hist(subset_y)
    ax = plt.gca()
    return ax.patches


def get_outlier_ranges(heights, x_left_corners, bin_widths, threshold):
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

    histogram_data = get_histogram(subset_y)
    heights = []
    x_left_corners = []
    bin_widths = [] 

    for bin in histogram_data:
        heights.append(bin.get_height())
        x_left_corners.append(bin.get_xy()[0])
        bin_widths.append(bin.get_width())

    outlier_ranges = get_outlier_ranges(heights, x_left_corners, bin_widths, threshold)

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

    outliers_x = []
    outliers_y = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    subset_size = int(len(points_y)/interval)
    if (interval == 1):
        return detect_histogram_outliers_for_subset(points_y, threshold, points_x, points_y)

    i = 0
    while (i < len(points_y) - subset_size):
        subset = create_subset(i, subset_size, points_x, points_y)
        outliers = detect_histogram_outliers_for_subset(subset['data'], threshold, points_x, points_y)
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

    confidence = []
    outliers_x = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    subset_size = int(len(points_y)/interval)
    if (interval == 1):
        return detect_histogram_outliers_for_subset(points_y, threshold, points_x, points_y)

    i = 0
    while (i < len(points_y) - subset_size):
        subset = create_subset(i, subset_size, points_x, points_y)
        outliers = detect_histogram_outliers_for_subset(subset['data'], threshold, points_x, points_y)
        for outlier_x in outliers['timestamp']:
            outliers_x.append(outlier_x)
        i += subset_size

    i = 0
    while (i < len(points_y)):
        if is_outlier(points_x[i], outliers_x):
            confidence.append(-0.2)
        else:
            confidence.append(0.8)
        i += 1
       
    return pd.DataFrame({'timestamp': points_x,'data': points_y,'confidence':confidence})