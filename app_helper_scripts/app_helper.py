from app_helper_scripts.app_exceptions import InvalidPercentageFloatValueError, InvalidValueForCalculationError
from app_helper_scripts.metric_calculations import metric_calculations
from database_scripts.database_helper import database_helper
import json
from app_helper_scripts.app_detection import detection_runner
import pandas as pd

class detection_helper:
    """Methods to support detection of outliers."""

    def get_detector_threshold(ref):
        """Returns detector threshold from config using reference."""
        f = open('resources/config.json',)
        data = json.load(f)
        for i in data['available_detectors']:
            if (i[0] ==ref):
                f.close()
                return i[1]
        f.close()

    
    def get_evaluation_metrics_as_list(tp, fp, fn, tn, n):
        """Returns evaluation metrics calculated from confusion matrix data as list"""
        evaluation_metrics = []
        try:
            evaluation_metrics.append(metric_calculations.calculate_accuracy(tn, tp, n))    # Accuracy
            evaluation_metrics.append(metric_calculations.calulate_recall(tp, fn))          # Recall
            evaluation_metrics.append(metric_calculations.calculate_precision(tp, fp))      # Precision
            evaluation_metrics.append(metric_calculations.calculate_f1(metric_calculations.calculate_precision(tp, fp), 
                                                                        metric_calculations.calulate_recall(tp, fn)))  # F1 Score
        except(InvalidValueForCalculationError, InvalidPercentageFloatValueError):
            # Return empty list
            return evaluation_metrics
        return evaluation_metrics


    def get_result_data(detector_name, dataset_name):
        """Returns dataframe of evaluation metrics."""
        if database_helper.does_data_exist(detector_name, dataset_name) == False:
            print('ERROR: attemping to access database for ' + detector_name + ' ' + dataset_name)
            return pd.DataFrame({'Evaluation_Metric':['No data generated','This could take several minutes'],'Result':['n/a','n/a']})
        detection_data = database_helper.load_generated_data_from_database(detector_name, dataset_name)
        tp = len(detection_data[2])
        fp = len(detection_data[3])
        fn = len(detection_data[4])
        tn = detection_data[5][0]
        n = detection_data[6][0]
        detection_time = detection_data[7]
        evalution_metrics = detection_helper.get_evaluation_metrics_as_list(tp, fp, fn, tn, n)
        evaluation_output = []
        for metric in evalution_metrics:
            evaluation_output.append(str(round(metric*100,4))+'%\n')
        evaluation_output.append(str(round(float(detection_time),4))+' seconds\n')
        output_text = ['Accuracy','Recall','Precision','F1 Score','Detection Time']
        return pd.DataFrame({'Evaluation_Metric':output_text,'Result':evaluation_output})


    def get_detection_data(model, data_to_run, data_coordinates, threshold=0):
        return detection_runner.run_detection(model, data_coordinates, threshold)


    def get_detection_data_months(model, data_to_run, data_coordinates, threshold=2):
        return detection_runner.run_detection_months(model, data_coordinates, threshold)


    def get_detection_data_known_outliers(detector_name, dataset_name, target_data, threshold, interval=10):
        """
        Get detection data from database for labelled data.
        
        If data doesnt exist, perform detection and store detection data.

        """
        if database_helper.does_data_exist(detector_name, dataset_name):
            print('data exists')
            return database_helper.load_generated_data_from_database(detector_name, dataset_name)
        detection_data = detection_runner.run_detection_known_outliers(detector_name, dataset_name, target_data, threshold, interval)
        database_helper.save_generated_data(detection_data)
        return detection_data


    def get_real_time_prediction(detector_name, data_window, dataset_name, time):
        """Get a prediction in real time using a specified detector"""
        confidence =  detection_runner.detect_in_real_time(detector_name, data_window)
        if (confidence < 0):
            database_helper.store_real_time_outlier_in_database(dataset_name, time, data_window[len(data_window)-1])
        return confidence


    def get_detection_data_supervised(detector_name, dataset_name, true_outliers_csv, split_ratio):
        """
        Get detection data from database for supervised models.
        
        If data doesnt exist, perform detection and store detection data.
        
        """
        if database_helper.does_data_exist(detector_name + '_' + str(split_ratio), dataset_name):
            return database_helper.load_generated_data_from_database(detector_name + '_' + str(split_ratio), dataset_name)
        detection_data = detection_runner.run_detection_supervised_model(detector_name, dataset_name, true_outliers_csv, split_ratio)
        database_helper.save_generated_data(detection_data)
        return detection_data
