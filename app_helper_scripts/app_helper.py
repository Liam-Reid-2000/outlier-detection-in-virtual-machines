import pandas as pd
import csv
import os
import json
from dash import html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from app_helper_scripts.app_detection import run_detection
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


def get_detection_data(model, data_to_run, target_data, threshold):
    requested_data = model + '_' + data_to_run

    detection_data = []

    if (os.path.isdir('generated_data/' + requested_data)):

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
        detection_data = run_detection(model, 'resources/'+data_to_run+'.csv', target_data, threshold)
        save_generated_data(requested_data, detection_data)

    return detection_data




def get_fig(detection_data, data_to_run, model):

    pycaret_plots = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})
    fig = px.line(pycaret_plots, x='timestamp', y='data',title= data_to_run + ' Data against Time (Using '+model+'-based outlier detection)')

    true_outlier_areas = pd.DataFrame({'timestamp1': detection_data[4],'timestamp2': detection_data[5]})
    i = 0
    while (i < len(true_outlier_areas['timestamp1'])):
        fig.add_vrect(x0=true_outlier_areas['timestamp1'][i],x1=true_outlier_areas['timestamp2'][i],fillcolor='red',opacity=0.25,line_width=0)
        i += 1

    detected_outliers = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})
    fig.add_trace(go.Scatter(x=detected_outliers['timestamp'], y=detected_outliers['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))

    fig.update_layout(autotypenumbers='convert types', xaxis_title='Timestamp', yaxis_title='Data')

    return fig