import unittest

from app_helper_scripts.config_utilities import config_utlilities

class config_utilities_test(unittest.TestCase):

    # TEST DOES_PATH_EXIST
    def test_does_path_exist_valid_path(self):
        self.assertTrue(config_utlilities.does_path_exist('resources/speed_7578.csv'))

    def test_does_path_exist_invalid_path(self):
        self.assertFalse(config_utlilities.does_path_exist('resources/invalid.csv'))


    # TEST GET_CONFIG
    def test_get_config_valid_values(self):
        requested_config = config_utlilities.get_config('available_datasets','dataset_config')
        self.assertEqual('speed_7578', requested_config[0][0])

    def test_get_config_invalid_file_name(self):
        requested_config = config_utlilities.get_config('available_datasets','invalid_config')
        self.assertTrue(len(requested_config) == 0)

    def test_get_config_invalid_config_name(self):
        requested_config = config_utlilities.get_config('invalid_datasets','dataset_config')
        self.assertTrue(len(requested_config) == 0)


    # TEST GET_TRUE_OUTLIERS
    def test_get_true_outliers_valid_reference(self):
        requested_outlier_data = config_utlilities.get_true_outliers('speed_7578')
        self.assertEqual(requested_outlier_data, 'realTraffic/speed_7578.csv')

    def test_get_true_outliers_valid_reference_cloud_resource_data(self):
        requested_outlier_data = config_utlilities.get_true_outliers('ec2_cpu_utilization_5f553')
        self.assertEqual(requested_outlier_data, 'realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv')

    def test_get_true_outliers_invalid_reference(self):
        requested_outlier_data = config_utlilities.get_true_outliers('invalid_7578')
        self.assertIsNone(requested_outlier_data)

if __name__ == '__main__':
    unittest.main()