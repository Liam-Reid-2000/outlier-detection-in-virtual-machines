import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def detect_boxplot_outliers(threshold, boxplot_dataset_size, data_points):                                                                                                                                                                                                                                                                                                                                                                                                     

    outliers_x = []
    outliers_y = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    outlier_count = 0
    i = 0
    while (i<len(points_x) - boxplot_dataset_size):

        #get 50
        subset_x = []
        subset_y = []
        j = i
        while (j < i + boxplot_dataset_size):
            subset_x.append(points_x[j])
            subset_y.append(points_y[j])
            j+=1

        #create new df
        subset_data = pd.DataFrame({'timestamp': subset_x, 'value': subset_y})

        #find quartile values and interquartile range

        #define array of data
        dataArr = np.array(subset_data['value'])
        #calculate interquartile range 
        q3, q1 = np.percentile(dataArr, [75 ,25])
        iqr = q3 - q1

        #calculate class boundaries
        lower_bound = q1 - iqr*threshold
        upper_bound = q3 + iqr*threshold


        #is next data item an outlier?
        data_point = points_y[i + boxplot_dataset_size]
        if ((data_point < lower_bound) or (data_point > upper_bound)):
            outlier_count +=1
            outliers_x.append(points_x[i + boxplot_dataset_size])
            outliers_y.append(points_y[i + boxplot_dataset_size])
        i = i + 1

    return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})


#data = pd.read_csv('resources/speed_7578.csv')
#data_renamed = pd.DataFrame({'points_x': data['timestamp'],'points_y': data['value']})
#get_boxplot_outliers(1.5,50,data_renamed)