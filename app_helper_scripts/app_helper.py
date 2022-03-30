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
from app_helper_scripts.app_detection import run_detection_hours_known_outliers, run_detection_known_outliers, run_detection, run_detection_months
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

def get_result_data(path):
    try:
        detection_result_data_file = open('generated_data/' + path)
    except:
        print('ERROR: attemping to access file: generated_data/' + path)
        return (html.H3('No data generated yet - This could take several minutes'))
    
    detection_result_data = csv.reader(detection_result_data_file)
    results = []
    for row in detection_result_data:
        results.append(row)

    tp = len(results[0])
    fp = len(results[1])
    fn = len(results[2])
    tn = results[3][0]
    n = results[4][0]

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


def save_generated_data(requested_data, detection_data):
    #if not os.path.exists('generated_data/' + requested_data):
    #    os.makedirs('generated_data/' + requested_data)
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_plots.csv', detection_data[0],'w')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_plots.csv', detection_data[1],'a')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detected_outliers.csv', detection_data[2],'w')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detected_outliers.csv', detection_data[3],'a')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv', detection_data[4],'w')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv', detection_data[5],'a')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv', detection_data[6],'a')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv', detection_data[7],'a')
    #write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv', detection_data[8],'a')
    detector_name = detection_data[0]
    dataset_name = detection_data[1]
    true_positives = detection_data[2]
    false_positives = detection_data[3]
    false_negatives = detection_data[4]
    true_negative_count = detection_data[5][0]
    dataset_size = detection_data[6][0]

    print('Attemping to execture query: '+ 'INSERT INTO DETECTION (detector_name, dataset_name, fn_count, data_size) VALUES ' 
        + '(\''+ str(detector_name) +'\', '
        + '\''+ str(dataset_name) +'\', '
        + str(true_negative_count) + ', ' +
        str(dataset_size) + ');')

    database_helper.execute_query('INSERT INTO DETECTION (detector_name, dataset_name, fn_count, data_size) VALUES ' 
        + '(\''+ detector_name +'\', '
        + '\''+ dataset_name +'\', '
        + str(true_negative_count) + ', ' +
        str(dataset_size) + ');')




def get_detection_data(model, data_to_run, data_coordinates, threshold=0):
    return run_detection(model, data_coordinates, threshold)

def get_detection_data_months(model, data_to_run, data_coordinates, threshold=2):
    return run_detection_months(model, data_coordinates, threshold)

def get_detection_data_hours_known_outliers(model, data_to_run, outliers_csv, threshold=2, interval=10):
    return get_detection_data_known_outliers(model, data_to_run, outliers_csv, threshold, interval, True)

def load_saved_data(requested_data):
    detection_data = []
    if (os.path.isdir('generated_data/' + requested_data)):
        #
    
        #
        print('accessing data at ' + 'generated_data/' + requested_data)
        #

        # Remove this repeated code

        file = open ('generated_data/'+requested_data+'/'+requested_data+'_plots.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            detection_data.append(row)

        file = open ('generated_data/'+requested_data+'/'+requested_data+'_detected_outliers.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            detection_data.append(row)

        file = open ('generated_data/'+requested_data+'/'+requested_data+'_detector_evaluation_data.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            detection_data.append(row)
    else:
        print('Requested data: ' + requested_data + ' does not exist')
    return detection_data


def get_detection_data_known_outliers(model, data_to_run, target_data, threshold, interval=10, split_hours=False):
    detection_data = run_detection_known_outliers(model, data_to_run, target_data, threshold, interval)
    requested_data = model + '_' + data_to_run
    #detection_data = []
    #if (os.path.isdir('generated_data/' + requested_data)):
    #    detection_data = load_saved_data(requested_data)
    #else:
    #    path_to_data = 'resources/'+data_to_run+'.csv'
    #    if (exists(path_to_data) == False):
    #        path_to_data = 'resources/cloud_resource_data/'+data_to_run+'.csv'
    #    if (split_hours):
    #        detection_data = run_detection_hours_known_outliers(model, path_to_data, target_data, threshold, interval)
    #    else:
    #        detection_data = run_detection_known_outliers(model, path_to_data, target_data, threshold, interval, split_hours)
    save_generated_data(requested_data, detection_data)
    return detection_data




def get_fig_known_outliers(detection_data, data_to_run, model):
    return get_fig(detection_data, data_to_run, model, True)




def get_fig(detection_data, data_to_run, model, plot_actual_outliers=False):

    try:
        pycaret_plots = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})
        fig = px.line(pycaret_plots, x='timestamp', y='data',title= data_to_run + ' Data against Time (Using '+model+'-based outlier detection)')
        if (plot_actual_outliers):
            true_outlier_areas = pd.DataFrame({'timestamp1': detection_data[4],'timestamp2': detection_data[5]})
            i = 0
            while (i < len(true_outlier_areas['timestamp1'])):
                fig.add_vrect(x0=true_outlier_areas['timestamp1'][i],x1=true_outlier_areas['timestamp2'][i],fillcolor='red',opacity=0.25,line_width=0)
                i += 1
        detected_outliers = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})
        fig.add_trace(go.Scatter(x=detected_outliers['timestamp'], y=detected_outliers['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))
        fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=data_to_run)

        return fig
    except:
        print('Error getting figure for ' + model + ' on ' + data_to_run + 'data')


def get_associated_y_value(all_points_x, all_points_y, x_ref):
    i = 0
    while (i < len(all_points_x)):
        if (datetime.datetime.strptime(str(all_points_x[i]), '%Y-%m-%d %H:%M:%S') == datetime.datetime.strptime(str(x_ref), '%Y-%m-%d %H:%M:%S')):
            return all_points_y[i]
        i += 1


def get_coordinates_dataframe(all_points_x, all_points_y, points_x):
    points_y = []
    if (len(points_x) > 0):
        for point_x in points_x:
            index = all_points_x.index(point_x)
            points_y.append(all_points_y[index])
    return pd.DataFrame({'timestamp': points_x,'data': points_y})


def get_fig_plot_outliers(detection_data, data_to_run, model):

    try:
        timeseries_data = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})
        fig = px.line(timeseries_data, x='timestamp', y='data',title= data_to_run + ' Data against Time (Using '+model+'-based outlier detection)')
        
        false_positives_x = detection_data[5]
        fp_df = get_coordinates_dataframe(detection_data[0], detection_data[1], false_positives_x)
        fig.add_trace(go.Scatter(x=fp_df['timestamp'], y=fp_df['data'], mode='markers',name='False Positives', line=dict(color='red')))

        false_negatives_x = detection_data[6]
        fn_df = get_coordinates_dataframe(detection_data[0], detection_data[1], false_negatives_x)
        fig.add_trace(go.Scatter(x=fn_df['timestamp'], y=fn_df['data'], mode='markers',name='False Negatives', line=dict(color='black')))

        true_positives_x = detection_data[4]
        tp_df = get_coordinates_dataframe(detection_data[0], detection_data[1], true_positives_x)
        fig.add_trace(go.Scatter(x=tp_df['timestamp'], y=tp_df['data'], mode='markers',name='True Positives', line=dict(color='green')))

        fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=data_to_run)

        return fig
    except:
        print('Error getting figure for ' + model + ' on ' + data_to_run + 'data')