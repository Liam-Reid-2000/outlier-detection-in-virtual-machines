import unittest
from datetime import datetime
import csv
import pandas as pd
from app_helper_scripts.app_detection import detection_runner

class app_detection_test(unittest.TestCase):

    def get_dummy_list(self, with_outlier):
        list_data_points =[]
        i = 0
        while i < 20:
            list_data_points.append(15)
            list_data_points.append(12)
            list_data_points.append(18)
            i += 1
        if (with_outlier):
            list_data_points.append(50)
        return list_data_points

    # TEST REAL TIME DETECTION
    def test_detect_real_time_moving_average(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_average', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)
    
    def test_detect_real_time_moving_median(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_median', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_moving_boxplot(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_boxplot', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_moving_histogram(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_histogram', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_full_ensemble(self):
        confidence_outlier = detection_runner.detect_in_real_time('full_ensemble', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_invalid_detector(self):
        confidence_outlier = detection_runner.detect_in_real_time('invalid_detector', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def get_data_for_test(self, requested_data):
        with open('test/test_resource/' + requested_data +'.csv','r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            points_x = []
            points_y = []
            for row in lines:
                try:
                    points_y.append(float(row[1]))
                    points_x.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    print("Error accessing data for resource")
            return pd.DataFrame({'timestamp':points_x,'data':points_y})
    
    # TEST RUN DETECTION
    def test_run_detection_moving_average(self):
        detection_data = detection_runner.run_detection('moving_average', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_moving_median(self):
        detection_data = detection_runner.run_detection('moving_median', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_moving_boxplot(self):
        detection_data = detection_runner.run_detection('moving_boxplot', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_moving_histogram(self):
        detection_data = detection_runner.run_detection('moving_histogram', self.get_data_for_test('test_data_coordinates'), threshold=1, interval=2)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_moving_median(self):
        detection_data = detection_runner.run_detection('moving_median', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_pycaret(self):
        detection_data = detection_runner.run_detection('svm', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNotNone(detection_data[2]) # The x outlier coordinates
        self.assertIsNotNone(detection_data[3]) # The y outlier coordinates

    def test_run_detection_non_exisiting_detector(self):
        detection_data = detection_runner.run_detection('invalid_detector', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=10)
        self.assertIsNone(detection_data)

    def test_run_detection_invalid_threshold(self):
        detection_data = detection_runner.run_detection('moving_average', self.get_data_for_test('test_data_coordinates'), threshold=-5, interval=10)
        self.assertIsNone(detection_data)

    def test_run_detection_invalid_interval(self):
        detection_data = detection_runner.run_detection('moving_average', self.get_data_for_test('test_data_coordinates'), threshold=5, interval=-10)
        self.assertIsNone(detection_data)


    # TEST SPLIT DATA TO MONTHS
    def test_split_data_to_months(self):
        data_coordinates = self.get_data_for_test('test_data_for_months')
        data_separated = detection_runner.split_data_to_months(data_coordinates['timestamp'], data_coordinates['data'])
        for data in data_separated:
            self.assertEqual(1, len(data['timestamp'])) # one for each month

    
    # TEST RUN DETECTION MONTHS
    def test_run_detection_months(self):
        detection_data = detection_runner.run_detection_months('moving_average', self.get_data_for_test('test_data_for_months'), threshold=5)
        self.assertIsNotNone(detection_data)

    def test_run_detection_months_invalid_threshold(self):
        detection_data = detection_runner.run_detection_months('moving_average', self.get_data_for_test('test_data_for_months'), threshold=-5)
        self.assertIsNone(detection_data)
    

    # TEST RUN DETECTION KNOWN OUTLEIRS
    def test_run_detection_known_outliers(self):
        detection_data = detection_runner.run_detection_known_outliers('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', threshold=5, interval=10)
        self.assertIsNotNone(detection_data)

    def test_run_detection_known_outliers_invalid_threshold(self):
        detection_data = detection_runner.run_detection_known_outliers('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', threshold=-5, interval=10)
        self.assertIsNone(detection_data)

    def test_run_detection_known_outliers_invalid_interval(self):
        detection_data = detection_runner.run_detection_known_outliers('moving_average', 'speed_7578', 'realTraffic/speed_7578.csv', threshold=5, interval=-10)
        self.assertIsNone(detection_data)

if __name__ == '__main__':
    unittest.main()