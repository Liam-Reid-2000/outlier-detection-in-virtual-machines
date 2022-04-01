from app_helper_scripts.csv_helper import csv_helper
from app_helper_scripts.app_detection import collect_detection_data_for_database, run_detection
from app_helper_scripts.app_helper import get_detector_threshold, save_generated_data
from ensemble_detectors.ensemble_voting import get_ensemble_result, get_ensemble_result_confidence
import pandas as pd

def get_ensemble_detection_data(ensemble_detector_list, dataset, known_outliers_csv):

    if (len(ensemble_detector_list) == 0):
        return []

    all_outlier_coordinates = []

    data_coordinates = csv_helper.load_data_coordinates(dataset)
    for ensemble_detector in ensemble_detector_list:
        #detection_data.append(get_detection_data_known_outliers(ensemble_detector, dataset, known_outliers_csv, get_detector_threshold(ensemble_detector)))
        detection_data = run_detection(ensemble_detector, data_coordinates, get_detector_threshold(ensemble_detector))
        outliers = pd.DataFrame({'timestamp':detection_data[2],'data':detection_data[3]})
        all_outlier_coordinates.append(outliers)
        print('got detection data for ' + ensemble_detector)

    ensemble_outliers = []
    # Pass outlier data from each detector to voting system
    ensemble_outliers = get_ensemble_result(all_outlier_coordinates)

    ## convert time stamps to date data types
    #ensemble_outlier_timestamps_dates = []
    #for outlier_x_string in ensemble_outliers['timestamp']:
    #    ensemble_outlier_timestamps_dates.append(datetime.datetime.strptime(str(outlier_x_string), '%Y-%m-%d %H:%M:%S'))
    #ensemble_outliers['timestamp'] = ensemble_outlier_timestamps_dates

    ## get the detection results
    #ensemble_collected_data = collect_detection_data_known_outliers(ensemble_outliers, known_outliers_csv, average_detection_data[0], average_detection_data[1])
    ensemble_collected_data = collect_detection_data_for_database('ensemble', dataset, ensemble_outliers, known_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'])


    # save the generated ensemble data  
    save_generated_data(ensemble_collected_data)

    ## return the figure
    return ensemble_collected_data