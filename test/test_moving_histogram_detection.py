import unittest
import pandas as pd

from ensemble_detectors.moving_histogram_detection import moving_histogram_detection
from test.test_utilitiy import get_data_for_test

class moving_histogram_detection_test(unittest.TestCase):

    def get_dummy_list(self):
        list_data_points =[]
        i = 0
        while i < 20:
            list_data_points.append(1)
            list_data_points.append(5)
            list_data_points.append(8)
            list_data_points.append(20)
            list_data_points.append(30)
            i += 1
        return list_data_points

    
    # TEST CREATE SUBSET
    def test_create_subset(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        subset = moving_histogram_detection.create_subset(0, 10, data_coordinates['timestamp'], data_coordinates['data'])
        self.assertTrue(len(subset['timestamp'])==10)

    # TEST GET HISTOGRAM
    def test_get_histogram(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        subset = moving_histogram_detection.create_subset(0, 10, data_coordinates['timestamp'], data_coordinates['data'])
        histogram_data = moving_histogram_detection.get_histogram(subset['data'])
        self.assertIsNotNone(histogram_data)

    # TEST REAL TIME PREDICTION
    def test_detect_prediction_with_inlier(self):
        confidence_outlier = moving_histogram_detection.real_time_prediction(self.get_dummy_list(), 13)
        self.assertTrue(confidence_outlier > 0)


    

if __name__ == '__main__':
    unittest.main()