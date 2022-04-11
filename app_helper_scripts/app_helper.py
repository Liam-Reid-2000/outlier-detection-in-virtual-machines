from app_helper_scripts.metric_calculations import metric_calculations
from database_scripts.database_helper import database_helper
import json
from dash import html
from app_helper_scripts.app_detection import detection_runner

class detection_helper:
    def get_detector_threshold(ref):
        f = open('resources/config.json',)
        data = json.load(f)
        for i in data['available_detectors']:
            if (i[0] ==ref):
                f.close()
                return i[1]
        f.close()


    def get_result_data(detector_name, dataset_name):
        if database_helper.does_data_exist(detector_name, dataset_name) == False:
            print('ERROR: attemping to access database for ' + detector_name + ' ' + dataset_name)
            return (html.B('No data generated yet - This could take several minutes'))
        
        detection_data = database_helper.load_generated_data_from_database(detector_name, dataset_name)

        tp = len(detection_data[2])
        fp = len(detection_data[3])
        fn = len(detection_data[4])
        tn = detection_data[5][0]
        n = detection_data[6][0]

        detection_time = detection_data[7]

        accuracy = metric_calculations.calculate_accuracy(tn, tp, n)
        recall = metric_calculations.calulate_recall(tp, fn)
        precision = metric_calculations.calculate_precision(tp, fp)
        f1 = metric_calculations.calculate_f1(precision, recall)

        output = []
        output.append('Accuracy: ' + str(round(float(accuracy)*100,4))+'%\n')
        output.append('Recall: ' + str(round(float(recall)*100,4))+'%\n')
        output.append('Precision: ' + str(round(float(precision)*100,4))+'%\n')
        output.append('F1 score: ' + str(round(float(f1)*100,4))+'%\n')
        output.append('Detection time: ' + str(round(float(detection_time),4))+' seconds\n')

        return (html.P([output[0],html.Br(),output[1],html.Br(),output[2],html.Br(),output[3],html.Br(),output[4]]))


    def get_detection_data(model, data_to_run, data_coordinates, threshold=0):
        return detection_runner.run_detection(model, data_coordinates, threshold)

    def get_detection_data_months(model, data_to_run, data_coordinates, threshold=2):
        return detection_runner.run_detection_months(model, data_coordinates, threshold)


    def get_detection_data_known_outliers(detector_name, dataset_name, target_data, threshold, interval=10):
        if database_helper.does_data_exist(detector_name, dataset_name):
            return database_helper.load_generated_data_from_database(detector_name, dataset_name)
        detection_data = detection_runner.run_detection_known_outliers(detector_name, dataset_name, target_data, threshold, interval)
        database_helper.save_generated_data(detection_data)
        return detection_data

    def get_real_time_prediction(detector_name, Y):
        return detection_runner.detect_in_real_time(detector_name, Y)

    def get_detection_data_supervised(detector_name, dataset_name, true_outliers_csv, split_ratio):
        if database_helper.does_data_exist(detector_name + '_' + str(split_ratio), dataset_name):
            return database_helper.load_generated_data_from_database(detector_name + '_' + str(split_ratio), dataset_name)
        detection_data = detection_runner.run_detection_supervised_model(detector_name, dataset_name, true_outliers_csv, split_ratio)
        database_helper.save_generated_data(detection_data)
        return detection_data
