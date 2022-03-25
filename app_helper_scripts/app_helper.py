import pandas as pd
import csv
import os
import json
from os.path import exists
from dash import html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from app_helper_scripts.app_detection import run_detection_hours_known_outliers, run_detection_known_outliers, run_detection, run_detection_months
from app_helper_scripts.csv_helper import *

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
        file = open ('generated_data/' + path)
    except:
        print('Error: no data generated yet')
        return (html.H3('No data generated yet - This could take several minutes'))
    csvreader = csv.reader(file)
    results = []
    for row in csvreader:
        results.append(row)
    accuracy = results[0][0]
    recall = results[0][1]
    precision = results[0][2]
    f1 = results[0][3]

    output = []
    output.append('Accuracy: ' + str(round(float(accuracy)*100,1))+'%\n')
    output.append('Recall: ' + str(round(float(recall)*100,1))+'%\n')
    output.append('Precision: ' + str(round(float(precision)*100,1))+'%\n')
    try:
        output.append('f1 score: ' + str(round(float(f1)*100,1))+'%\n')
    except:
        output.append('f1 score: 0.0%')

    return (html.P([output[0],html.Br(),output[1],html.Br(),output[2],html.Br(),output[3]]))


def save_generated_data(requested_data, detection_data):
    if not os.path.exists('generated_data/' + requested_data):
        os.makedirs('generated_data/' + requested_data)
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_plots.csv', detection_data[0],'w')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_plots.csv', detection_data[1],'a')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detected_outliers.csv', detection_data[2],'w')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_detected_outliers.csv', detection_data[3],'a')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_true_outliers.csv', detection_data[4],'w')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_true_outliers.csv', detection_data[5],'a')
    write_to_csv('generated_data/'+requested_data+'/'+requested_data+'_results.csv', detection_data[6],'w')



def get_detection_data(model, data_to_run, data_coordinates, threshold=0):
    return run_detection(model, data_coordinates, threshold)

def get_detection_data_months(model, data_to_run, data_coordinates, threshold=2):
    return run_detection_months(model, data_coordinates, threshold)

def get_detection_data_hours_known_outliers(model, data_to_run, outliers_csv, threshold=2, interval=10):
    return get_detection_data_known_outliers(model, data_to_run, outliers_csv, threshold, interval, True)

def get_detection_data_known_outliers(model, data_to_run, target_data, threshold, interval=10, split_hours=False):
    requested_data = model + '_' + data_to_run

    detection_data = []

    if (os.path.isdir('generated_data/' + requested_data)):
        #
    
        #

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

        file = open ('generated_data/'+requested_data+'/'+requested_data+'_true_outliers.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            detection_data.append(row)
    else:
        path_to_data = 'resources/'+data_to_run+'.csv'
        if (exists(path_to_data) == False):
            path_to_data = 'resources/cloud_resource_data/'+data_to_run+'.csv'
        if (split_hours):
            detection_data = run_detection_hours_known_outliers(model, path_to_data, target_data, threshold, interval)
        else:
            detection_data = run_detection_known_outliers(model, path_to_data, target_data, threshold)
        save_generated_data(requested_data, detection_data)

    return detection_data




def get_fig_known_outliers(detection_data, data_to_run, model):
    return get_fig(detection_data, data_to_run, model, True)


def get_fig_with_training_points():
    print('')


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