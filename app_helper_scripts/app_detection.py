from datetime import datetime
import pandas as pd
import csv
import json
from ensemble_detectors.ensemble_voting import get_ensemble_result
from ensemble_detectors.moving_average_detection import *
from ensemble_detectors.moving_median_detection import *
from ensemble_detectors.moving_boxplot import *
from ensemble_detectors.moving_histogram_detection import *
from app_helper_scripts.display_results import display_results
from unsupervised_detectors.pycaret_detection import detect_outliers_with_pycaret


def get_no_outliers(target_data):
    f = open('resources/combined_labels.json')
    data = json.load(f)
    f.close()
    return len(data[target_data])


def load_data_coordinates(csv_file_name):
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        points_x = []
        points_y = []
        for row in lines:
            try:
                points_y.append(float(row[1]))
                points_x.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("error")
        return pd.DataFrame({'timestamp':points_x,'data':points_y})



def get_outlier_area_ordinates(target_data):
    f = open('resources/combined_windows.json')
    data = json.load(f)
    arrX1 = []
    arrX2 = []
    for i in data[target_data]:
        arrX1.append(datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'))
        arrX2.append(datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'))
    f.close()
    return pd.DataFrame({'first_x': arrX1, 'second_x': arrX2})
    

def collect_detection_data_known_outliers(outliers_df, anomalies_csv_passed, points_x_passed, points_y_passed, real_outlier_areas=[]):
    true_outliers = get_outlier_area_ordinates(anomalies_csv_passed)
    if (len(real_outlier_areas)>0):
        true_outliers = real_outlier_areas
    outliers_x_detected = []
    outliers_x_detected.append(outliers_df['timestamp'])
    detection_data = collect_detection_data(outliers_df, points_x_passed, points_y_passed)
    detection_data.append(true_outliers['first_x'])
    detection_data.append(true_outliers['second_x'])
    results = display_results(anomalies_csv_passed, points_x_passed, outliers_x_detected)
    detection_data.append(results.display_results())

    return detection_data


def collect_detection_data(outliers_df, points_x, points_y):
    outliers_x_detected = []
    outliers_x_detected.append(outliers_df['timestamp'])
    detection_data = []
    detection_data.append(points_x)
    detection_data.append(points_y)
    detection_data.append(outliers_df['timestamp'])
    detection_data.append(outliers_df['data'])

    return detection_data


def run_detection(model, data_coordinates, threshold, interval=10):
    
    points_x = data_coordinates['timestamp']
    points_y = data_coordinates['data']

    data_coordinates_renamed = pd.DataFrame({'points_x': points_x,'points_y': points_y})

    outliers_x = []
    outliers_y = []
    #use switch case here
    if (model == 'moving_average'):
        outliers_ = detect_average_outliers(threshold, get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_median'):
        outliers_ = detect_median_outliers(threshold, get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_boxplot'):
        #outliers_ = detect_boxplot_outliers(threshold, interval, data_coordinates_renamed)
        outliers_ = detect_boxplot_outliers(threshold, 20, data_coordinates_renamed)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_histogram'):
        #outliers_ = detect_histogram_outliers(threshold,interval, data_coordinates_renamed)
        outliers_ = detect_histogram_outliers(threshold,2, data_coordinates_renamed)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'full_ensemble'):
        ensemble_outliers = []
        ensemble_outliers.append(detect_average_outliers(threshold, get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
        ensemble_outliers.append(detect_median_outliers(threshold, get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
        ensemble_outliers.append(detect_boxplot_outliers(threshold, interval, data_coordinates_renamed))
        #ensemble_outliers.append(detect_histogram_outliers(threshold,interval, data_coordinates_renamed))
        #ensemble_outliers.append(detect_histogram_outliers(threshold,2, data_coordinates_renamed))
        outliers_after_voting = get_ensemble_result(ensemble_outliers)
        outliers_x = outliers_after_voting['timestamp']
        outliers_y = outliers_after_voting['data']
    else:
        outliers_ = detect_outliers_with_pycaret(model, data_coordinates)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    outliers = pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})

    return collect_detection_data(outliers, points_x, points_y)



def split_data_to_months(timestamps, data):
    data_split_to_months_x = []
    data_split_to_months_y = []
    i = 0
    while i < 12:
        arr = []
        data_split_to_months_x.append(arr)
        arrtoo = []
        data_split_to_months_y.append(arrtoo)
        i += 1

    i = 0
    while i < len(timestamps):
        data_split_to_months_x[timestamps[i].month-1].append(timestamps[i])
        data_split_to_months_y[timestamps[i].month-1].append(data[i])
        i += 1


    # list of data frames
    separated_months_as_dataframes = []
    i = 0
    while i < len(data_split_to_months_x):
        df = pd.DataFrame({'timestamp':data_split_to_months_x[i], 'data':data_split_to_months_y[i]})
        separated_months_as_dataframes.append(df)
        i += 1
    return separated_months_as_dataframes



def run_detection_months(model, data_coordinates, threshold, interval=7):
    
    points_x = data_coordinates['timestamp']
    points_y = data_coordinates['data']
    
    separated_months_as_dataframes = split_data_to_months(points_x, points_y)
    all_outliers_x = []
    all_outliers_y = []

    for i in separated_months_as_dataframes:
        detection_data = run_detection(model, i, threshold, interval)
        for j in detection_data[2]:
            all_outliers_x.append(j)
        for j in detection_data[3]:
            all_outliers_y.append(j)

    all_outliers_df = pd.DataFrame({'timestamp':all_outliers_x,'data':all_outliers_y})
    return collect_detection_data(all_outliers_df, points_x, points_y)


def run_detection_known_outliers(model, data_csv, outliers_csv, threshold):

    data_coordinates = load_data_coordinates(data_csv)
    detection_data = run_detection(model, data_coordinates, threshold)
    outliers_df = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})

    return collect_detection_data_known_outliers(outliers_df, outliers_csv, data_coordinates['timestamp'], data_coordinates['data'])