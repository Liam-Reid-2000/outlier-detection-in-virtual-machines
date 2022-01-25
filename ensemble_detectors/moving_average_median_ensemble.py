import pandas as pd

def get_ensemble_result(outliers1, outliers2):
    
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

