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


    

if __name__ == '__main__':
    unittest.main()