import unittest

from ensemble_detectors.moving_average_detection import moving_average_detection

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
    



    def test_is_data_outside_bounds(self):
        test_result = moving_average_detection.is_data_outside_bounds(1,3,1)
        self.assertEqual(True, test_result)

        test_result = moving_average_detection.is_data_outside_bounds(2,2,5)
        self.assertEqual(False, test_result)

        test_result = moving_average_detection.is_data_outside_bounds(7,2,2)
        self.assertEqual(True, test_result)
    

    

if __name__ == '__main__':
    unittest.main()