import unittest
import pandas as pd
from app_helper_scripts.app_exceptions import InvalidValueForCalculationError

from ensemble_detectors.moving_boxplot import moving_boxplot_detection
from test.test_utilitiy import get_data_for_test

class moving_boxplot_detection_detection_test(unittest.TestCase):

    def get_dummy_list(self):
        list_data_points =[]
        i = 0
        while i < 20:
            list_data_points.append(1)
            list_data_points.append(5)
            list_data_points.append(8)
            i += 1
        return list_data_points

    # TEST REAL TIME PREDICTION
    def test_detect_prediction_with_inlier(self):
        confidence_inlier = moving_boxplot_detection.real_time_prediction(self.get_dummy_list(), 13)
        self.assertTrue(confidence_inlier > 0)

    def test_detect_prediction_with_outlier(self):
        confidence_outlier = moving_boxplot_detection.real_time_prediction(self.get_dummy_list(), 200)
        self.assertTrue(confidence_outlier < 0)


    # TEST CREATE SUBSET
    def test_create_subset_dataframe(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        subset = moving_boxplot_detection.create_subset_dataframe(dataframe_renamed, 10, 0)
        self.assertEqual(10, len(subset))


    # TEST DETECT BOXPLOT OUTLIERS
    def test_detect_boxplot_outliers(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers(3, 10, dataframe_renamed)
        self.assertIsNotNone(outliers)

    def test_detect_boxplot_outliers_invalid_threshold(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers(-3, 10, dataframe_renamed)
        self.assertEqual(0, len(outliers))

    def test_detect_boxplot_outliers_invalid_dataset_size(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers(3, -10, dataframe_renamed)
        self.assertEqual(0, len(outliers))

    
    # TEST DETECT BOXPLOT OUTLIERS
    def test_detect_boxplot_outliers_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers_predictions_confidence(3, 10, dataframe_renamed)
        self.assertIsNotNone(outliers['confidence'])

    def test_detect_boxplot_outliers_invalid_threshold_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers_predictions_confidence(-3, 10, dataframe_renamed)
        self.assertEqual(0, len(outliers))

    def test_detect_boxplot_outliers_invalid_dataset_size_confidence(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        outliers = moving_boxplot_detection.detect_boxplot_outliers_predictions_confidence(3, -10, dataframe_renamed)
        self.assertEqual(0, len(outliers))


    # TEST CALCULATE LOWER BOUND
    def test_calculate_lower_bound(self):
        lower_bound = moving_boxplot_detection.calculate_lower_bound(20, 5, 2)
        self.assertEqual(10, lower_bound)

    def test_calculate_lower_bound_high_iqr(self):
        lower_bound = moving_boxplot_detection.calculate_lower_bound(20, 10, 5)
        self.assertEqual(0, lower_bound)

    def test_calculate_lower_bound_negative_iqr(self):
        with self.assertRaises(InvalidValueForCalculationError):
            moving_boxplot_detection.calculate_lower_bound(70, -10, 5)

    def test_calculate_lower_bound_negative_threshold(self):
        with self.assertRaises(InvalidValueForCalculationError):
            moving_boxplot_detection.calculate_lower_bound(70, 10, -5)

    
    # TEST CALCULATE CONFIDENCE
    def test_calculate_confidence_outliers(self):
        confidence = moving_boxplot_detection.calculate_confidence(100, 20, 80, 40, 60)
        self.assertTrue(confidence < 0)
        confidence = moving_boxplot_detection.calculate_confidence(10, 20, 80, 40, 60)
        self.assertTrue(confidence < 0)

    def test_calculate_confidence_inliers(self):
        confidence = moving_boxplot_detection.calculate_confidence(50, 20, 80, 40, 60)
        self.assertTrue(confidence > 0)

if __name__ == '__main__':
    unittest.main()