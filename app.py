from dash import dcc
from dash import html
import dash
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from collections import deque
from app_helper_scripts.csv_helper import *

from som.outlier_detection_som import detect_som_outliers, detect_som_outliers_circle
from ensemble_detectors.moving_average_median_ensemble import get_ensemble_result
from app_helper_scripts.average_outlier_detection_stream import get_average, get_data_coordinates, get_stream_fig
from app_helper_scripts.app_helper import *

app = dash.Dash(__name__)


dc = get_data_coordinates('resources/speed_7578.csv')
  
X = deque(maxlen = 30)
X.append(1)

Xavg = deque(maxlen = 30)
Xavg.append(1)

points_x = dc['points_x']
points_y = dc['points_y']
  
Y = deque(maxlen = 30)
Y.append(1)

Yavg = deque(maxlen = 30)
Yavg.append(1)

Value = 0



available_detectors_df = pd.read_csv('resources/detectors.csv')
detector_list = available_detectors_df['value']

available_data_df = pd.read_csv('resources/data.csv')
data_list = available_data_df['name']

app.layout = html.Div([
    html.H1('Outlier Detection'),
    
    ### Graph to display classifier detection results ###

    html.Div([
        html.Div([
            html.Div([

                ### Drop down boxes with options for user ###

                html.Div([
                    dcc.Dropdown(
                        id='available_detectors',
                        options=[{'label': i, 'value': i} for i in detector_list],
                        value='svm'
                    ),
                ],style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Dropdown(
                        id='available_data',
                        options=[{'label': i, 'value': i} for i in data_list],
                        value='speed_7578'
                    ),
                ],style={'width': '30%', 'display': 'inline-block'}),
            ]),

            ### The Graph ### 
            dcc.Graph(
                id='pycaret-plots'
            ),
        ],style={'width': '70%', 'display': 'inline-block'}),
        
        ### The detection results as text ###

        html.Div([
            html.H2('Detection Results'),
            html.Button('Refresh Results', id='btn_refresh', n_clicks=0),
            html.Br(),
            html.Br(),
            html.Div([
                html.Div(id='results_title', children='...'),
                html.Div(id='live-update-results')
            ],style={'width': '50%', 'float': 'left', 'display': 'inline-block',"border":"2px black solid"})
        ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),

    ],style={'padding': '10px 5px',"border":"2px black solid"}),

    ### A live update graph demonstrating real time outlier detection ### 

    html.Div([
        html.H2("Live Update Graph"),
        html.H3("Graph demonstrating real-time outlier detection using moving average based outlier detection"),
        html.Div(id='live-update-text'),
        dcc.Graph(id = 'live-graph', animate = True),
        dcc.Interval(
            id = 'graph-update',
            interval = 2400,
            n_intervals=0
        ),
    ],style={"border":"2px black solid"}),


    ### Demonstration of SOM ###

    html.Div([
        html.Div(),
        html.H2("SOM"),
        html.H3("Demonstrating SOM outlier detection using 'Minisom' library, I plan to make an improved version of this algorithm based on 'An Incremental Approach to Outlier Detection in Virtual Machines'"),
        html.Div([
            dcc.Graph(id = 'som-graph')
        ],style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id = 'som-graph-2')
        ],style={'width': '49%', 'display': 'inline-block'}),
    ],style={"border":"2px black solid"}),



    ### A graph demonstrating how weak ensembes are strong outlier detectors ### 

    html.Div([
        html.H2("Ensemble of Detectors"),
        html.H3("Graph demonstrating how an ensemble of weak classifiers are strong outlier detectors"),
        html.H3('Moving Average'),
        dcc.RadioItems(
            id='ensemble-average-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='On',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),
        html.H3('Moving Median'),
        dcc.RadioItems(
            id='ensemble-median-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='On',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),
        dcc.Graph(id = 'ensemble-graph'),
    ],style={"border":"2px black solid"}),
])





@app.callback(
    Output('results_title', 'children'),
    [Input('available_data','value'),
    Input('available_detectors','value')]
)
def update_results_title(data, detector):
    return html.H3(detector.upper() + ' on \'' + data + '\' data')


@app.callback(
    Output('live-update-results', 'children'),
    [Input('available_data','value'),
    Input('available_detectors','value'),
    Input('btn_refresh', 'n_clicks')]
)
def update_results(data, detector, n_clicks):
    try:
        return get_result_data(detector + '_' + data + '/' + detector + '_' + data + '_results.csv')
    except:
        print('Error when getting results')


@app.callback(
    Output('pycaret-plots', 'figure'),
    [Input('available_data','value'),
    Input('available_detectors','value')]
)
def plot_graph(data, detector):
    detection_data = get_detection_data(detector, data, get_outlier_ref(data), get_detector_threshold(detector))
    return get_fig(detection_data, data, detector)



@app.callback(
    Output('ensemble-graph', 'figure'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value')]
)
def update_results_title(average_rd, median_rd):
    if (average_rd == 'Off' and median_rd == 'Off'):
        return go.figure()
    if (average_rd == 'On' and median_rd == 'Off'):
        detection_data = get_detection_data('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', 25)
        return get_fig(detection_data, 'speed_7578.csv', 'moving_average')
    if (average_rd == 'Off' and median_rd == 'On'):
        detection_data = get_detection_data('moving_median', 'speed_7578', 'realTraffic/speed_7578.csv', 34)
        return get_fig(detection_data, 'speed_7578', 'moving_median')
    if (average_rd == 'On' and median_rd == 'On'):
        
        average_detection_data = get_detection_data('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', 25)
        median_detection_data = get_detection_data('moving_median', 'speed_7578', 'realTraffic/speed_7578.csv', 34)
        
        average_outliers_x = average_detection_data[2]
        average_outliers_y = average_detection_data[3]

        average_outliers = pd.DataFrame({'timestamp': average_outliers_x,'data': average_outliers_y})

        median_outliers_x = median_detection_data[2]
        median_outliers_y = median_detection_data[3]

        median_outliers = pd.DataFrame({'timestamp': median_outliers_x, 'data': median_outliers_y})

        ensemble_outliers = get_ensemble_result(average_outliers, median_outliers)

        average_detection_data[2] = ensemble_outliers['timestamp']
        average_detection_data[3] = ensemble_outliers['data']

        return get_fig(average_detection_data, 'speed_7578', 'moving median and average ensemble')




@app.callback(Output('live-update-text', 'children'),
              Input('graph-update', 'n_intervals'))
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Value: ' + str(points_y[X[-1]+1]), style=style)
    ]



@app.callback(
    Output('som-graph', 'figure'),
    [ Input('btn_refresh', 'n_clicks') ]
)
def update_graph_scatter(n):
    som_detection_data = detect_som_outliers()
    outliers_x = som_detection_data[0]
    outliers_y = som_detection_data[1]
    inliers_x = som_detection_data[2]
    inliers_y = som_detection_data[3]

    fig = px.scatter(x=inliers_x,y=inliers_y,title='SOM Outlier Detection for Clustered Data')
    fig.add_scatter(x=outliers_x,y=outliers_y,mode='markers',name='Outliers')

    return fig

@app.callback(
    Output('som-graph-2', 'figure'),
    [ Input('btn_refresh', 'n_clicks') ]
)
def update_graph_scatter(n):
    som_detection_data = detect_som_outliers_circle()
    outliers_x = som_detection_data[0]
    outliers_y = som_detection_data[1]
    inliers_x = som_detection_data[2]
    inliers_y = som_detection_data[3]

    fig = px.scatter(x=inliers_x,y=inliers_y,title='SOM Outlier Detection for Data appearing Circular')
    fig.add_scatter(x=outliers_x,y=outliers_y,mode='markers',name='Outliers')

    return fig



  
@app.callback(
    Output('live-graph', 'figure'),
    [ Input('graph-update', 'n_intervals') ]
)
def update_graph_scatter(n):
    X.append(X[-1]+1)
    Y.append(points_y[X[-1]+1])
    points_y[X[-1]+1]

    data_points = pd.DataFrame({'points_x': X,'points_y': Y})
    has_average = False
    average = 0

    if(X[-1]+1 > 5):
        arr = []
        i = 0
        while(i < 5):
            arr.append(points_y[X[-1]+1 - i])
            has_average = True
            i += 1
        average = get_average(arr)
        Xavg.append(X[-1])
        Yavg.append(average)

    return get_stream_fig(data_points, has_average, Xavg, Yavg, X)

if __name__ == '__main__':
    app.run_server()