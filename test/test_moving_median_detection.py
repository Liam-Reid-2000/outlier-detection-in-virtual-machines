import unittest
import pandas as pd

from ensemble_detectors.moving_median_detection import moving_median_detection
from test.test_utilitiy import get_data_for_test

class moving_median_detection_test(unittest.TestCase):

    def get_dummy_list(self):
        list_data_points =[]
        i = 0
        while i < 20:
            list_data_points.append(15)
            list_data_points.append(12)
            list_data_points.append(18)
            i += 1
        return list_data_points

    # TEST REAL TIME DETECTION
    def test_detect_prediction_with_outlier(self):
        confidence_outlier = moving_median_detection.real_time_prediction(self.get_dummy_list(), 50)
        self.assertTrue(confidence_outlier < 0)

    def test_detect_prediction_with_inlier(self):
        confidence_outlier = moving_median_detection.real_time_prediction(self.get_dummy_list(), 13)
        self.assertTrue(confidence_outlier > 0)

    
    # TEST GET MEDIAN
    def test_get_median(self):
        points = []
        points.append(10)
        points.append(20)
        points.append(40)
        points.append(50)
        median = moving_median_detection.get_median(points)
        self.assertEqual(30, median)
    
    def test_get_median_empty_data(self):
        points = []
        median = moving_median_detection.get_median(points)
        self.assertEqual(0, median)


    # TEST GET MOVING MEDIAN COORDINATES
    def test_get_moving_median_coordinates(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        median_coordinates = moving_median_detection.get_moving_median_coordinates(10, pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']}))
        self.assertIsNotNone(median_coordinates['points_median_x'])
        self.assertIsNotNone(median_coordinates['points_median_y'])

    
    # TEST DETECT MEDIAN OUTLIERS
    def test_detect_median_outliers(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        median_coordinates = moving_median_detection.get_moving_median_coordinates(10, dataframe_renamed)
        outliers = moving_median_detection.detect_median_outliers(10, median_coordinates, dataframe_renamed)
        self.assertIsNotNone(outliers['timestamp'])
        self.assertIsNotNone(outliers['data'])

    
    # TEST DETECT MEDIAN OUTLIERS CONFIDENCE
    def test_detect_median_outliers_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        median_coordinates = moving_median_detection.get_moving_median_coordinates(10, dataframe_renamed)
        outliers = moving_median_detection.detect_median_outliers_labelled_prediction(10, median_coordinates, dataframe_renamed)
        self.assertIsNotNone(outliers['timestamp'])
        self.assertIsNotNone(outliers['data'])
        self.assertIsNotNone(outliers['confidence'])

if __name__ == '__main__':
    unittest.main()