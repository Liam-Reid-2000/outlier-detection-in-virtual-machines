import unittest
import pandas as pd

from ensemble_detectors.moving_average_detection import moving_average_detection
from test.test_utilitiy import get_data_for_test

class moving_average_detection_test(unittest.TestCase):

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
        confidence_outlier = moving_average_detection.real_time_prediction(self.get_dummy_list(), 50)
        self.assertTrue(confidence_outlier < 0)

    def test_detect_prediction_with_inlier(self):
        confidence_outlier = moving_average_detection.real_time_prediction(self.get_dummy_list(), 13)
        self.assertTrue(confidence_outlier > 0)

    
    # TEST GET AVERAGE
    def test_get_average(self):
        points = []
        points.append(10)
        points.append(20)
        points.append(40)
        points.append(50)
        average = moving_average_detection.get_average(points)
        self.assertEqual(30, average)
    
    def test_get_average_empty_data(self):
        points = []
        average = moving_average_detection.get_average(points)
        self.assertEqual(0, average)


    # TEST GET MOVING AVERAGE COORDINATES
    def test_get_moving_average_coordinates(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        average_coordinates = moving_average_detection.get_moving_average_coordinates(10, pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']}))
        self.assertIsNotNone(average_coordinates['points_average_x'])
        self.assertIsNotNone(average_coordinates['points_average_y'])

    
    # TEST DETECT AVERAGE OUTLIERS
    def test_detect_average_outliers(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        average_coordinates = moving_average_detection.get_moving_average_coordinates(10, dataframe_renamed)
        outliers = moving_average_detection.detect_average_outliers(10, average_coordinates, dataframe_renamed)
        self.assertIsNotNone(outliers['timestamp'])
        self.assertIsNotNone(outliers['data'])

    
    # TEST DETECT AVERAGE OUTLIERS CONFIDENCE
    def test_detect_average_outliers_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        average_coordinates = moving_average_detection.get_moving_average_coordinates(10, dataframe_renamed)
        outliers = moving_average_detection.detect_average_outliers_labelled_prediction(10, average_coordinates, dataframe_renamed)
        self.assertIsNotNone(outliers['timestamp'])
        self.assertIsNotNone(outliers['data'])
        self.assertIsNotNone(outliers['confidence'])

if __name__ == '__main__':
    unittest.main()