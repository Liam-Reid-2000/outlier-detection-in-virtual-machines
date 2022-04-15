import pandas as pd
import time
from app_helper_scripts.csv_helper import csv_helper
from ensemble_detectors.ensemble_voting import ensemble_voting
from ensemble_detectors.moving_average_detection import moving_average_detection
from ensemble_detectors.moving_median_detection import moving_median_detection
from ensemble_detectors.moving_boxplot import moving_boxplot_detection
from ensemble_detectors.moving_histogram_detection import moving_histogram_detection
from app_helper_scripts.detector_evaluation import detector_evaluation
from supervised_learning_detectors.isolation_forest import do_isolation_forest_detection
from unsupervised_detectors.pycaret_detection import detect_outliers_with_pycaret


class detection_runner:

    def detect_in_real_time(detector_name, Y):
        confidence = 0
        if (detector_name == 'moving_average'):
            confidence = moving_average_detection.real_time_prediction(Y, Y[len(Y)-1])
        elif (detector_name == 'moving_median'):
            confidence = moving_median_detection.real_time_prediction(Y, Y[len(Y)-1])
        elif (detector_name == 'moving_boxplot'):
            confidence = moving_boxplot_detection.real_time_prediction(Y, Y[len(Y)-1])
        elif (detector_name == 'moving_histogram'):
            confidence = moving_histogram_detection.real_time_prediction(Y, Y[len(Y)-1])
        else: # FULL ENSEMBLE
            confidence += moving_average_detection.real_time_prediction(Y, Y[len(Y)-1])
            confidence += moving_median_detection.real_time_prediction(Y, Y[len(Y)-1])
            confidence += moving_boxplot_detection.real_time_prediction(Y, Y[len(Y)-1])
            confidence += moving_histogram_detection.real_time_prediction(Y, Y[len(Y)-1])
        return confidence


    def run_detection(detector_name, data_coordinates, threshold, interval=10):
        if (int(threshold)<0 or int(interval) <0):
            print('Invalid parameters passed for: ' + detector_name)
            return
        points_x = data_coordinates['timestamp']
        points_y = data_coordinates['data']
        if len(points_x)==0:
            print('Error: Data coordinates passed do not contain data')
            return
        data_coordinates_renamed = pd.DataFrame({'points_x': points_x,'points_y': points_y})

        outliers_x = []
        outliers_y = []
        if (detector_name == 'moving_average'):
            outliers_ = moving_average_detection.detect_average_outliers(threshold, moving_average_detection.get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
            outliers_x = outliers_['timestamp']
            outliers_y = outliers_['data']
        elif (detector_name == 'moving_median'):
            outliers_ = moving_median_detection.detect_median_outliers(threshold, moving_median_detection.get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
            outliers_x = outliers_['timestamp']
            outliers_y = outliers_['data']
        elif (detector_name == 'moving_boxplot'):
            outliers_ = moving_boxplot_detection.detect_boxplot_outliers(threshold, interval, data_coordinates_renamed)
            outliers_x = outliers_['timestamp']
            outliers_y = outliers_['data']
        elif (detector_name == 'moving_histogram'):
            outliers_ = moving_histogram_detection.detect_histogram_outliers(threshold,1, data_coordinates_renamed)
            outliers_x = outliers_['timestamp']
            outliers_y = outliers_['data']
        elif (detector_name == 'full_ensemble'):
            #ensemble_outliers = []
            #ensemble_outliers.append(detect_average_outliers(threshold, get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            #ensemble_outliers.append(detect_median_outliers(threshold, get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            #ensemble_outliers.append(detect_boxplot_outliers(threshold, interval, data_coordinates_renamed))
            #ensemble_outliers.append(detect_histogram_outliers(1,1, data_coordinates_renamed))
            #outliers_after_voting = get_ensemble_result(ensemble_outliers, 4)
            #outliers_x = outliers_after_voting['timestamp']
            #outliers_y = outliers_after_voting['data']

            ensemble_outliers_confidence = []
            ensemble_outliers_confidence.append(moving_average_detection.detect_average_outliers_labelled_prediction(threshold, moving_average_detection.get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_median_detection.detect_median_outliers_labelled_prediction(threshold, moving_median_detection.get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_boxplot_detection.detect_boxplot_outliers_predictions_confidence(threshold, interval, data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_histogram_detection.detect_histogram_outliers_predictions_confidence(1,1, data_coordinates_renamed))
            outliers_after_voting = ensemble_voting.get_ensemble_result_confidence(ensemble_outliers_confidence)
            outliers_x = outliers_after_voting['timestamp']
            outliers_y = outliers_after_voting['data']
        else:
            try:
                outliers_ = detect_outliers_with_pycaret(detector_name, data_coordinates)
                outliers_x = outliers_['timestamp']
                outliers_y = outliers_['data']
            except:
                print('Error: Detector does not exist')
                return
        outliers = pd.DataFrame({'timestamp': outliers_x,'data': outliers_y})

        return detection_data_collector.collect_detection_data(outliers, points_x, points_y)


    def run_detection_supervised_model(detector, data_to_run, true_outliers_csv, split_ratio):  
        data_coordinates = csv_helper.load_data_coordinates(data_to_run)
        tic = time.perf_counter()
        outliers = do_isolation_forest_detection(split_ratio, data_coordinates, true_outliers_csv)
        toc = time.perf_counter()
        detection_time = toc - tic
        return detection_data_collector.collect_detection_data_for_database(detector + '_' + str(split_ratio), data_to_run, outliers, true_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'], detection_time)


    def split_data_to_months(timestamps, data):
        data_split_to_months_x = []
        data_split_to_months_y = []
        i = 0
        while i < 12:
            arr = []
            data_split_to_months_x.append(arr)
            arrtoo = []
            data_split_to_months_y.append(arrtoo)
            i += 1

        i = 0
        while i < len(timestamps):
            data_split_to_months_x[timestamps[i].month-1].append(timestamps[i])
            data_split_to_months_y[timestamps[i].month-1].append(data[i])
            i += 1

        # list of data frames
        separated_months_as_dataframes = []
        i = 0
        while i < len(data_split_to_months_x):
            df = pd.DataFrame({'timestamp':data_split_to_months_x[i], 'data':data_split_to_months_y[i]})
            separated_months_as_dataframes.append(df)
            i += 1
        return separated_months_as_dataframes


    def run_detection_months(detector_name, data_coordinates, threshold, interval=7):
        if (threshold<=0 or interval<=0):
            print('invalid parameters passed')
            return
        separated_months_as_dataframes = detection_runner.split_data_to_months(data_coordinates['timestamp'], data_coordinates['data'])
        all_outliers_x = []
        all_outliers_y = []
        for i in separated_months_as_dataframes:
            detection_data = detection_runner.run_detection(detector_name, i, threshold, interval)
            for j in detection_data[2]:
                all_outliers_x.append(j)
            for j in detection_data[3]:
                all_outliers_y.append(j)
        all_outliers_df = pd.DataFrame({'timestamp':all_outliers_x,'data':all_outliers_y})
        return detection_data_collector.collect_detection_data(all_outliers_df, data_coordinates['timestamp'], data_coordinates['data'])
    

    def run_detection_known_outliers(detector, data_to_run, true_outliers_csv, threshold, interval=10):
        if (int(threshold)<0 or int(interval)<0):
            print('Error: Invalid parameters passed')
            return
        data_coordinates = csv_helper.load_data_coordinates(data_to_run)
        tic = time.perf_counter()
        detection_data = detection_runner.run_detection(detector, data_coordinates, threshold)
        toc = time.perf_counter()
        detection_time = toc - tic
        outliers_df = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})

        return detection_data_collector.collect_detection_data_for_database(detector, data_to_run, outliers_df, true_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'], detection_time)


class detection_data_collector:
    def collect_detection_data_for_database(detector, data, outliers_df, true_outliers_csv_reference, points_x_passed, points_y_passed, detection_time):
        detection_data = []
        outliers_x_detected = outliers_df['timestamp']

        classification_outcomes = detector_evaluation(true_outliers_csv_reference, points_x_passed, outliers_x_detected)
        result_data = classification_outcomes.get_detector_classification_evalutaion_data()

        detection_data.append(detector)
        detection_data.append(data)
        detection_data.append(result_data[0])
        detection_data.append(result_data[1])
        detection_data.append(result_data[2])
        detection_data.append(result_data[3])
        detection_data.append(result_data[4])
        detection_data.append(detection_time)

        return detection_data

    def collect_detection_data(outliers_df, points_x, points_y):
        detection_data = []
        detection_data.append(points_x)
        detection_data.append(points_y)
        detection_data.append(outliers_df['timestamp'])
        detection_data.append(outliers_df['data'])
        return detection_data