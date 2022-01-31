import pandas as pd

def get_ensemble_result(outliers1, outliers2):
    
    all_outliers = []
    all_outliers.append(outliers1)
    all_outliers.append(outliers2)

    all_points_x = []
    all_points_y = []
    predicted_actual_outliers_x = []
    predicted_actual_outliers_y = []
    
    for outlier_data in all_outliers:
        for point_x in outlier_data['timestamp']:
            all_points_x.append(point_x)
        for point_y in outlier_data['data']:
            all_points_y.append(point_y)
    
    i = 0
    while (i < len(all_points_x)):
        print('size x = ' + str(len(predicted_actual_outliers_x)))
        print('size y = ' + str(len(predicted_actual_outliers_y)))
        if (all_points_x[i] not in predicted_actual_outliers_x):
            j = i + 1
            while (j < len(all_points_x)):
                if (all_points_x[i] == all_points_x[j]):
                    predicted_actual_outliers_x.append(all_points_x[i])
                    predicted_actual_outliers_y.append(all_points_y[i])
                j += 1
        i += 1
    
    print('size x = ' + str(len(predicted_actual_outliers_x)))
    print('size y = ' + str(len(predicted_actual_outliers_y)))

    return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})

    #######################################################


    outlier_points_1_x = outliers1['timestamp']
    outlier_points_1_y = outliers1['data']

    outlier_points_2_x = outliers2['timestamp']
    outlier_points_2_y = outliers2['data']
    
    smallerSet = outlier_points_1_x
    if (len(smallerSet) > len(outlier_points_2_x)):
        smallerSet = outlier_points_2_x

    ensemble_outliers_x = []
    ensemble_outliers_y = []

    i = 0
    while (i < len(smallerSet)):
        if (outlier_points_1_x[i] == outlier_points_2_x[i]):
            ensemble_outliers_x.append(outlier_points_1_x[i])
            ensemble_outliers_y.append(outlier_points_1_y[i])
        i += 1

    return pd.DataFrame({'timestamp': ensemble_outliers_x,'data': ensemble_outliers_y})

