import unittest
import pandas as pd
from app_helper_scripts.csv_helper import csv_helper

from supervised_learning_detectors.isolation_forest import *

class moving_average_detection_test(unittest.TestCase):

    def test_do_isolation_forest_detection(self):
        data_coordinates = csv_helper.load_data_coordinates('speed_7578')
        outliers_detected = do_isolation_forest_detection(0.5, data_coordinates, 'realTraffic/speed_7578.csv')
        self.assertIsNotNone(outliers_detected)

    def test_do_isolation_forest_detection_invlaid_ratio(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            do_isolation_forest_detection(1.2, 'test_dataset', 'test_outlier_ref')

if __name__ == '__main__':
    unittest.main()