import matplotlib.pyplot as plt
from datetime import datetime
from pycaret.anomaly import *
import pandas as pd
import csv
import json
from ensemble_detectors.moving_average_detection import *
from ensemble_detectors.moving_median_detection import *
from ensemble_detectors.moving_boxplot import *
from app_helper_scripts.display_results import display_results


points_x = []
points_y = []

outliers_x_detected = []


def get_no_outliers(target_data):
    f = open('resources/combined_labels.json')
    data = json.load(f)
    f.close()
    return len(data[target_data])


def plot_data(csv_file_name):
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        for row in lines:
            try:
                points_y.append(float(row[1]))
                points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("error")



def plot_anomalies(target_data):
    f = open('resources/combined_windows.json')
    data = json.load(f)
    arrX1 = []
    arrX2 = []
    for i in data[target_data]:
        arrX1.append(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'))
        arrX2.append(datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'))
    f.close()
    return pd.DataFrame({'first_x': arrX1, 'second_x': arrX2})


def detect_anomalies(model, outlierCount):
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





def run_detection(model, data_csv, anomalies_csv, threshold):
    
    points_x.clear()
    points_y.clear()

    outliers_x_detected.clear()
    
    plot_data(data_csv)
    true_outliers = plot_anomalies(anomalies_csv)
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
    else:
        outliers_ = detect_anomalies(model, get_no_outliers(anomalies_csv))
        outliers_x = outliers_['timestamp']
        outliers_y = outliers_['data']
    outliers = pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})
    outliers_x_detected.append(outliers_x)
    results = display_results(anomalies_csv, points_x, outliers_x_detected)
    detection_data = []
    detection_data.append(points_x)
    detection_data.append(points_y)
    detection_data.append(outliers['timestamp'])
    detection_data.append(outliers['data'])
    detection_data.append(true_outliers['first_x'])
    detection_data.append(true_outliers['second_x'])
    detection_data.append(results.display_results())

    return detection_data

def plot_detection_data(detection_data, title, target_data):
    plt.plot(detection_data[0], detection_data[1], color = 'b',label = "Data",linewidth=0.5)
    plt.scatter(detection_data[2], detection_data[3],color = 'r',label = "Outliers Detected",marker='o')
    
    
    f = open('resources/combined_windows.json')
    data = json.load(f)
    for i in data[target_data]:
        plt.axvspan(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'), datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'), color = 'red',alpha=0.5)
    f.close()


    plt.xticks(rotation = 25)
    plt.xlabel('Timestamp')
    plt.ylabel('Data')
    plt.title(title, fontsize = 20)
    plt.grid()
    plt.legend()

    plt.show()

def main():
    detection_data = run_detection('svm', 'resources/speed_7578.csv', 'realTraffic/speed_7578.csv')
    #run_detection('knn', 'nyc_taxi.csv', 'realKnownCause/nyc_taxi.csv', 'NYC Taxi Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'Twitter_volume_UPS.csv', 'realTweets/Twitter_volume_UPS.csv', 'Twitter Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'machine_temperature_system_failure.csv', 'realKnownCause/machine_temperature_system_failure.csv', 'Machine Temperature Data against Time (Using knn-based outlier detection)')
    #detection_data = run_detection('knn', 'ec2_cpu_utilization_fe7f93.csv', 'realAWSCloudwatch/ec2_cpu_utilization_fe7f93.csv', 'AWS Cloud Watch Data against Time (Using knn-based outlier detection)')

    plot_detection_data(detection_data, 'Speed Data against Time (Using svm-based outlier detection)', 'realTraffic/speed_7578.csv')
    


if __name__=="__main__":
    main()