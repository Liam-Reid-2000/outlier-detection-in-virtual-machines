import pandas as pd

def get_ensemble_result(all_outliers, no_detectors):

    all_points_x = []
    all_points_y = []
    predicted_actual_outliers_x = []
    predicted_actual_outliers_y = []
    
    for outlier_data in all_outliers:
        for point_x in outlier_data['timestamp']:
            all_points_x.append(point_x)
        for point_y in outlier_data['data']:
            all_points_y.append(point_y)
    
    #i = 0
    #while (i < len(all_points_x)):
    #    if (all_points_x[i] not in predicted_actual_outliers_x):
    #        j = i + 1
    #        while (j < len(all_points_x)):
    #            if (all_points_x[i] == all_points_x[j]):
    #                predicted_actual_outliers_x.append(all_points_x[i])
    #                predicted_actual_outliers_y.append(all_points_y[i])
    #            j += 1
    #    i += 1

    i = 0
    while (i < len(all_points_x)):
        if (all_points_x[i] not in predicted_actual_outliers_x):
            if (all_points_x.count(all_points_x[i]) > 2):
                predicted_actual_outliers_x.append(all_points_x[i])
                predicted_actual_outliers_y.append(all_points_y[i])
        i += 1
        
    return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})