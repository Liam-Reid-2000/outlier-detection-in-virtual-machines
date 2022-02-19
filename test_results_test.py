import unittest
import csv
import datetime

from app_helper_scripts.display_results import display_results

class outlier_detection_test(unittest.TestCase):


    # Test method
    def test_upper(self):
        try:
            file = open ('test/test_resource/results_test_data.csv')
        except:
            print('Error')
        csvreader = csv.reader(file)
        test_data = []
        for row in csvreader:
            test_data.append(row)

        points_x_raw = test_data[0]
        outliers_x_detected_raw = test_data[1]

        points_x = []
        for i in points_x_raw:
            points_x.append(datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))

        outliers_x_detected = []
        for i in outliers_x_detected_raw:
            outliers_x_detected.append(datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))

        outliers_x = []
        outliers_x.append(outliers_x_detected)

        results = display_results('realTraffic/speed_7578.csv', points_x, outliers_x)

        correct_results = []
        correct_results.append(0.90150842945874)
        correct_results.append(1.0)
        correct_results.append(0.543859649122807)
        correct_results.append(0.7045454545454546)

        self.assertEqual(correct_results, results.display_results())


if __name__ == '__main__':
    unittest.main()