import numpy as np
import pandas as pd


def detect_boxplot_outliers(threshold, boxplot_dataset_size, data_points):                                                                                                                                                                                                                                                                                                                                                                                                     

    outliers_x = []
    outliers_y = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    i = 0

    if (i >= len(points_x) - boxplot_dataset_size):
        boxplot_dataset_size = int(len(points_x)/3)

    while (i<len(points_x) - boxplot_dataset_size):

        #get amount
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
        if (q1 - iqr*1.5*float(threshold) < 0):
            lower_bound = 0
        else:
            lower_bound = q1 - iqr*1.5*float(threshold)
        upper_bound = q3 + iqr*1.5*float(threshold)


        #is next data item an outlier?
        data_point = points_y[i + boxplot_dataset_size]
        if ((data_point < lower_bound) or (data_point > upper_bound)):
            outliers_x.append(points_x[i + boxplot_dataset_size])
            outliers_y.append(points_y[i + boxplot_dataset_size])
        i = i + 1

    return pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})





def detect_boxplot_outliers_predictions_confidence(threshold, boxplot_dataset_size, data_points):                                                                                                                                                                                                                                                                                                                                                                                                     

    predictions_x = []
    predictions_y = []
    confidence = []

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    i = 0

    if (i >= len(points_x) - boxplot_dataset_size):
        boxplot_dataset_size = int(len(points_x)/3)

    while (i<len(points_x) - boxplot_dataset_size):

        #get amount
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
        if (q1 - iqr*1.5*float(threshold) < 0):
            lower_bound = 0
        else:
            lower_bound = q1 - iqr*1.5*float(threshold)
        upper_bound = q3 + iqr*1.5*float(threshold)


        # confidence of next prediction
        data_point = points_y[i + boxplot_dataset_size]
        data_point_x = points_x[i + boxplot_dataset_size]
        predictions_x.append(data_point_x)
        predictions_y.append(data_point)
        if (data_point < lower_bound):
            distance_to_threshold = lower_bound - data_point
            conf = distance_to_threshold/lower_bound
            if (conf > 1):
                conf = 1
            confidence.append(-1 * conf)
        elif (data_point > upper_bound):
            distance_to_threshold = data_point - upper_bound
            conf = distance_to_threshold/upper_bound
            if (conf > 1):
                conf = 1
            confidence.append(-1 * conf) 
        elif (data_point > q3):
            distance_to_threshold = data_point - q3
            confidence.append(distance_to_threshold/upper_bound)
        elif (data_point < q1):
            distance_to_threshold = q1 - data_point
            confidence.append(distance_to_threshold/lower_bound)
        else:
            confidence.append(1)
            
        i = i + 1

    return pd.DataFrame({'timestamp': predictions_x,'data': predictions_y,'confidence':confidence})


#data = pd.read_csv('resources/speed_7578.csv')
#data_renamed = pd.DataFrame({'points_x': data['timestamp'],'points_y': data['value']})
#get_boxplot_outliers(1.5,50,data_renamed)