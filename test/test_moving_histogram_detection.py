import unittest
import pandas as pd
from app_helper_scripts.app_exceptions import InvalidStartIndexError
from ensemble_detectors.ensemble_shared_methods import shared_methods

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


    # TEST GET HISTOGRAM
    def test_get_histogram(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        subset = shared_methods.create_subset_dataframe(dataframe_renamed, 10, 0)
        histogram_data = moving_histogram_detection.get_histogram(subset['data'])
        self.assertIsNotNone(histogram_data)


    # TEST REAL TIME PREDICTION
    def test_detect_prediction_with_inlier(self):
        confidence_outlier = moving_histogram_detection.real_time_prediction(self.get_dummy_list(), 13)
        self.assertTrue(confidence_outlier > 0)


    # TEST DETECT HISTOGRAM OUTLIERS
    def test_detect_histogram_outliers(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers(3, 2, dataframe_renamed)
        self.assertIsNotNone(outliers)

    def test_detect_histogram_outliers_low_interval(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers(3, 1, dataframe_renamed)
        self.assertIsNotNone(outliers)

    def test_detect_histogram_outliers_invalid_threshold(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers(-3, 2, dataframe_renamed)
        self.assertEqual(0, len(outliers))

    def test_detect_histogram_outliers_invalid_dataset_size(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers(3, -2, dataframe_renamed)
        self.assertEqual(0, len(outliers))


    
    # TEST DETECT HISTOGRAM OUTLIERS CONFIDENCE
    def test_detect_histogram_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers_predictions_confidence(3, 2, dataframe_renamed)
        self.assertIsNotNone(outliers['confidence'])

    def test_detect_histogram_confidence_invalid_threshold(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers_predictions_confidence(-3, 2, dataframe_renamed)
        self.assertEqual(0, len(outliers))

    def test_detect_histogram_confidence_invalid_dataset_size(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_histogram_detection.detect_histogram_outliers_predictions_confidence(3, -2, dataframe_renamed)
        self.assertEqual(0, len(outliers))


    ## TEST IS OUTLIER
    def test_is_outlier(self):
        self.assertTrue(moving_histogram_detection.is_outlier(45, [45,67,89]))

    def test_is_outlier_not(self):
        self.assertFalse(moving_histogram_detection.is_outlier(33, [45,67,89]))


    

if __name__ == '__main__':
    unittest.main()