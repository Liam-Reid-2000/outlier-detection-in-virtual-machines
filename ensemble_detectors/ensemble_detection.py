from app_helper_scripts.csv_helper import csv_helper
from app_helper_scripts.app_detection import collect_detection_data_for_database, run_detection
from app_helper_scripts.app_helper import get_detector_threshold, save_generated_data
from ensemble_detectors.ensemble_voting import ensemble_voting
import pandas as pd
import time

def get_ensemble_detection_data(ensemble_detector_list, dataset, known_outliers_csv):

    if (len(ensemble_detector_list) == 0):
        return []

    all_outlier_coordinates = []

    tic = time.perf_counter()
    
    data_coordinates = csv_helper.load_data_coordinates(dataset)
    for ensemble_detector in ensemble_detector_list:
        detection_data = run_detection(ensemble_detector, data_coordinates, get_detector_threshold(ensemble_detector))
        outliers = pd.DataFrame({'timestamp':detection_data[2],'data':detection_data[3]})
        all_outlier_coordinates.append(outliers)

    ensemble_outliers = []
    # Pass outlier data from each detector to voting system
    ensemble_outliers = ensemble_voting.get_ensemble_result_majority(all_outlier_coordinates)
    
    toc = time.perf_counter()
    detection_time = toc - tic

    ## get the detection results
    ensemble_collected_data = collect_detection_data_for_database('ensemble', dataset, ensemble_outliers, known_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'], detection_time)

    # save the generated ensemble data  
    save_generated_data(ensemble_collected_data)

    ## return the figure
    return ensemble_collected_data