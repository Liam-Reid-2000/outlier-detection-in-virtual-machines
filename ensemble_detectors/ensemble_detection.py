from asyncio.windows_events import NULL
import pandas as pd
import datetime
from app_helper_scripts.app_detection import collect_detection_data

from app_helper_scripts.app_helper import get_detection_data_known_outliers, get_detector_threshold, get_fig, save_generated_data
from ensemble_detectors.ensemble_voting import get_ensemble_result

def get_ensemble_fig(ensemble_detector_list):

    if (len(ensemble_detector_list) == 0):
        return NULL

    detection_data = []

    for ensemble_detector in ensemble_detector_list:
        detection_data.append(get_detection_data_known_outliers(ensemble_detector, 'speed_7578', 'realTraffic/speed_7578.csv', get_detector_threshold(ensemble_detector)))
        print('got detection data for ' + ensemble_detector)
    all_outlier_coordinates = []

    # Get the outliers detected from each detector
    for data in detection_data:
        all_outlier_coordinates.append(pd.DataFrame({'timestamp':data[2], 'data':data[3]}))

    ensemble_outliers = []
    # Pass outlier data from each detector to voting system
    ensemble_outliers = get_ensemble_result(all_outlier_coordinates)

    ## Get detection data of average and modify outlier data to include ensemble voting result then plot ##
    average_detection_data = get_detection_data_known_outliers('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', 25)

    ## convert time stamps to date data types
    ensemble_outlier_timestamps_dates = []
    for outlier_x_string in ensemble_outliers['timestamp']:
        ensemble_outlier_timestamps_dates.append(datetime.datetime.strptime(str(outlier_x_string), '%Y-%m-%d %H:%M:%S'))
    ensemble_outliers['timestamp'] = ensemble_outlier_timestamps_dates

    ensemble_collected_data = []

    ## get the detection results
    ensemble_collected_data = collect_detection_data(ensemble_outliers, 'realTraffic/speed_7578.csv', average_detection_data[0], average_detection_data[1])

    # save the generated ensemble data  
    save_generated_data('ensemble', ensemble_collected_data)

    ## return the figure
    return get_fig(ensemble_collected_data, 'speed_7578', 'moving ensemble')