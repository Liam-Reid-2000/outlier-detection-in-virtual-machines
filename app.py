from dash import dcc
from dash import html
import dash
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
from collections import deque
from app_helper_scripts.csv_helper import *
import json
from ensemble_detectors.ensemble_detection import get_ensemble_detection_data

from som.outlier_detection_som import detect_som_outliers, detect_som_outliers_circle
from app_helper_scripts.average_outlier_detection_stream import get_average, get_data_coordinates, get_stream_fig
from app_helper_scripts.app_helper import *
from supervised_learning_detectors.isolation_forest import do_isolation_forest_detection

app = dash.Dash(__name__)

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
    html.H1('Outlier Detection'),


    ##################### HEALTH DATA TESTING SPACE ##########################

    html.Div([
        html.H2('Health Data Experimental Space'),
            html.Div([
                html.Div([

                    ### Drop down boxes with options for user ###

                    html.Div([
                        dcc.Dropdown(
                            id='available_detectors_health_data',
                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                            value='moving_average'
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
                    id='plots_health_data'
                ),
            ],style={'width': '70%', 'display': 'inline-block'}),

        ],style={'padding': '10px 5px',"border":"2px black solid"}),



    ##################### CLOUD RESOURCE DATA TESTING SPACE ##########################

    html.Div([
        html.H2('Cloud Resource Experimental Space'),
            html.Div([
                html.Div([

                    ### Drop down boxes with options for user ###

                    html.Div([
                        dcc.Dropdown(
                            id='available_detectors_cloud_resource_data',
                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_detectors')],
                            value='moving_average'
                        ),
                    ],style={'width': '20%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='available_data_cloud_resource_data',
                            options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets_cloud_resource_data')],
                            value='ec2_cpu_utilization_fe7f93'
                        ),
                    ],style={'width': '20%', 'display': 'inline-block'}),
                ]),

                ### The Graph ### 
                dcc.Graph(
                    id='graph_cloud_resource_data'
                ),
            ],style={'width': '70%', 'display': 'inline-block'}),

        ],style={'padding': '10px 5px',"border":"2px black solid"}),
    




    ### Graph to display classifier detection results ###

    html.Div([
        html.H2('Unsupervised Detection'),
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



    ### Graph to display classifier detection results using supervised training ###

    html.Div([
        html.H2('Supervised Detection'),
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
                id='supervised-plots_supervised'
            ),
        ],style={'width': '70%', 'display': 'inline-block'}),
        
        ### The detection results as text ###

        html.Div([
            html.H2('Detection Results'),
            html.Button('Refresh Results', id='btn_refresh_supervised', n_clicks=0),
            html.Button('Show Learning', id='btn_show_supervised', n_clicks=0),
            html.Br(),
            html.Br(),
            html.Div([
                html.Div(id='results_title_supervised', children='...'),
                html.Div(id='live-update-results_supervised')
            ],style={'width': '50%', 'float': 'left', 'display': 'inline-block',"border":"2px black solid"})
        ],style={'width': '29%', 'float': 'right', 'display': 'inline-block'}),
        ### The Graph ### 
            dcc.Graph(
                id='supervised_plots_supervised_learning'
            ),
    ],style={'padding': '10px 5px',"border":"2px black solid"}),



    ### A live update graph demonstrating real time outlier detection ### 

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='available_data_real_time_detection',
                options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets')],
                value='speed_7578'
            ),
        ],style={'width': '20%', 'display': 'inline-block'}),
        html.H2("Live Update Graph"),
        html.H3("Graph demonstrating real-time outlier detection using moving average based outlier detection"),
        dcc.Graph(id = 'live-graph', animate = True),
        dcc.Interval(
            id = 'graph-update',
            interval = 300000,
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

        html.Div([

            ### Drop down boxes with options for user ###
            html.Div([
                dcc.Dropdown(
                    id='available_data_ensemble',
                    options=[{'label': i[0], 'value': i[0]} for i in get_config('available_datasets')],
                    value='speed_7578'
                ),
            ],style={'width': '20%', 'display': 'inline-block'}),
        ]),
        
        # Moving Average
        html.H3('Moving Average'),
        dcc.RadioItems(
            id='ensemble-average-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='Off',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),

        # Moving Median
        html.H3('Moving Median'),
        dcc.RadioItems(
            id='ensemble-median-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='Off',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),

        # Moving Boxplot
        html.H3('Moving Boxplot'),
        dcc.RadioItems(
            id='ensemble-boxplot-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='Off',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),

        # Moving Histogram
        html.H3('Moving Histogram'),
        dcc.RadioItems(
            id='ensemble-histogram-radio-btns',
            options=[{'label': i, 'value': i} for i in ['On', 'Off']],
            value='Off',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),

        # Graph
        dcc.Graph(id = 'ensemble-graph'),
        html.Div([
            html.H2('Ensemble Detection Results'),
            html.Button('Refresh Results', id='btn_refresh_ensemble', n_clicks=0),
            html.Br(),
            html.Br(),
            html.Div([
                html.Div(id='live-update-results_ensemble')
            ],)
        ],),
    ],style={"border":"2px black solid"}),
])


@app.callback(
    Output('live-update-results_ensemble', 'children'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value'),
    Input('ensemble-boxplot-radio-btns','value'),
    Input('ensemble-histogram-radio-btns','value'),
    Input('btn_refresh_ensemble', 'n_clicks')]
)
def update_results(average_rad, median_rad, boxplot_rad, histogram_rad, n_clicks):
    try:
        return get_result_data('ensemble/ensemble_results.csv')
    except:
        print('Error when getting results')
        

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
    #if (detector == 'full_ensemble'):
    #    detection_data = detect__outliers_full_ensemble(data, get_outlier_ref(data))
    #else:
    #    detection_data = get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))
    detection_data = get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))
    return get_fig_known_outliers(detection_data, data, detector)


################################

# HEALTH DATA


@app.callback(
    Output('plots_health_data', 'figure'),
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
    detection_data = get_detection_data_months(detector, dataset + '_' + data_subset, health_data)
    return get_fig(detection_data, dataset + '_' + data_subset, detector)


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
    return get_fig_known_outliers(detection_data, data, detector)


# CLOUD RESOURCE DATA

################################

####################################################################################

### SUPERVISED LEARNING ###

@app.callback(
    Output('supervised-plots_supervised', 'figure'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value')]
)
def plot_graph(data, detector,ratio):
    detection_data = do_isolation_forest_detection(float(ratio), 'resources/' + data + '.csv', get_outlier_ref(data), False)
    return get_fig_known_outliers(detection_data, "speed", "isolation forest")

@app.callback(
    Output('live-update-results_supervised', 'children'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('btn_refresh_supervised', 'n_clicks'),
    Input('supervised_test_train_split_ratio', 'value')]
)
def update_results(data, detector, n_clicks, ratio):
    try:
        return get_result_data('supervised_histogram_'+ratio+'/supervised_histogram_'+ratio+'_results.csv')
    except:
        print('Error when getting results')

@app.callback(
    Output('supervised_plots_supervised_learning','figure'),
    [Input('available_data_supervised','value'),
    Input('btn_show_supervised', 'n_clicks'),
    Input('supervised_test_train_split_ratio', 'value')]
)
def update_results(data, n_clicks, ratio):
    return do_isolation_forest_detection(float(ratio), 'resources/' + data + '.csv', get_outlier_ref(data), True)

        

### SUPERVISED LEARNING ###

####################################################################################



@app.callback(
    Output('ensemble-graph', 'figure'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value'),
    Input('ensemble-histogram-radio-btns','value'),
    Input('ensemble-boxplot-radio-btns','value'),
    Input('available_data_ensemble','value')]
)
def update_results_title(average_rd, median_rd, histogram_rd, boxplot_rd, data):

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

    ## return the figure
    return get_fig_known_outliers(detection_data, data, 'moving ensemble')



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
        print('Error creating SOM fig')

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

#######################################################################################
  
X = deque(maxlen = 30)
X.append(1)
Xavg = deque(maxlen = 30)
Xavg.append(1)
  
Y = deque(maxlen = 30)
Y.append(1)
Yavg = deque(maxlen = 30)
Yavg.append(1)

Current_Data = ''

@app.callback(
    Output('live-graph', 'figure'),
    [ Input('graph-update', 'n_intervals'),
    Input('available_data_real_time_detection','value') ]
)
def update_graph_scatter(n,data):


    dc = get_data_coordinates('resources/'+data+'.csv')
    points_x = dc['points_x']
    points_y = dc['points_y']


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
    try:
        return get_stream_fig(data_points, has_average, Xavg, Yavg, X, Y)
    except:
        print('Problem with stream graph')

if __name__ == '__main__':
    app.run_server()