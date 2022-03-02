from turtle import width
import matplotlib.pyplot as plt
import pandas as pd


def detect_histogram_outliers(threshold,interval,data_points):                                                                                                                                                                                                                                                                                                                                                                                                     

    outliers_x = []
    outliers_y = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    interval = int(len(points_y)/8)
    threshold = 1

    i = 0
    while (i<len(points_y) - interval):
        subset_x = []
        subset_y = []
        j = i
        while (j < i + interval):
            subset_x.append(points_x[j])
            subset_y.append(points_y[j])
            j+=1

        plt.hist(subset_y)
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

        j = 0
        while j < len(heights):
            outlier_range = []
            if (heights[j] < int(threshold)):
                outlier_range.append(x_left_corners[j])
                outlier_range.append(x_left_corners[j] + bin_widths[j])
                outlier_ranges.append(outlier_range)
            j += 1

        j = 0
        while (j < len(points_x)):
            for range in outlier_ranges:
                if ((points_y[j] > range[0]) and (points_y[j] <= range[1])):
                    outliers_x.append(points_x[j])
                    outliers_y.append(points_y[j])
            j += 1
        print('iteration = ' + str(i))
        i += interval

        #plt.show()
    print('loop terminated')
    return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})