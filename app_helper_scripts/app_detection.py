import matplotlib.pyplot as plt
from datetime import datetime
from pycaret.anomaly import *
import pandas as pd
import csv
import json
from ensemble_detectors.moving_average_detection import *
from ensemble_detectors.moving_median_detection import *
from ensemble_detectors.moving_boxplot import *
from ensemble_detectors.moving_histogram_detection import *
from app_helper_scripts.display_results import display_results

outliers_x_detected = []


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
                points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("error")
        return pd.DataFrame({'timestamp':points_x,'data':points_y})



def get_outlier_area_ordinates(target_data):
    f = open('resources/combined_windows.json')
    data = json.load(f)
    arrX1 = []
    arrX2 = []
    for i in data[target_data]:
        arrX1.append(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'))
        arrX2.append(datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'))
    f.close()
    return pd.DataFrame({'first_x': arrX1, 'second_x': arrX2})


def detect_anomalies(model, data_coordinates):
    points_x = data_coordinates['timestamp']
    points_y = data_coordinates['data']
    
    data = pd.DataFrame({'timestamp': points_x,
                    'data': points_y})
    data.set_index('timestamp', drop=True, inplace=True)
    data['day'] = [i.day for i in data.index]
    data['day_name'] = [i.day_name() for i in data.index]
    data['day_of_year'] = [i.dayofyear for i in data.index]
    data['week_of_year'] = [i.weekofyear for i in data.index]
    data['hour'] = [i.hour for i in data.index] # only use this for speed data, commetn rest
    data['is_weekday'] = [i.isoweekday() for i in data.index]
    data.head()

    s = setup(data, session_id = 123, silent = True)
    myModel = create_model(model, fraction = 0.05)#, fraction = outlierCount/len(points_x))

    myModel_results = assign_model(myModel)
    myModel_results.head()
    myModel_results[myModel_results['Anomaly'] == 1].head()
    outlier_dates = myModel_results[myModel_results['Anomaly'] == 1].index
    y_values = [myModel_results.loc[i]['data'] for i in outlier_dates]

    outliers = pd.DataFrame({'timestamp': outlier_dates,
                    'data': y_values})

    return outliers



def collect_detection_data(outliers_passed, anomalies_csv_passed, points_x_passed, points_y_passed, real_outlier_areas=[]):
    true_outliers = get_outlier_area_ordinates(anomalies_csv_passed)
    if (len(real_outlier_areas)>0):
        true_outliers = real_outlier_areas
    outliers_x_detected = []
    outliers_x_detected.clear()
    outliers_x_detected.append(outliers_passed['timestamp'])
    results = display_results(anomalies_csv_passed, points_x_passed, outliers_x_detected)
    detection_data = []
    detection_data.clear()
    detection_data.append(points_x_passed)
    detection_data.append(points_y_passed)
    detection_data.append(outliers_passed['timestamp'])
    detection_data.append(outliers_passed['data'])
    detection_data.append(true_outliers['first_x'])
    detection_data.append(true_outliers['second_x'])
    detection_data.append(results.display_results())

    return detection_data



def run_detection(model, data_csv, anomalies_csv, threshold):
    
    data_coordinates = load_data_coordinates(data_csv)
    points_x = data_coordinates['timestamp']
    points_y = data_coordinates['data']

    outliers_x = []
    outliers_y = []
    if (model == 'moving_average'):
        outliers_ = detect_average_outliers(threshold, get_moving_average_coordinates(10, pd.DataFrame({'points_x': points_x,'points_y': points_y})), pd.DataFrame({'points_x': points_x,'points_y': points_y}))
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_median'):
        outliers_ = detect_median_outliers(threshold, get_moving_median_coordinates(10, pd.DataFrame({'points_x': points_x,'points_y': points_y})), pd.DataFrame({'points_x': points_x,'points_y': points_y}))
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_boxplot'):
        outliers_ = detect_boxplot_outliers(threshold, 50, pd.DataFrame({'points_x': points_x,'points_y': points_y}))
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    elif (model == 'moving_histogram'):
        outliers_ = detect_histogram_outliers(threshold, pd.DataFrame({'points_x': points_x,'points_y': points_y}))
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    else:
        outliers_ = detect_anomalies(model, data_coordinates)
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    outliers = pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})

    return collect_detection_data(outliers, anomalies_csv, points_x, points_y)
