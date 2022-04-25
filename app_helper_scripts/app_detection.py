import pandas as pd
import time
from app_helper_scripts.app_exceptions import InvalidValueForCalculationError
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
    """
    Runs detection on datasets.

    Most methods return lists of outliers or lists of detection data.
    """

    def detect_in_real_time(detector_name, data_window):
        """
        Give real time prediection.
    
        Args:
        detector_name (string): Name of detector selected to perform detection.
        data_window (array of floats): Data window to use for detection.
        
        Returns:
        float: Confidence score (negative = outlier) closer to 0 = less confident.
    
        """

        confidence = 0
        if (detector_name == 'moving_average'):
            confidence = moving_average_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
        elif (detector_name == 'moving_median'):
            confidence = moving_median_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
        elif (detector_name == 'moving_boxplot'):
            confidence = moving_boxplot_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
        elif (detector_name == 'moving_histogram'):
            confidence = moving_histogram_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
        else: # FULL ENSEMBLE
            confidence += moving_average_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
            confidence += moving_median_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
            confidence += moving_boxplot_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
            confidence += moving_histogram_detection.real_time_prediction(data_window, data_window[len(data_window)-1])
        return confidence


    def run_detection(detector_name, data_coordinates, threshold, interval=10, confidence_threshold=-0.4):
        """
        Detection outliers using specified detector.
    
        Args:
        detector_name (string): Name of detector selected to perform detection.
        data_coordinates (dataframe): Dataset used for detection.
        threshold (int): Threshold for detector.
        interval (int): window interval.
        confidence threshold (float): Confidence score of outliers.

        Returns:
        dataframe: cooridnates of outliers.

        Raises:
        InvalidValueForCalculationError: If any input variables are invalid.

        """
        print('threshold = ' + str(threshold))
        print('interval = ' + str(interval))
        print('conf thres = ' + str(confidence_threshold))
        if (int(threshold)<0 or int(interval) <0):
            raise(InvalidValueForCalculationError([threshold, interval]))
        points_x = data_coordinates['timestamp']
        points_y = data_coordinates['data']
        if len(points_x)==0:
            print('Error: Data coordinates passed do not contain data')
            return
        data_coordinates_renamed = pd.DataFrame({'points_x': points_x,'points_y': points_y})
        outliers = []
        if (detector_name == 'moving_average'):
            outliers = moving_average_detection.detect_average_outliers(threshold, moving_average_detection.get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
        elif (detector_name == 'moving_median'):
            outliers = moving_median_detection.detect_median_outliers(threshold, moving_median_detection.get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed)
        elif (detector_name == 'moving_boxplot'):
            outliers = moving_boxplot_detection.detect_boxplot_outliers(threshold, interval, data_coordinates_renamed)
        elif (detector_name == 'moving_histogram'):
            outliers = moving_histogram_detection.detect_histogram_outliers(threshold,1, data_coordinates_renamed)
        elif (detector_name == 'full_ensemble'):
            ensemble_outliers_confidence = []
            ensemble_outliers_confidence.append(moving_average_detection.detect_average_outliers_labelled_prediction(threshold, moving_average_detection.get_moving_average_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_median_detection.detect_median_outliers_labelled_prediction(threshold, moving_median_detection.get_moving_median_coordinates(interval, data_coordinates_renamed), data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_boxplot_detection.detect_boxplot_outliers_predictions_confidence(threshold, interval, data_coordinates_renamed))
            ensemble_outliers_confidence.append(moving_histogram_detection.detect_histogram_outliers_predictions_confidence(1,1, data_coordinates_renamed))
            outliers_after_voting = ensemble_voting.get_ensemble_result_confidence(ensemble_outliers_confidence, confidence_threshold)
            outliers = outliers_after_voting
        else:
            try:
                outliers = detect_outliers_with_pycaret(detector_name, data_coordinates)
            except:
                print('Error: Detector does not exist')
                return
        return detection_data_collector.collect_detection_data(outliers, points_x, points_y)


    def run_detection_supervised_model(detector, data_to_run, true_outliers_csv, split_ratio):
        """
        Run detection for supervised models.
    
        Args:
        detector (string): Name of detector selected to perform detection.
        data_to_run (dataframe): Dataset used for detection.
        true_outliers_csv (int): Location of where the true outliers for this data are stored.
        split_ratio (int): Ratio of test to train split.

        Returns:
        List: Contains the detection data and classifications.

        """  

        data_coordinates = csv_helper.load_data_coordinates(data_to_run)
        tic = time.perf_counter()
        outliers = do_isolation_forest_detection(split_ratio, data_coordinates, true_outliers_csv)
        toc = time.perf_counter()
        detection_time = toc - tic
        return detection_data_collector.collect_detection_data_for_database(detector + '_' + str(split_ratio), data_to_run, outliers, true_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'], detection_time)


    def split_data_to_months(timestamps, data):
        """
        Splits data into dataframes by month.
    
        Args:
        timestamps (date): Timestamp (x-coordinate).
        data (float): Data (y-coordinate).

        Returns:
        List: List of 12 dataframes

        """

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
        """
        Run detection for unlabelled data based on months.
    
        Args:
        detector (string): Name of detector selected to perform detection.
        data_to_run (dataframe): Dataset used for detection.
        true_outliers_csv (int): Location of where the true outliers for this data are stored.
        interval (int): Window interval.

        Returns:
        List: Contains the detection data and classifications.

        """
        if (threshold<=0 or interval<=0):
            print('invalid parameters passed')
            return
        separated_months_as_dataframes = detection_runner.split_data_to_months(data_coordinates['timestamp'], data_coordinates['data'])
        all_outliers_x = []
        all_outliers_y = []
        for i in separated_months_as_dataframes:
            detection_data = detection_runner.run_detection(detector_name, i, threshold, interval, confidence_threshold=0)
            for j in detection_data[2]:
                all_outliers_x.append(j)
            for j in detection_data[3]:
                all_outliers_y.append(j)
        all_outliers_df = pd.DataFrame({'timestamp':all_outliers_x,'data':all_outliers_y})
        return detection_data_collector.collect_detection_data(all_outliers_df, data_coordinates['timestamp'], data_coordinates['data'])
    

    def run_detection_known_outliers(detector, data_to_run, true_outliers_csv, threshold, interval=10):
        """
        Run detection for labelled datasets.
    
        Args:
        detector (string): Name of detector selected to perform detection.
        data_to_run (dataframe): Dataset used for detection.
        true_outliers_csv (int): Location of where the true outliers for this data are stored.
        interval (int): Window interval.

        Returns:
        List: Contains the detection data and classifications.

        """

        if (int(threshold)<0 or int(interval)<0):
            raise(InvalidValueForCalculationError([threshold, interval]))
        data_coordinates = csv_helper.load_data_coordinates(data_to_run)
        tic = time.perf_counter()
        detection_data = detection_runner.run_detection(detector, data_coordinates, threshold)
        toc = time.perf_counter()
        detection_time = toc - tic
        outliers_df = pd.DataFrame({'timestamp': detection_data[2],'data': detection_data[3]})
        return detection_data_collector.collect_detection_data_for_database(detector, data_to_run, outliers_df, true_outliers_csv, data_coordinates['timestamp'], data_coordinates['data'], detection_time)


class detection_data_collector:
    """
    Returns detection data as lists.

    Useful for passing large amounts of detection between methods/classes.

    """

    def collect_detection_data_for_database(detector, data, outliers_df, true_outliers_csv_reference, points_x_passed, points_y_passed, detection_time):
        """
        Collects data from arguments into a list ready to be saved to the database.

        Returns data as list.

        """
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
        """
        Collects coordinates and outliers.

        Returns them as list.

        """
        detection_data = []
        detection_data.append(points_x)
        detection_data.append(points_y)
        detection_data.append(outliers_df['timestamp'])
        detection_data.append(outliers_df['data'])
        return detection_data