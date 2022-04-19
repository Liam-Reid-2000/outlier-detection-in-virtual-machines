import unittest

import pandas as pd

from ensemble_detectors.ensemble_shared_methods import shared_methods
from test.test_utilitiy import get_data_for_test

class test_ensemble_shared_methods(unittest.TestCase):

    # TEST IS DATA OUTSIDE BOUND
    def test_is_data_outside_bounds(self):
        test_result = shared_methods.is_data_outside_bounds(1,3,1)
        self.assertEqual(True, test_result)

        test_result = shared_methods.is_data_outside_bounds(2,2,5)
        self.assertEqual(False, test_result)

        test_result = shared_methods.is_data_outside_bounds(7,2,2)
        self.assertEqual(True, test_result)

    # TEST CALCULATE OUTLIER CONFIDENCE
    def test_calculate_confidence_same_as_average(self):
        confidence = shared_methods.calculate_confidence_outlier(10,10,3)
        self.assertEqual(1.0, confidence)
    
    def test_calculate_confidence_different_than_average(self):
        confidence = shared_methods.calculate_confidence_outlier(10,15,10)
        self.assertEqual(0.5, confidence)


    # TEST FIND THRESHOLD
    def test_find_threshold(self):
        arr = []
        arr.append(5)
        arr.append(5)
        arr.append(15)
        arr.append(15)
        threshold = shared_methods.find_threshold(arr)
        self.assertEqual(5, threshold)

    def test_find_threshold_empty_values(self):
        arr = []
        threshold = shared_methods.find_threshold(arr)
        self.assertEqual(0, threshold)

    # TEST CREATE SUBSET
    def test_create_subset_dataframe(self):
        data_coordinates = get_data_for_test('test_data_coordinates')
        dataframe_renamed = pd.DataFrame({'points_x':data_coordinates['timestamp'],'points_y':data_coordinates['data']})
        subset = shared_methods.create_subset_dataframe(dataframe_renamed, 10, 0)
        self.assertEqual(10, len(subset))

if __name__ == '__main__':
    unittest.main()