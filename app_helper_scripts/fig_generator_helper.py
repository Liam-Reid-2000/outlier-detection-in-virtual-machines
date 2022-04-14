import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app_helper_scripts.csv_helper import csv_helper
from supervised_learning_detectors.isolation_forest import do_isolation_forest_detection

class fig_generator:
    def get_fig(detection_data, dataset_name, detector):
        try:
            timeseries_data = pd.DataFrame({'timestamp': detection_data[0],'data': detection_data[1]})
            fig = px.line(timeseries_data, x='timestamp', y='data',title= dataset_name + ' Data against Time (Using '+detector+'-based outlier detection)')
            detected_outliers = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})
            fig.add_trace(go.Scatter(x=detected_outliers['timestamp'], y=detected_outliers['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))
            fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=dataset_name)

            return fig
        except:
            print('Error getting figure for ' + detector + ' on ' + dataset_name + 'data')


    def change_x_values_to_dates(points_x):
        x_as_dates = []
        for point_x in points_x:
            x_as_dates.append(datetime.datetime.strptime(str(point_x), '%Y-%m-%d %H:%M:%S'))
        return x_as_dates


    def get_coordinates_dataframe(all_points_x, all_points_y, points_x):
        points_y = []
        points_x_new = []
        if (len(points_x) > 0):
            this_point_x = points_x[0]
            try:
                for point_x in points_x:
                    this_point_x = point_x
                    index = all_points_x.index(datetime.datetime.strptime(str(point_x), '%Y-%m-%d %H:%M:%S'))
                    points_y.append(all_points_y[index])
                    points_x_new.append(all_points_x[index])
            except:
                print('ValueError: data not found to plot')
                points_x.remove(this_point_x)
            print(len(points_x))
            print(len(points_y))
        return pd.DataFrame({'timestamp': points_x_new,'data': points_y})


    def split_timeseries_data(points_x, points_y, split):
        data_size = len(points_x)
        data_split_point = round(float(data_size) * float(split))
        points_x_after_split = []
        points_y_after_split = []
        i = data_split_point
        while i < data_size:
            points_x_after_split.append(points_x[i])
            points_y_after_split.append(points_y[i])
            i += 1
        return pd.DataFrame({'timestamp':points_x_after_split,'data':points_y_after_split})


    def get_fig_plot_outliers(detection_data, data_to_run, model, split=0):
        timeseries_data = csv_helper.load_data_coordinates(data_to_run)
        if (split != 0):
            timeseries_data = fig_generator.split_timeseries_data(timeseries_data['timestamp'], timeseries_data['data'], split)
        points_x = timeseries_data['timestamp']
        points_y = timeseries_data['data']

        points_x = fig_generator.change_x_values_to_dates(points_x)

        fig = px.line(timeseries_data, x='timestamp', y='data',title= data_to_run + ' Data against Time (Using '+model+'-based outlier detection)')
        
        if len(detection_data) > 2:
            false_positives_x = detection_data[3]
            if len(false_positives_x) > 0:
                fp_df = fig_generator.get_coordinates_dataframe(points_x, points_y, fig_generator.change_x_values_to_dates(false_positives_x))
                fig.add_trace(go.Scatter(x=fp_df['timestamp'], y=fp_df['data'], mode='markers',name='False Positives', line=dict(color='red')))

            false_negatives_x = detection_data[4]
            if len(false_negatives_x) > 0:
                fn_df = fig_generator.get_coordinates_dataframe(points_x, points_y, fig_generator.change_x_values_to_dates(false_negatives_x))
                fig.add_trace(go.Scatter(x=fn_df['timestamp'], y=fn_df['data'], mode='markers',name='False Negatives', line=dict(color='black')))

            true_positives_x = detection_data[2]
            if len(true_positives_x) > 0:
                tp_df = fig_generator.get_coordinates_dataframe(points_x, points_y, fig_generator.change_x_values_to_dates(true_positives_x))
                fig.add_trace(go.Scatter(x=tp_df['timestamp'], y=tp_df['data'], mode='markers',name='True Positives', line=dict(color='green')))

        fig.update_layout(autotypenumbers='convert types', xaxis_title='timestamp', yaxis_title=data_to_run)

        return fig


    def get_stream_fig(Outliers, XTime, Y, title):
        outlier_indexes = []
        i = 0
        while i < len(Outliers):
            if Outliers[i]:
                outlier_indexes.append(i)
            i += 1
        outliers_x = []
        outliers_y = []
        for i in outlier_indexes:
            outliers_x.append(XTime[i])
            outliers_y.append(Y[i])
        fig = px.line(pd.DataFrame({'Timestamp': XTime,'CPU_Usage': Y}), x='Timestamp', y='CPU_Usage')
        fig.add_trace(go.Scatter(x=outliers_x, y=outliers_y, mode='markers',name='Outliers detected', line=dict(color='red')))
        fig.update_xaxes(range=[min(XTime),max(XTime)])
        fig.update_yaxes(range=[min(Y) - min(Y)*0.5,max(Y) + max(Y)*0.5])
        return fig


    def plot_iso_detection_data(split_ratio, dataset, outlier_ref):

        timeseries_data = csv_helper.load_data_coordinates(dataset)

        print(timeseries_data)

        supervised_training_data = do_isolation_forest_detection(split_ratio, timeseries_data, outlier_ref, plot=True)
        
        X_train = supervised_training_data[0]
        inliers_detected_x = supervised_training_data[1]
        inliers_detected_y = supervised_training_data[2]
        outliers_detected_x = supervised_training_data[3]
        outliers_detected_y = supervised_training_data[4]
   
        train_data_df = pd.DataFrame({'minutes': X_train[:, 0],'data': X_train[:, 1]})
        inliers_data_df = pd.DataFrame({'minutes': inliers_detected_x,'data':inliers_detected_y})
        outliers_data_df = pd.DataFrame({'minutes': outliers_detected_x,'data':outliers_detected_y})

        fig = px.scatter(train_data_df, x='minutes', y='data',title= 'Data against Time (Using supervised isolation forest based outlier detection)')
    
        fig.add_trace(go.Scatter(x=inliers_data_df['minutes'], y=inliers_data_df['data'], mode='markers',name='Inliers Detected', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=outliers_data_df['minutes'], y=outliers_data_df['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))

        return fig