import pandas as pd
import csv
import os
import json
import datetime
from os.path import exists
from dash import html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from app_helper_scripts.app_detection import run_detection_known_outliers, run_detection, run_detection_months
from app_helper_scripts.csv_helper import *
from app_helper_scripts.metric_calculations import metric_calculations
from database_scripts.database_helper import database_helper

def get_detector_threshold(ref):
    f = open('resources/config.json',)
    data = json.load(f)
    for i in data['available_detectors']:
        if (i[0] ==ref):
            f.close()
            return i[1]
    f.close()
   
def get_outlier_ref(ref):
    f = open('resources/config.json',)
    data = json.load(f)
    for i in data['available_datasets']:
        if (i[0] ==ref):
            f.close()
            return i[1]
    for i in data['available_datasets_cloud_resource_data']:
        if (i[0] ==ref):
            f.close()
            return i[1]
    f.close()


def is_data_generated(detector_name, dataset_name):
    rows_returned = database_helper.execute_query('SELECT * FROM DETECTION WHERE detector_name == \'' + detector_name + '\' AND dataset_name == \'' + dataset_name + '\';')
    if len(rows_returned) > 0:
        return True
    return False


def get_result_data(detector_name, dataset_name):
    if is_data_generated(detector_name, dataset_name) == False:
        print('ERROR: attemping to access database for ' + detector_name + ' ' + dataset_name)
        return (html.H3('No data generated yet - This could take several minutes'))
    
    detection_data = load_generated_data_from_database(detector_name, dataset_name)

    tp = len(detection_data[2])
    fp = len(detection_data[3])
    fn = len(detection_data[4])
    tn = detection_data[5][0]
    n = detection_data[6][0]

    accuracy = metric_calculations.calculate_accuracy(tn, tp, n)
    recall = metric_calculations.calulate_recall(tp, fn)
    precision = metric_calculations.calculate_precision(tp, fp)
    f1 = metric_calculations.calculate_f1(precision, recall)

    output = []
    output.append('Accuracy: ' + str(round(float(accuracy)*100,4))+'%\n')
    output.append('Recall: ' + str(round(float(recall)*100,4))+'%\n')
    output.append('Precision: ' + str(round(float(precision)*100,4))+'%\n')
    output.append('f1 score: ' + str(round(float(f1)*100,4))+'%\n')

    return (html.P([output[0],html.Br(),output[1],html.Br(),output[2],html.Br(),output[3]]))


def save_generated_data(detection_data):

    detector_name = detection_data[0]
    dataset_name = detection_data[1]
    true_positives = detection_data[2]
    false_positives = detection_data[3]
    false_negatives = detection_data[4]
    true_negative_count = detection_data[5][0]
    dataset_size = detection_data[6][0]

    database_helper.execute_query('INSERT INTO DETECTION (detector_name, dataset_name, fn_count, data_size) VALUES ' 
        + '(\''+ detector_name +'\', '
        + '\''+ dataset_name +'\', '
        + str(true_negative_count) + ', ' +
        str(dataset_size) + ');')

    detection_key = database_helper.get_primary_key_of_added_row()
    for true_poitive in true_positives:
        database_helper.execute_query('INSERT INTO TRUE_POSITIVES (detection_id, true_positive_datetime) VALUES (' 
            + str(detection_key) + ', \'' + str(true_poitive) + '\');')
    for false_positive in false_positives:
        database_helper.execute_query('INSERT INTO FALSE_POSITIVES (detection_id, false_positive_datetime) VALUES (' 
            + str(detection_key) + ', \'' + str(false_positive) + '\');')
    for false_negative in false_negatives:
        database_helper.execute_query('INSERT INTO FALSE_NEGATIVES (detection_id, false_negative_datetime) VALUES (' 
            + str(detection_key) + ', \'' + str(false_negative) + '\');')

def load_generated_data_from_database(detector_name, dataset_name):
    returned_detection_data = database_helper.execute_query('SELECT * FROM DETECTION WHERE detector_name == \'' + detector_name + '\' AND dataset_name == \'' + dataset_name + '\';')[0]
    key = returned_detection_data[0]
    true_negative_count = returned_detection_data[3]
    dataset_size = returned_detection_data[4]

    true_positives = []
    for true_positive_row in database_helper.execute_query('SELECT * FROM TRUE_POSITIVES WHERE detection_id == ' + str(key)):
        true_positives.append(true_positive_row[2])
    false_positives = []
    for false_positive_row in database_helper.execute_query('SELECT * FROM FALSE_POSITIVES WHERE detection_id == ' + str(key)):
        false_positives.append(false_positive_row[2])
    false_negatives = []
    for false_negative_row in database_helper.execute_query('SELECT * FROM FALSE_NEGATIVES WHERE detection_id == ' + str(key)):
        false_negatives.append(false_negative_row[2])

    detection_data = []
    detection_data.append(detector_name)
    detection_data.append(dataset_name)
    detection_data.append(true_positives)
    detection_data.append(false_positives)
    detection_data.append(false_negatives)
    detection_data.append([true_negative_count])
    detection_data.append([dataset_size])

    return detection_data



def get_detection_data(model, data_to_run, data_coordinates, threshold=0):
    return run_detection(model, data_coordinates, threshold)

def get_detection_data_months(model, data_to_run, data_coordinates, threshold=2):
    return run_detection_months(model, data_coordinates, threshold)


def get_detection_data_known_outliers(detector_name, dataset_name, target_data, threshold, interval=10):
    if is_data_generated(detector_name, dataset_name):
        return load_generated_data_from_database(detector_name, dataset_name)
    detection_data = run_detection_known_outliers(detector_name, dataset_name, target_data, threshold, interval)
    save_generated_data(detection_data)
    return detection_data


def get_fig(detection_data, dataset_name, detector):
    try:
        timeseries_data = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})
        fig = px.line(timeseries_data, x='timestamp', y='data',title= dataset_name + ' Data against Time (Using '+detector+'-based outlier detection)')
        detected_outliers = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})
        fig.add_trace(go.Scatter(x=detected_outliers['timestamp'], y=detected_outliers['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))
        fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=dataset_name)

        return fig
    except:
        print('Error getting figure for ' + detector + ' on ' + dataset_name + 'data')


def change_x_values_to_dates(points_x):
    x_as_dates = []
    for point_x in points_x:
        x_as_dates.append(datetime.datetime.strptime(str(point_x), '%Y-%m-%d %H:%M:%S'))
    return x_as_dates


def get_coordinates_dataframe(all_points_x, all_points_y, points_x):
    points_y = []
    if (len(points_x) > 0):
        for point_x in points_x:
            index = all_points_x.index(datetime.datetime.strptime(str(point_x), '%Y-%m-%d %H:%M:%S'))
            points_y.append(all_points_y[index])
    return pd.DataFrame({'timestamp': points_x,'data': points_y})


def load_data_coordinates(dataset_name):
    path_to_data = 'resources/' + dataset_name + '.csv'
    if (exists(path_to_data) == False):
        path_to_data = 'resources/cloud_resource_data/'+dataset_name+'.csv'
    with open(path_to_data,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        points_x = []
        points_y = []
        for row in lines:
            try:
                points_y.append(float(row[1]))
                points_x.append(datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("Error, could not load data coordinates")
        return pd.DataFrame({'timestamp':points_x,'data':points_y})


def get_fig_plot_outliers(detection_data, data_to_run, model):
    timeseries_data = load_data_coordinates(data_to_run)
    points_x = timeseries_data['timestamp']
    points_y = timeseries_data['data']
    points_x = change_x_values_to_dates(points_x)

    #try:
    fig = px.line(timeseries_data, x='timestamp', y='data',title= data_to_run + ' Data against Time (Using '+model+'-based outlier detection)')
    
    false_positives_x = detection_data[3]
    if len(false_positives_x) > 0:
        fp_df = get_coordinates_dataframe(points_x, points_y, change_x_values_to_dates(false_positives_x))
        fig.add_trace(go.Scatter(x=fp_df['timestamp'], y=fp_df['data'], mode='markers',name='False Positives', line=dict(color='red')))

    false_negatives_x = detection_data[4]
    if len(false_negatives_x) > 0:
        fn_df = get_coordinates_dataframe(points_x, points_y, change_x_values_to_dates(false_negatives_x))
        fig.add_trace(go.Scatter(x=fn_df['timestamp'], y=fn_df['data'], mode='markers',name='False Negatives', line=dict(color='black')))

    true_positives_x = detection_data[2]
    if len(true_positives_x) > 0:
        tp_df = get_coordinates_dataframe(points_x, points_y, change_x_values_to_dates(true_positives_x))
        fig.add_trace(go.Scatter(x=tp_df['timestamp'], y=tp_df['data'], mode='markers',name='True Positives', line=dict(color='green')))

    fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=data_to_run)

    return fig
    #except:
    #    print('Error getting figure for ' + model + ' on ' + data_to_run + 'data')