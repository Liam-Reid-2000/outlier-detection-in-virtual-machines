from dash import dcc
from dash import html
from dash import dash_table
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

box_info_style = {'width': '20%', 'display': 'inline-block', 'border':'2px black solid', 'margin-left':'50px', 'background-color':'white','border-radius':'20px', 'padding': '7px'}
box_info_style_extended = {'width': '20%', 'display': 'inline-block', 'border':'2px black solid', 'margin-left':'50px', 'background-color':'white','border-radius':'20px', 'padding': '7px'}
dropdown_box_style = {'width': '30%', 'display': 'inline-block', 'border':'2px black solid', 'background-color':'white','border-radius':'25px', 'padding': '10px', 'margin-bottom':'20px'}
dropdown_box_style_full = {'width': '100%', 'display': 'inline-block', 'border':'2px black solid', 'background-color':'white','border-radius':'25px', 'padding': '10px', 'margin-bottom':'20px'}
dropdown_box_with_margin = {'width': '30%', 'display': 'inline-block', 'border':'2px black solid', 'background-color':'white','border-radius':'25px', 'padding': '10px', 'margin-bottom':'20px','margin-right':'20px'}
graph_style = {'border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white'}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
table_style={
    'backgroundColor': '#82a5a3',
    'fontWeight': 'bold'
}

app.title = 'Outlier Detection Dashboard'
app.layout = html.Div([
    html.Img(src='assets/icon.png'),
    html.H1('Outlier Detection Dashboard',style={'display':'inline-block'}),
    dcc.Interval(
        id = 'graph-update',
        interval = 1000*300,
        n_intervals=0
    ),
    dcc.Tabs([
        dcc.Tab(label='Real Time Detection', children=[
            ### A live update graph demonstrating real time outlier detection ### 

            html.Div([
                html.H4("Real Time Outlier Detection"),
                html.P("Data streamed and outliers detected in real time."),
                
                html.Div([
                    html.Div([
                        html.Div([html.B('Detector:')],style={'width': '20%', 'display': 'inline-block'}),
                        html.Div([dcc.Dropdown(
                            id='available_detectors_real_time_detection',
                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_real_time_detectors', 'detector_config')],
                            value='full_ensemble'
                        )],style={'width': '80%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div([html.B('Dataset:')],style={'width': '20%', 'display': 'inline-block'}),
                        html.Div([dcc.Dropdown(
                            id='available_data_real_time_detection',
                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets_cloud_resource_data', 'dataset_config')],
                            value='ec2_cpu_utilization_5f5533'
                        )],style={'width': '80%', 'display': 'inline-block'}),
                    ],style={'width': '100%', 'display': 'inline-block'}),
                ],style=dropdown_box_style),
                html.Div([
                    html.Div(id='real_time_stream_status',style=box_info_style),
                    html.Div(id='real_time_data_behaviour_status',style=box_info_style),
                    html.Div(id='real_time_stream_last_update_time',style=box_info_style),
                    html.Div(id='real_time_stream_session_start',style=box_info_style),
                ],style={'width': '70%', 'display': 'inline-block', 'padding': '10px', 'margin-bottom':'20px'}),

                html.Div([
                    html.Div([
                        html.Div([html.H4(id='live-graph-update-title')],style={'textAlign': 'center'}),
                        dcc.Graph(id = 'live-graph', animate = True),
                    ], style=graph_style),
                ],style={'width': '70%', 'display': 'inline-block'}),

                html.Div([
                    html.H4('CPU Usage'),
                    dcc.Graph(id='cpu_usage_pie_chart'),
                ],style={'width': '29%', 'float': 'right', 'display': 'inline-block', 'border':'2px black solid', 'background-color':'white','border-radius':'25px', 'padding': '10px'}),
                html.Div(),
                html.Div([
                    html.H4('Outlier Data'),
                    html.Div(id='cpu_usage_dataset_title'),
                    dash_table.DataTable(
                        id='real_time_outlier_data',
                        data = pd.DataFrame({'timestamp':[],'data':[]}).to_dict('records'),
                        columns = [{'name':i, 'id':i} for i in {'timestamp', 'data'}],
                        style_header=table_style,
                    ),
                ],style={'width': '30%', 'display': 'inline-block','border-radius':'25px', 'padding': '10px', 'margin-bottom':'20px'}),
                html.Div([
                    html.Div(id='real_time_outlier_count',style=box_info_style_extended),
                    html.Div(id='real_time_data_outlier_status',style=box_info_style_extended),
                    html.Div([
                        html.Button('Reset session data', id='session-restart-btn', n_clicks=0,style={'border':'2px black solid', 'margin-left':'50px', 'background-color':'white','border-radius':'20px', 'padding': '7px'})
                    ],style={'width': '20%', 'display': 'inline-block'}),
                ],style={'width': '70%', 'display': 'inline-block', 'margin-top':'20px', 'padding': '10px', 'margin-bottom':'20px'}),

            ],style={"border":"2px black solid"}),
        ]),





        dcc.Tab(label='Experimental Space', children=[

            dcc.Tabs([
            
                dcc.Tab(label='Unsupervised Detection', children=[

                    ### Graph to display classifier detection results for unsupervised methods ###

                    html.Div([
                        html.H4('Unsupervised Detection'),
                        html.Div([
                            ### Drop down boxes with options for user ###
                            html.Div([
                                html.Div([
                                    html.Div([html.B('Detector:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_detectors',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                        value='svm'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style={'width': '100%', 'display': 'inline-block'}),
                                html.Div([
                                    html.Div([html.B('Dataset:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_data',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets', 'dataset_config')],
                                        value='speed_7578'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style={'width': '100%', 'display': 'inline-block'}),
                            ],style=dropdown_box_style_full),
                            html.Div([
                                html.H4('Detection Results'),
                                html.Div(id='unsupervised_detection_results_title', children='...'),
                                dash_table.DataTable(
                                    id='unsupervised_detection_results',
                                    data = pd.DataFrame({'Evaluation_Metric':[],'Result':[]}).to_dict('records'),
                                    columns = [{'name':i, 'id':i} for i in {'Evaluation_Metric', 'Result'}],
                                    style_header=table_style
                                ),
                            ],style={'width': '100%', 'float': 'right', 'display': 'inline-block','border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white'}),
                        ],style={'width': '27%', 'display': 'inline-block'}),

                        html.Div([
                            ### The Graph ### 
                            dcc.Graph(
                                id='unsupervised_detection_graph',style=graph_style
                            ),
                        ],style={'width': '70%', 'display': 'inline-block', 'float': 'right'}),
                        
                        ### The detection results as text ###
                    ],style={'padding': '10px 5px',"border":"2px black solid",'border-bottom':'2px white'}),
                ]),
                dcc.Tab(label='Supervised Detection', children=[
                    html.Div([
                   ### Graph to display classifier detection results using supervised training ###

                        html.H4('Supervised Detection'),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([html.B('Detector:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_detectors_supervised',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_supervised_detectors', 'detector_config')],
                                        value='iforest'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style={'width': '100%', 'display': 'inline-block'}),
                                html.Div([
                                    html.Div([html.B('Dataset:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_data_supervised',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets', 'dataset_config')],
                                        value='speed_7578'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style={'width': '100%', 'display': 'inline-block'}),
                                html.Div([
                                    html.Div([html.B('Split Ratio:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([
                                        dcc.Textarea(
                                            id='supervised_test_train_split_ratio',
                                            value='0.75',
                                            style={'width': '50%', 'height': '40%'},
                                        ),
                                    ],style={'width': '70%', 'display': 'inline-block'}),
                                ],style={'width': '100%', 'display': 'inline-block'}),
                            ],style=dropdown_box_style_full),
                            html.Div([
                                html.H4('Detection Results'),
                                html.Div(id='results_title_supervised', children='...'),
                                dash_table.DataTable(
                                    id='live_update_results_supervised',
                                    data = pd.DataFrame({'Evaluation_Metric':[],'Result':[]}).to_dict('records'),
                                    columns = [{'name':i, 'id':i} for i in {'Evaluation_Metric', 'Result'}],
                                    style_header=table_style
                                ),
                            ],style={'width': '100%', 'float': 'right', 'display': 'inline-block','border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white'}),
                        ],style={'width': '27%', 'display': 'inline-block'}),
                        
                        
                        html.Div([
                            ### The Graph ### 
                            dcc.Graph(
                                id='supervised_learning_graph',style=graph_style
                            ),
                        ],style={'width': '70%', 'display': 'inline-block', 'float': 'right'}),

                            ### The detection results as text ###
                        html.Div([
                            ### The Graph ### 
                            dcc.Graph(
                                id='supervised_train_test_graph',style=graph_style
                            ),
                        ],style={'width': '100%', 'display': 'inline-block', 'float': 'right','margin-top':'40px'})
                    ],style={'padding': '10px 5px',"border":"2px black solid",'border-bottom':'2px white'}),

                ]),
                #dcc.Tab(label='SOM', children=[
                #    ### Demonstration of SOM ####
#
#                    html.Div([
#                        html.Div(),
#                        html.H4("SOM"),
#                        html.H4("Demonstrating SOM outlier detection using 'Minisom' library."),
#                        html.Div([
#                            dcc.Graph(id = 'som-graph')
#                        ],style={'width': '49%', 'display': 'inline-block'}),
#                        html.Div([
#                            dcc.Graph(id = 'som-graph-2')
#                        ],style={'width': '49%', 'display': 'inline-block'}),
#                    ],style={"border":"2px black solid"}),
#                ]),

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
                        ],style={'width': '30%', 'float': 'left', 'display': 'inline-block','border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white','margin-right':'30px'}),
                        html.Div([
                            html.Div([
                                html.H4('Detection Results'),
                                #html.Div(id='unsupervised_detection_results_title', children='...'),
                                dash_table.DataTable(
                                    id='update_results_ensemble',
                                    data = pd.DataFrame({'Evaluation_Metric':[],'Result':[]}).to_dict('records'),
                                    columns = [{'name':i, 'id':i} for i in {'Evaluation_Metric', 'Result'}],
                                    style_header=table_style
                                ),
                            ]),
                        ],style={'width': '30%', 'float': 'left', 'display': 'inline-block','border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white'}),
                        html.Div([
                            # Graph
                            dcc.Graph(id = 'ensemble-graph',style=graph_style),
                        ],style={'width': '100%', 'float': 'right', 'display': 'inline-block','margin-top':'40px'}),
                    ],style={"border-top":"2px black solid"}),
                ]),

                
                dcc.Tab(label='Cloud Resource Usage Experiment', children=[


                    ##################### CLOUD RESOURCE DATA TESTING SPACE ##########################

                    html.Div([
                        html.H4('Cloud Resource Experimental Space'),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Div([html.B('Detector:')],style={'width': '20%', 'display': 'inline-block'}),
                                        html.Div([dcc.Dropdown(
                                            id='available_detectors_cloud_resource_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                            value='moving_average'
                                        )],style={'width': '80%', 'display': 'inline-block'}),
                                    ],style={'width': '100%', 'display': 'inline-block'}),
                                    html.Div([
                                        html.Div([html.B('Dataset:')],style={'width': '20%', 'display': 'inline-block'}),
                                        html.Div([dcc.Dropdown(
                                            id='available_data_cloud_resource_data',
                                            options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_datasets_cloud_resource_data', 'dataset_config')],
                                            value='ec2_cpu_utilization_5f5533'
                                        )],style={'width': '80%', 'display': 'inline-block'}),
                                    ],style={'width': '100%', 'display': 'inline-block'}),
                                ],style=dropdown_box_style_full),
                                html.Div([
                                    html.H4('Detection Results'),
                                    html.Div(id='results_title_cloud_resource', children='...'),
                                    dash_table.DataTable(
                                        id='live_update_results_cloud_resource',
                                        data = pd.DataFrame({'Evaluation_Metric':[],'Result':[]}).to_dict('records'),
                                        columns = [{'name':i, 'id':i} for i in {'Evaluation_Metric', 'Result'}],
                                        style_header=table_style
                                    ),
                                ],style={'width': '100%', 'float': 'right', 'display': 'inline-block','border':'2px black solid', 'border-radius':'25px', 'padding': '10px', 'background-color':'white'}),
                                html.Div(),
                                html.Div(),
                            ],style={'width': '27%', 'display': 'inline-block'}),
                            html.Div([
                                dcc.Graph(
                                    id='graph_cloud_resource_data',style=graph_style
                                ),
                            ],style={'width': '70%', 'display': 'inline-block', 'float': 'right'}),
                        ],style={'border':'2px black solid','border-bottom':'2px white'}),
                ]),



                dcc.Tab(label='Dengue Fever Experiment', children=[
            
                    ##################### Dengue Fever Data DATA TESTING SPACE ##########################

                    html.Div([
                        html.H4('Dengue Fever Data Experimental Space'),
                            html.Div([

                                ### Drop down boxes with options for user ###

                                #### drop down box style for detector
                                html.Div([
                                    html.Div([html.B('Detector:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_detectors_health_data',
                                        options=[{'label': i[0], 'value': i[0]} for i in config_utlilities.get_config('available_detectors', 'detector_config')],
                                        value='full_ensemble'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style=dropdown_box_with_margin),

                                #### drop down box for datasets
                                html.Div([
                                    html.Div([html.B('Region:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_data_health_data',
                                        options=[{'label': i, 'value': i} for i in config_utlilities.get_config('available_datasets_health_data', 'dataset_config')[0]],
                                        value='AnGiang.xlsx'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                    html.Div([html.B('Dataset:')],style={'width': '20%', 'display': 'inline-block'}),
                                    html.Div([dcc.Dropdown(
                                        id='available_data_health_data_subsets',
                                        options=[{'label': i, 'value': i} for i in config_utlilities.get_config('available_datasets_health_data_subsets', 'dataset_config')[0]],
                                        value='Average_temperature'
                                    )],style={'width': '80%', 'display': 'inline-block'}),
                                ],style=dropdown_box_style),
                            ]),
                            html.Div([
                                ### The Graph ### 
                                dcc.Graph(
                                    id='dengue_fever_graph',style=graph_style
                                ),
                            ],style={'width': '70%', 'display': 'inline-block'}),

                        ],style={'padding': '10px 5px',"border":"2px black solid"}),
                ]),
            ]),
        ]),
    ],style=tab_style)
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
    ## return the figure
    fig = fig_generator.get_fig_plot_outliers(detection_data, data, 'moving ensemble')
    return fig


@app.callback(
    Output('update_results_ensemble', 'data'),
    [Input('ensemble-average-radio-btns','value'),
    Input('ensemble-median-radio-btns','value'),
    Input('ensemble-boxplot-radio-btns','value'),
    Input('ensemble-histogram-radio-btns','value'),
    Input('available_data_ensemble','value'),
    Input('ensemble-graph', 'figure')]
)
def update_results(average_rad, median_rad, boxplot_rad, histogram_rad, data, fig):
    return detection_helper.get_result_data('ensemble', data).to_dict('records')

###########################################################################
        

###########################################################################
##################### UNSUPERVISED DETECTION
@app.callback(
    Output('unsupervised_detection_results_title', 'children'),
    [Input('available_data','value'),
    Input('available_detectors','value'),
    Input('unsupervised_detection_graph', 'figure')]
)
def update_results_title(data, detector, fig):
    return html.H4(detector.upper() + ' on \'' + data + '\' data')


@app.callback(
    Output('unsupervised_detection_results', 'data'),
    [Input('available_data','value'),
    Input('available_detectors','value'),
    Input('unsupervised_detection_graph', 'figure')]
)
def update_results(data, detector, fig):
    return detection_helper.get_result_data(detector, data).to_dict('records')


@app.callback(
    Output('unsupervised_detection_graph', 'figure'),
    [Input('available_data','value'),
    Input('available_detectors','value')]
)
def plot_graph(data, detector):
    detection_data = detection_helper.get_detection_data_known_outliers(detector, data, config_utlilities.get_true_outliers(data), detection_helper.get_detector_threshold(detector))
    fig = fig_generator.get_fig_plot_outliers(detection_data, data, detector)
    return fig

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
    return html.B(detector.upper() + ' on \'' + data + '\' data')


@app.callback(
    Output('live_update_results_cloud_resource', 'data'),
    [Input('available_data_cloud_resource_data','value'),
    Input('available_detectors_cloud_resource_data','value'),
    Input('graph_cloud_resource_data', 'figure')]
)
def update_results(data, detector, fig):
    return detection_helper.get_result_data(detector, data).to_dict('records')

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
def update_supervised_learning_graph(data, detector, ratio):
    detection_data = detection_helper.get_detection_data_supervised(detector, data, config_utlilities.get_true_outliers(data), float(ratio))
    return fig_generator.get_fig_plot_outliers(detection_data, "speed_7578", "isolation forest", ratio)

@app.callback(
    Output('live_update_results_supervised', 'data'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_supervised_learning_results(data, detector, ratio, fig):
    return detection_helper.get_result_data(detector + '_' + str(ratio), data).to_dict('records')

@app.callback(
    Output('supervised_train_test_graph','figure'),
    [Input('available_data_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value'),
    Input('supervised_learning_graph', 'figure')]
)
def update_supervised_learning_graph(data, ratio, fig):
    return fig_generator.plot_iso_detection_data(float(ratio), data, config_utlilities.get_true_outliers(data))   

@app.callback(
    Output('results_title_supervised', 'children'),
    [Input('available_data_supervised','value'),
    Input('available_detectors_supervised','value'),
    Input('supervised_test_train_split_ratio', 'value')]
)
def update_results_title(data, detector, split):
    return html.B(detector.upper() + ' on \'' + data + '\' data with split ratio ' + str(split))

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
    Input('available_detectors_real_time_detection', 'value')]
)
def update_graph_scatter(n,dataset_name, detector_name):
    current_dataset = ''
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    print(current_dataset)
    if (dataset_name != current_dataset):
        reset_ques(dataset_name)
    cpu_usage = 0
    try:
        headers = {'Accept': 'application/json'}
        r = requests.get('http://localhost:8000/' + dataset_name + '/' + str(X[-1]+1), headers=headers,timeout=5)
        cpu_usage = r.json()['cpu_usage']
    except(requests.ConnectionError, requests.ConnectTimeout) as exception:
        print('Could not connect to server')

    time = datetime.now()

    X.append(X[-1]+1)
    Y.append(cpu_usage)
    XTime.append(time)
    confidence = detection_helper.get_real_time_prediction(detector_name, Y, dataset_name, time)
    if (confidence < 0):
        Outliers.append(True)
    else:
        Outliers.append(False)
    return fig_generator.get_stream_fig(Outliers, XTime, Y, detector_name + ' on ' + dataset_name)



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

@app.callback(
    Output('real_time_outlier_data', 'data'),
    [Input('graph-update', 'n_intervals')]
)
def get_outlier_data_table(n):
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    outlier_real_time_data = database_helper.get_real_time_detections_for_session(current_dataset)
    outlier_timestamp = []
    outlier_data = []
    for outlier in outlier_real_time_data:
        outlier_timestamp.append(outlier[2])
        outlier_data.append(outlier[3])
    outlier_df = pd.DataFrame({'timestamp':outlier_timestamp, 'data':outlier_data})
    return outlier_df.to_dict('records')

@app.callback(
    Output('cpu_usage_dataset_title', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_outlier_table_name(n):
    current_dataset = ''
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    return html.B(current_dataset + ' outliers detected')


@app.callback(
    Output('real_time_outlier_count', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_outlier_count(n):
    current_dataset = ''
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    outlier_real_time_data = database_helper.get_real_time_detections_for_session(current_dataset)
    return html.Div([
        html.B('Outlier Count'),
        html.H3(str(len(outlier_real_time_data)))
    ])


@app.callback(
    Output('real_time_data_behaviour_status', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_data_behaviour_status(n):
    i = len(Outliers)-1
    while i > max(len(Outliers)-10, 0):
        if Outliers[i]:
            return (html.B('Resource Usage Status'),
                html.H3('Alert',style={'color':'red'}))
        i-=1
    return html.B('Resource Usage Status'), html.H3('Normal',style={'color':'green'})



@app.callback(
    Output('real_time_data_outlier_status', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_outlier_status(n):
    i = len(Outliers)-1
    while i > max(len(Outliers)-10, 0):
        if Outliers[i]:
            return (html.B('Outlier detected',style={'color':'red'}), html.Br(),
                html.B('Time: ' + str(XTime[i].hour) + ':' + str(XTime[i].minute)), html.Br(),
                 html.B('CPU Usage: ' + str(Y[i])))
        i-=1
    return html.B('Outlier Status'), html.H3('N/A',style={'color':'green'})


@app.callback(
    Output('real_time_stream_last_update_time', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_last_update_time(n):
    return html.B('Last Update'), html.H3(str(XTime[len(XTime)-1].strftime('%H:%M.%S')))


@app.callback(
    Output('live-graph-update-title', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def update_live_graph_title(n):
    current_dataset = ''
    with open("temp_storage.txt", "r") as file:
        current_dataset = file.readline()
    return ('Real time detection on ' + current_dataset)


@app.callback(
    Output('real_time_stream_status', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def get_outlier_count(n):
    error = True
    try:
        headers = {'Accept': 'application/json'}
        r = requests.get('http://localhost:8000/' + 'ec2_cpu_utilization_5f5533' + '/' + '1', headers=headers,timeout=5)
        error = r.json()['error']
    except(requests.ConnectionError, requests.ConnectTimeout) as exception:
        print('Could not connect to server')

    if (error == False):
        return (html.B('Stream Status'), html.H3('LIVE',style={'color':'green'}))
    return (html.B('Stream Status'), html.H3('DOWN',style={'color':'red'}))


@app.callback(
    Output('real_time_stream_session_start', 'children'),
    [Input('session-restart-btn', 'n_clicks')]
)
def get_session_start_time(n):
    database_helper.reset_real_time_session_data()
    return (html.B('Session start'), html.H3(datetime.now().strftime('%H:%M.%S')))
    



if __name__ == '__main__':
    database_helper.create_database()
    app.run_server()