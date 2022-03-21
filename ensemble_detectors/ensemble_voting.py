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

    i = 0
    while (i < len(all_points_x)):
        if (all_points_x[i] not in predicted_actual_outliers_x):
            if (all_points_x.count(all_points_x[i]) > 2):
                predicted_actual_outliers_x.append(all_points_x[i])
                predicted_actual_outliers_y.append(all_points_y[i])
        i += 1
        
    return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})




def check_if_not_in_list(data, arr):
    i = 0
    while (i < len(arr)):
        if (data == arr[i]):
            return False
        i += 1
    return True


def get_ensemble_result_confidence(detector_results):
    
    print('Starting vote')

    all_points_x = []
    all_points_y = []
    final_confidence = []

    predicted_actual_outliers_x = []
    predicted_actual_outliers_y = []

    # fill all points x and y


    for detector_result in detector_results:
        i = 0
        while (i < len(detector_result['timestamp'])):
            print('iteration for getting unique data ' + str(i))
            if (detector_result['timestamp'][i] not in all_points_x):
                all_points_x.append(detector_result['timestamp'][i])
                all_points_y.append(detector_result['data'][i])
            i += 1
    
    # sum confidences
    i = 0
    while (i < len(all_points_x)):
        print('iteration ' + str(i))
        current_conf = 0
        for detector_result in detector_results:
            j = 0
            while (j < len(detector_result['timestamp'])):
                if (all_points_x[i] == detector_result['timestamp'][j]):
                    current_conf += detector_result['confidence'][j]
                j += 1
        #print('combined confidence for ' + str(i) + 'th x_point = ' + str(current_conf))
        final_confidence.append(current_conf)
        i += 1
     

    # Return outliers

    i = 0
    while (i < len(final_confidence)):
        if (final_confidence[i] < -0.5):
            predicted_actual_outliers_x.append(all_points_x[i])
            predicted_actual_outliers_y.append(all_points_y[i])
        i += 1


    return pd.DataFrame({'timestamp': predicted_actual_outliers_x,'data': predicted_actual_outliers_y})


