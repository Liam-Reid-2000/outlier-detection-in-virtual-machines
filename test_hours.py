import csv
from datetime import datetime
import pandas as pd
import plotly.express as px

from app_helper_scripts.app_detection import split_data_to_hours
from app_helper_scripts.app_helper import get_detection_data_hours_known_outliers, get_fig_known_outliers, save_generated_data

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

cpu_df = load_data_coordinates('resources/cloud_resource_data/ec2_cpu_utilization_5f5533.csv')

#print(cpu_df)

#cpu_dfs_split_hours = split_data_to_hours(cpu_df['timestamp'], cpu_df['data'])

detector = 'moving_average'
data = cpu_df
outlier_ref = 'realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv'

detection_data = get_detection_data_hours_known_outliers(detector, data, outlier_ref, 2) 
save_generated_data('moving_average' + '_'+ 'ec2_cpu_utilization_5f5533.csv', detection_data)
fig = get_fig_known_outliers(detection_data, 'ec2_cpu_utilization_5f5533.csv', detector)

#pycaret_plots = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})

#fig = px.line(pycaret_plots, x='timestamp', y='data',title= 'cpu' + ' Data against Time (Using '+'ach'+'-based outlier detection)')
fig.show()