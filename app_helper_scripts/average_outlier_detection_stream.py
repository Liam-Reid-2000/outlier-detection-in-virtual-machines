import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import csv
from os.path import exists

def detect_average_outliers(threshold, average_points, data_points):
    detected_ouliters_x = []
    detected_ouliters_y = []

    average_points_x = average_points['points_x']
    average_points_y = average_points['points_y']

    points_x = data_points['points_x']
    points_y = data_points['points_y']

    i = 0
    while i < len(average_points_x):
        if ((points_y[i] < average_points_y[i]-threshold) or (points_y[i] > average_points_y[i]+threshold)):
            detected_ouliters_x.append(points_x[i])
            detected_ouliters_y.append(points_y[i])
        i += 1
    return pd.DataFrame({'average_outlier_x': detected_ouliters_x,'average_outlier_y': detected_ouliters_y})


def get_average(arr):
    total = 0
    count = 0
    for num in arr:
        total = total + num
        count += 1
    return total/count

def get_stream_fig(data_points, X, Y):
    # Plot and return the graph
    fig = px.line(data_points, x='points_x', y='points_y')

    fig.update_xaxes(range=[min(X),max(X)])
    fig.update_yaxes(range=[min(Y) - min(Y)*0.5,max(Y) + max(X)*0.5])   
    return fig