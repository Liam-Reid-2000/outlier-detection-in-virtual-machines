from dash import dcc
from dash import html
import dash
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import deque
from app_helper_scripts.csv_helper import *
import json
from ensemble_detectors.ensemble_detection import get_ensemble_detection_data
import time
import requests
from ensemble_detectors.moving_average_detection import moving_average_detection
from ensemble_detectors.moving_median_detection import moving_median_detection

from som.outlier_detection_som import detect_som_outliers, detect_som_outliers_circle
from app_helper_scripts.average_outlier_detection_stream import get_average, get_stream_fig
from app_helper_scripts.app_helper import *
from supervised_learning_detectors.isolation_forest import do_isolation_forest_detection

app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#logging.basicConfig(level=logging.DEBUG)

def get_config(requested_config):
    f = open('resources/config.json',)
    data = json.load(f) 
    requested_config_list = []
    for i in data[requested_config]:
        requested_config_list.append(i)
    # Closing file
    f.close()
    return requested_config_list
 

app.layout = html.Div([
    html.H1('Outlier Detection Dashboard'),
    dcc.Tabs([
        dcc.Tab(label='Real Time Detection', children=[
            ### A live update graph demonstrating real time outlier detection ### 

            html.Div([
                html.H4("Live Update Graph"),
                html.Div([
                    html.P("Graph demonstrating real-time outlier detection using moving average based outlier detection"),
                    html.Div([
                        html.Div([html.B('Detector:')],style={'width': '10%', 'display': 'inline-block'}),
                        html.Div([dcc.Dropdown(
                            id='available_detectors_real_time_detection',
                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                            value='ec2_cpu_utilization_5f5533'
                        )],style={'width': '25%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div([html.B('Dataset:')],style={'width': '10%', 'display': 'inline-block'}),
                        html.Div([dcc.Dropdown(
                            id='available_data_real_time_detection',
                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets_cloud_resource_data')],
                            value='ec2_cpu_utilization_5f5533'
                        )],style={'width': '25%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                    dcc.Graph(id = 'live-graph', animate = True),
                    dcc.Interval(
                        id = 'graph-update',
                        interval = 5000,
                        n_intervals=0
                    ),
                ],style={'width': '70%', 'display': 'inline-block'}),

                html.Div([
                    html.H4('CPU Usage'),
                    dcc.Graph(id='cpu_usage_pie_chart'),
                ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),

            ],style={"border":"2px black solid"}),
        ]),
        dcc.Tab(label='Experimental Space', children=[

            dcc.Tabs([
                dcc.Tab(label='Dengue Fever Experiment', children=[
            
                    ##################### Dengue Fever Data DATA TESTING SPACE ##########################

                    html.Div([
                        html.H4('Dengue Fever Data Experimental Space'),
                            html.Div([
                                html.Div([

                                    ### Drop down boxes with options for user ###

                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_detectors_health_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                                            value='full_ensemble'
                                        ),
                                    ],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_health_data',
                                            options=[{'label': i, 'value': i} for i in get_config('available_datasets_health_data')[0]],
                                            value='AnGiang.xlsx'
                                        ),
                                    ],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_health_data_subsets',
                                            options=[{'label': i, 'value': i} for i in get_config('available_datasets_health_data_subsets')[0]],
                                            value='Average_temperature'
                                        ),
                                    ],style={'width': '20%', 'display': 'inline-block'}),
                                ]),

                                ### The Graph ### 
                                dcc.Graph(
                                    id='dengue_fever_graph'
                                ),
                            ],style={'width': '70%', 'display': 'inline-block'}),

                        ],style={'padding': '10px 5px',"border":"2px black solid"}),
                ]),
                dcc.Tab(label='Cloud Resource Usage Experiment', children=[


                    ##################### CLOUD RESOURCE DATA TESTING SPACE ##########################

                    html.Div([
                        html.H4('Cloud Resource Experimental Space'),
                            html.Div([
                                html.Div([

                                    ### Drop down boxes with options for user ###

                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_detectors_cloud_resource_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                                            value='moving_average'
                                        ),
                                    ],style={'width': '30%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_cloud_resource_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets_cloud_resource_data')],
                                            value='ec2_cpu_utilization_5f5533'
                                        ),
                                    ],style={'width': '30%', 'display': 'inline-block'}),
                                ]),

                                ### The Graph ### 
                                dcc.Graph(
                                    id='graph_cloud_resource_data'
                                ),
                            ],style={'width': '70%', 'display': 'inline-block'}),

                            ### The detection results as text ###

                            html.Div([
                                html.H4('Detection Results'),
                                html.Br(),
                                html.Br(),
                                html.Div([
                                    html.Div(id='results_title_cloud_resource', children='...'),
                                    html.Div(id='live_update_results_cloud_resource')
                                ],style={'width': '50%', 'float': 'left', 'display': 'inline-block',"border":"2px black solid"})
                            ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),

                        ],style={'padding': '10px 5px',"border":"2px black solid"}),
                    
                ]),

                dcc.Tab(label='Unsupervised Detection', children=[

                    ### Graph to display classifier detection results for unsupervised methods ###

                    html.Div([
                        html.H4('Unsupervised Detection'),
                        html.Div([
                            html.Div([

                                ### Drop down boxes with options for user ###

                                html.Div([
                                    dcc.Dropdown(
                                        id='available_detectors',
                                        options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                                        value='svm'
                                    ),
                                ],style={'width': '30%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='available_data',
                                        options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets')],
                                        value='speed_7578'
                                    ),
                                ],style={'width': '30%', 'display': 'inline-block'}),
                            ]),

                            ### The Graph ### 
                            dcc.Graph(
                                id='unsupervised_detection_graph'
                            ),
                        ],style={'width': '70%', 'display': 'inline-block'}),
                        
                        ### The detection results as text ###

                        html.Div([
                            html.H4('Detection Results'),
                            html.Button('Refresh Results', id='btn_refresh', n_clicks=0),
                            html.Br(),
                            html.Br(),
                            html.Div([
                                html.Div(id='results_title', children='...'),
                                html.Div(id='live-update-results')
                            ],style={'width': '50%', 'float': 'left', 'display': 'inline-block',"border":"2px black solid"})
                        ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),

                    ],style={'padding': '10px 5px',"border":"2px black solid"}),
                ]),
                dcc.Tab(label='Supervised Detection', children=[

                   ### Graph to display classifier detection results using supervised training ###

                    html.Div([
                        html.H4('Supervised Detection'),
                        html.Div([
                            html.Div([

                                ### Drop down boxes with options for user ###

                                html.Div([
                                    dcc.Dropdown(
                                        id='available_detectors_supervised',
                                        options=[{'label': i[0], 'value': i[0]} for i in get_config('available_supervised_detectors')],
                                        value='iforest'
                                    ),
                                ],style={'width': '20%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='available_data_supervised',
                                        options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets')],
                                        value='speed_7578'
                                    ),
                                ],style={'width': '20%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Textarea(
                                        id='supervised_test_train_split_ratio',
                                        value='0.75',
                                        style={'width': '100%', 'height': '100%'},
                                    ),
                                ],style={'width': '20%', 'display': 'inline-block'}),
                            ]),

                            ### The Graph ### 
                            dcc.Graph(
                                id='supervised_learning_graph'
                            ),
                        ],style={'width': '70%', 'display': 'inline-block'}),
                        
                        ### The detection results as text ###

                        html.Div([
                            html.H4('Detection Results'),
                            html.B('Supervised Detection Results'),
                            html.Br(),
                            html.Br(),
                            html.Div([
                                html.Div(id='results_title_supervised', children='...'),
                                html.Div(id='live-update-results_supervised')
                            ],style={'width': '50%', 'float': 'left', 'display': 'inline-block',"border":"2px black solid"})
                        ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),
                        ### The Graph ### 
                            dcc.Graph(
                                id='supervised_train_test_graph'
                            ),
                    ],style={'padding': '10px 5px',"border":"2px black solid"}),

                ]),
                dcc.Tab(label='SOM', children=[
                    ### Demonstration of SOM ###

                    html.Div([
                        html.Div(),
                        html.H4("SOM"),
                        html.H4("Demonstrating SOM outlier detection using 'Minisom' library, I plan to make an improved version of this algorithm based on 'An Incremental Approach to Outlier Detection in Virtual Machines'"),
                        html.Div([
                            dcc.Graph(id = 'som-graph')
                        ],style={'width': '49%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Graph(id = 'som-graph-2')
                        ],style={'width': '49%', 'display': 'inline-block'}),
                    ],style={"border":"2px black solid"}),
                ]),

                dcc.Tab(label='Ensemble Testing Space', children=[
                    ### A graph demonstrating how weak ensembes are strong outlier detectors ### 
                    html.Div([
                        html.Div([
                            html.H4("Ensemble of Detectors"),
                            html.B("Graph demonstrating how an ensemble of weak classifiers are strong outlier detectors"),
                        ],style={'width': '100%'}),
                        ### Drop down boxes with options for user ###
                        html.Div([
                            html.Div([html.B('Dataset:')],style={'width': '30%'}),
                            html.Div([dcc.Dropdown(
                                id='available_data_ensemble',
                                options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets_cloud_resource_data')],
                                value='ec2_cpu_utilization_5f5533'
                            )],style={'width': '100%'}),

                            # Moving Average
                            html.B('Moving Average'),
                            dcc.RadioItems(
                                id='ensemble-average-radio-btns',
                                options=[{'label': i, 'value': i} for i in ['On', 'Off']],
                                value='Off',
                                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                            ),

                            # Moving Median
                            html.B('Moving Median'),
                            dcc.RadioItems(
                                id='ensemble-median-radio-btns',
                                options=[{'label': i, 'value': i} for i in ['On', 'Off']],
                                value='Off',
                                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                            ),

                            # Moving Boxplot
                            html.B('Moving Boxplot'),
                            dcc.RadioItems(
                                id='ensemble-boxplot-radio-btns',
                                options=[{'label': i, 'value': i} for i in ['On', 'Off']],
                                value='Off',
                                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                            ),

                            # Moving Histogram
                            html.B('Moving Histogram'),
                            dcc.RadioItems(
                                id='ensemble-histogram-radio-btns',
                                options=[{'label': i, 'value': i} for i in ['On', 'Off']],
                                value='Off',
                                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                            ),
                        ],style={'width': '30%', 'display': 'inline-block'}),
                        html.Div([
                            html.B('Ensemble Detection Results'),
                            html.Br(),
                            html.Br(),
                            html.Div([
                                html.Div(id='live-update-results_ensemble')
                            ]),
                        ],style={'width': '30%', 'display': 'inline-block', "border":"2px black solid"}),
                        html.Div([
                            # Graph
                            dcc.Graph(id = 'ensemble-graph'),
                        ]),
                    ],style={"border":"2px black solid"}),
                ]),
            ]),
        ]),
    ])
])

###########################################################################
################### Ensemble 

@app.callback(
    Output('ensemble-graph', 'figure'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value'),
    Input('ensemble-histogram-radio-btns','value'),
    Input('ensemble-boxplot-radio-btns','value'),
    Input('available_data_ensemble','value')]
)
def update_ensemble_graph(average_rd, median_rd, histogram_rd, boxplot_rd, data):

    ensemble_detector_list = []

    # Check which detectors user has selected
    if (average_rd == 'On'):
        ensemble_detector_list.append('moving_average')
    if (median_rd == 'On'):
        ensemble_detector_list.append('moving_median')
    if (boxplot_rd == 'On'):
        ensemble_detector_list.append('moving_boxplot')
    if (histogram_rd == 'On'):
        ensemble_detector_list.append('moving_histogram')

    detection_data = get_ensemble_detection_data(ensemble_detector_list, data, get_outlier_ref(data))
    print('Detection data got - Plotting')
    print('detection data')
    print(detection_data)
    ## return the figure
    fig = get_fig_plot_outliers(detection_data, data, 'moving ensemble')
    return fig


@app.callback(
    Output('live-update-results_ensemble', 'children'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value'),
    Input('ensemble-boxplot-radio-btns','value'),
    Input('ensemble-histogram-radio-btns','value'),
    Input('available_data_ensemble','value'),
    Input('ensemble-graph', 'figure')]
)
def update_results(average_rad, median_rad, boxplot_rad, histogram_rad, data, fig):
    try:
        return get_result_data('ensemble', data)
    except:
        print('Error when getting results')

###########################################################################
        

###########################################################################
##################### UNSUPERVISED DETECTION
@app.callback(
    Output('results_title', 'children'),
    [Input('available_data','value'),
    Input('available_detectors','value'),
    Input('unsupervised_detection_graph', 'figure')]
)
def update_results_title(data, detector, fig):
    return html.H4(detector.upper() + ' on \'' + data + '\' data')


@app.callback(
    Output('live-update-results', 'children'),
    [Input('available_data','value'),
    Input('available_detectors','value'),
    Input('btn_refresh', 'n_clicks'),
    Input('unsupervised_detection_graph', 'figure')]
)
def update_results(data, detector, n_clicks, fig):
    return get_result_data(detector, data)


@app.callback(
    Output('unsupervised_detection_graph', 'figure'),
    [Input('available_data','value'),
    Input('available_detectors','value')]
)
def plot_graph(data, detector):
    detection_data = get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))
    return get_fig_plot_outliers(detection_data, data, detector)

##################### UNSUPERVISED DETECTION
###########################################################################


################################
# HEALTH DATA


@app.callback(
    Output('dengue_fever_graph', 'figure'),
    [Input('available_detectors_health_data','value'),
    Input('available_data_health_data_subsets','value'),
    Input('available_data_health_data','value')]
)
def plot_graph(detector, data_subset, dataset):
    file = 'resources/health_data/' + dataset
    data = pd.read_excel(file)
    timestamp = data['year_month']
    data = data[data_subset]
    health_data = pd.DataFrame({'timestamp':timestamp,'data':data})
    tic = time.perf_counter()
    detection_data = get_detection_data_months(detector, dataset + '_' + data_subset, health_data)
    toc = time.perf_counter()
    print(f"Did the detection in {toc - tic:0.4f} seconds")
    return get_fig(detection_data, dataset.replace('.xlsx','') + '_' + data_subset, detector)


# HEALTH DATA
################################

################################
# CLOUD RESOURCE DATA

@app.callback(
    Output('graph_cloud_resource_data', 'figure'),
    [Input('available_detectors_cloud_resource_data','value'),
    Input('available_data_cloud_resource_data','value')]
)
def plot_graph(detector, data):
    detection_data = get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector)) 
    fig = get_fig_plot_outliers(detection_data, data, detector)
    return fig


@app.callback(
    Output('results_title_cloud_resource', 'children'),
    [Input('available_data_cloud_resource_data','value'),
    Input('available_detectors_cloud_resource_data','value'),
    Input('graph_cloud_resource_data', 'figure')]
)
def update_results_title(data, detector, fig):
    return html.H4(detector.upper() + ' on \'' + data + '\' data')


@app.callback(
    Output('live_update_results_cloud_resource', 'children'),
    [Input('available_data_cloud_resource_data','value'),
    Input('available_detectors_cloud_resource_data','value'),
    Input('graph_cloud_resource_data', 'figure')]
)
def update_results(data, detector, fig):
    return get_result_data(detector, data)


# CLOUD RESOURCE DATA
################################

####################################################################################
### SUPERVISED LEARNING ###

@app.callback(
    Output('supervised_learning_graph', 'figure'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value')]
)
def plot_graph(data, detector, ratio):
    detection_data = do_isolation_forest_detection(float(ratio), 'resources/' + data + '.csv', get_outlier_ref(data), False)
    return get_fig_plot_outliers(detection_data, "speed_7578", "isolation forest", ratio)

@app.callback(
    Output('live-update-results_supervised', 'children'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_results(data, detector, ratio, fig):
    try:
        return get_result_data(detector, data)
    except:
        print('Error when getting results for ' + detector + ' ' + data)

@app.callback(
    Output('supervised_train_test_graph','figure'),
    [Input('available_data_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_results(data, ratio, fig):
    return do_isolation_forest_detection(float(ratio), 'resources/' + data + '.csv', get_outlier_ref(data), True)   

### SUPERVISED LEARNING ###
####################################################################################


###################################################
## SOM

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
    try:
        fig = px.scatter(x=inliers_x,y=inliers_y,title='SOM Outlier Detection for Clustered Data')
        fig.add_scatter(x=outliers_x,y=outliers_y,mode='markers',name='Outliers')
        return fig
    except:
        print('Error when getting results')
        #logging.error('Error creating SOM fig')

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

## SOM
###################################################

#######################################################################################
####### REAL TIME STREAMING DATA #######
  
X = deque(maxlen = 30)
X.append(1)
Xavg = deque(maxlen = 30)
Xavg.append(1)
  
Y = deque(maxlen = 30)
Y.append(1)
Yavg = deque(maxlen = 30)
Yavg.append(1)

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'),
    Input('available_data_real_time_detection','value') ]
)
def update_graph_scatter(n,data):

    headers = {'Accept': 'application/json'}
    r = requests.get('http://localhost:8000/ec2_cpu_utilization_5f5533/' + str(X[-1]+1), headers=headers)

    X.append(X[-1]+1)
    Y.append(r.json()['cpu_usage'])

    data_points = pd.DataFrame({'points_x': X,'points_y': Y})

    moving_average_prediction = moving_average_detection.real_time_prediction(Y, Y[len(Y)-1])
    print('Moving average predicts: ' + str(moving_average_prediction))

    moving_median_prediciton = moving_median_detection.real_time_prediction(Y, Y[len(Y)-1])
    print('Moving median predicts: ' + str(moving_median_prediciton))

    try:
        return get_stream_fig(data_points, X, Y)
    except:
        print('Error with stream graph')

@app.callback(
    Output('cpu_usage_pie_chart', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def generate_pie_chat(n):
    colors = ['green', 'red']
    labels = ['Available', 'In use']
    values = [100-Y[len(Y)-1], Y[len(Y)-1]]
    fig = go.Figure(data=[go.Pie(labels=labels,values=values)])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    return fig


if __name__ == '__main__':
    database_helper.create_database()
    app.run_server()