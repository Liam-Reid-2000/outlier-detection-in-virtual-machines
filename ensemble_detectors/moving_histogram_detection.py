from turtle import width
import matplotlib.pyplot as plt
import numpy as np
import csv
import datetime
import pandas as pd


def detect_histogram_outliers(threshold, data_points):                                                                                                                                                                                                                                                                                                                                                                                                     

    outliers_x = []
    outliers_y = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    plt.hist(points_y)
    ax = plt.gca()
    p = ax.patches

    heights = []
    x_left_corners = []
    bin_widths = [] 

    for bin in p:
        heights.append(bin.get_height())
        x_left_corners.append(bin.get_xy()[0])
        bin_widths.append(bin.get_width())

    outlier_ranges = []

    i = 0
    while i < len(heights):
        outlier_range = []
        if (heights[i] < threshold):
            outlier_range.append(x_left_corners[i])
            outlier_range.append(x_left_corners[i] + bin_widths[i])
            outlier_ranges.append(outlier_range)
        else:
            print('inliers')
        i += 1

    outliers_x = []
    outliers_y = []

    i = 0
    while (i < len(points_x)):
        outlier = False
        for range in outlier_ranges:
            if ((points_y[i] > range[0]) and (points_y[i] <= range[1])):
                outliers_x.append(points_x[i])
                outliers_y.append(points_y[i])
        i += 1

    #plt.show()
    return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})