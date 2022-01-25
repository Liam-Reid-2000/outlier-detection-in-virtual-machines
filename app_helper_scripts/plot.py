import datetime
import csv
import pandas as pd
import matplotlib.pyplot as plt
import json

def get_data_coordinates(csv_file_name):
    points_y=[]
    points_x=[]
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        for row in lines:
            try:
                points_y.append(float(row[1]))
                points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("error")
    return pd.DataFrame({'points_x': points_x,'points_y': points_y})


def plot_anomaly_areas(xF, xS):
    plt.axvspan(xF, xS, color = 'red',alpha=0.5)


def plot_anomalies(target_data):
    f = open('resources/combined_windows.json')
    data = json.load(f)
    for i in data[target_data]:
        plot_anomaly_areas(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'),datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'))
    f.close()