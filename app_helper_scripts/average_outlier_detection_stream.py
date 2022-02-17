import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import csv

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


def get_average(arr):
    total = 0
    count = 0
    for num in arr:
        total = total + num
        count += 1
    return total/count

def get_stream_fig(data_points, has_average, Xavg, Yavg, X, Y):
    # Plot and return the graph
    fig = px.line(data_points, x='points_x', y='points_y')
    if (has_average):
        average_data_points = pd.DataFrame({'points_x': Xavg,'points_y': Yavg})
        fig.add_scatter(x=average_data_points['points_x'], y=average_data_points['points_y'],mode='lines',name='Average')

        
        outliers = detect_average_outliers(25, average_data_points, data_points)
        if (outliers.size>0):
           # scatter trace with medium sized markers
            fig.add_trace(
                go.Scatter(
                    mode='markers',
                    x=outliers['average_outlier_x'],
                    y=outliers['average_outlier_y'],
                    marker=dict(
                        color='LightSkyBlue',
                        size=20,
                        line=dict(
                            color='MediumPurple',
                            width=2
                        )
                    ),
                    showlegend=False
                )
            )

    fig.update_xaxes(range=[min(X),max(X)])
    fig.update_yaxes(range=[min(Y),max(Y)])   
    return fig