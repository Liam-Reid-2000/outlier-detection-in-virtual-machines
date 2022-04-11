from dash import dcc
from dash import html
import dash
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import requests
from collections import deque
from datetime import datetime

from database_scripts.database_helper import database_helper
from app_helper_scripts.config_utilities import config_utlilities
from app_helper_scripts.fig_generator_helper import fig_generator
from app_helper_scripts.app_helper import detection_helper

from ensemble_detectors.ensemble_detection import get_ensemble_detection_data
from som.outlier_detection_som import detect_som_outliers, detect_som_outliers_circle

app = dash.Dash(__name__)

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
                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_real_time_detectors', 'detector_config')],
                            value='full_ensemble'
                        )],style={'width': '25%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div([html.B('Dataset:')],style={'width': '10%', 'display': 'inline-block'}),
                        html.Div([dcc.Dropdown(
                            id='available_data_real_time_detection',
                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets_cloud_resource_data', 'dataset_config')],
                            value='ec2_cpu_utilization_5f5533'
                        )],style={'width': '25%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                    dcc.Graph(id = 'live-graph', animate = True),
                    dcc.Interval(
                        id = 'graph-update',
                        interval = 10000,
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
                                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                            value='full_ensemble'
                                        ),
                                    ],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_health_data',
                                            options=[{'label': i, 'value': i} for i in config_utlilities.get_config('available_datasets_health_data', 'dataset_config')[0]],
                                            value='AnGiang.xlsx'
                                        ),
                                    ],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_health_data_subsets',
                                            options=[{'label': i, 'value': i} for i in config_utlilities.get_config('available_datasets_health_data_subsets', 'dataset_config')[0]],
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
                                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                            value='moving_average'
                                        ),
                                    ],style={'width': '30%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='available_data_cloud_resource_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets_cloud_resource_data', 'dataset_config')],
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
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                        value='svm'
                                    ),
                                ],style={'width': '30%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='available_data',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets', 'dataset_config')],
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
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_supervised_detectors', 'detector_config')],
                                        value='iforest'
                                    ),
                                ],style={'width': '20%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id='available_data_supervised',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets', 'dataset_config')],
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
                        html.H4("Demonstrating SOM outlier detection using 'Minisom' library."),
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
                                options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets_cloud_resource_data', 'dataset_config')],
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

    detection_data = get_ensemble_detection_data(ensemble_detector_list, data, config_utlilities.get_true_outliers(data))
    print('Detection data got - Plotting')
    print('detection data')
    print(detection_data)
    ## return the figure
    fig = fig_generator.get_fig_plot_outliers(detection_data, data, 'moving ensemble')
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
        return detection_helper.get_result_data('ensemble', data)
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
    return detection_helper.get_result_data(detector, data)


@app.callback(
    Output('unsupervised_detection_graph', 'figure'),
    [Input('available_data','value'),
    Input('available_detectors','value')]
)
def plot_graph(data, detector):
    detection_data = detection_helper.get_detection_data_known_outliers(detector, data, config_utlilities.get_true_outliers(data), detection_helper.get_detector_threshold(detector))
    return fig_generator.get_fig_plot_outliers(detection_data, data, detector)

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
    detection_data = detection_helper.get_detection_data_months(detector, dataset + '_' + data_subset, health_data)
    toc = time.perf_counter()
    print(f"Did the detection in {toc - tic:0.4f} seconds")
    return fig_generator.get_fig(detection_data, dataset.replace('.xlsx','') + '_' + data_subset, detector)


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
    detection_data = detection_helper.get_detection_data_known_outliers(detector, data, config_utlilities.get_true_outliers(data), detection_helper.get_detector_threshold(detector)) 
    fig = fig_generator.get_fig_plot_outliers(detection_data, data, detector)
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
    return detection_helper.get_result_data(detector, data)


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
    detection_data = detection_helper.get_detection_data_supervised('supervised_isolation_forest', data, config_utlilities.get_true_outliers(data), float(ratio))
    return fig_generator.get_fig_plot_outliers(detection_data, "speed_7578", "isolation forest", ratio)

@app.callback(
    Output('live-update-results_supervised', 'children'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_results(data, detector, ratio, fig):
    try:
        return detection_helper.get_result_data(detector, data)
    except:
        print('Error when getting results for ' + detector + ' ' + data)

@app.callback(
    Output('supervised_train_test_graph','figure'),
    [Input('available_data_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_results(data, ratio, fig):
    print('not doing')
    return fig_generator.plot_iso_detection_data(float(ratio), data, config_utlilities.get_true_outliers(data))   

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
        print('Error when getting som figure')

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
  
X = deque(maxlen = 50)
X.append(1)

XTime = deque(maxlen = 50)
XTime.append(datetime.now())
  
Y = deque(maxlen = 50)
Y.append(1)

Outliers = deque(maxlen = 50)
Outliers.append(False)

def reset_ques(dataset_name):
    print('swaping dataset_name')
    with open('temp_storage.txt', 'w') as f:
        f.write(dataset_name)
        X.clear()
        X.append(1)
        Y.clear()
        Y.append(1)
        XTime.clear()
        XTime.append(datetime.now())
        Outliers.clear()
        Outliers.append(False)


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals'),
    Input('available_data_real_time_detection','value'),
    Input('available_detectors_real_time_detection', 'value') ]
)
def update_graph_scatter(n,dataset_name, detector_name):
    current_dataset = ''
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    print(current_dataset)
    if (dataset_name != current_dataset):
        reset_ques(dataset_name)

    headers = {'Accept': 'application/json'}
    r = requests.get('http://localhost:8000/' + dataset_name + '/' + str(X[-1]+1), headers=headers)

    X.append(X[-1]+1)
    Y.append(r.json()['cpu_usage'])
    XTime.append(datetime.now())
    confidence = detection_helper.get_real_time_prediction(detector_name, Y)
    if (confidence < 0):
        Outliers.append(True)
    else:
        Outliers.append(False)
    return fig_generator.get_stream_fig(Outliers, XTime, Y)



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
                  marker=dict(colors=colors, line=dict(color='#000000', width=1)))
    return fig


if __name__ == '__main__':
    database_helper.create_database()
    app.run_server()