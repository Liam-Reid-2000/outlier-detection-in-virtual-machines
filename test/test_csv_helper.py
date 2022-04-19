import csv
import unittest

from app_helper_scripts.csv_helper import csv_helper

class csv_test(unittest.TestCase):

    # TEST LOAD CSV HELPER
    def test_load_data_coordinates_valid_dataset(self):
        data = csv_helper.load_data_coordinates('speed_7578')
        self.assertTrue(len(data['timestamp'])>0)
        self.assertTrue(len(data['data'])>0)

    def test_load_data_coordinates_valid_dataset_cloud(self):
        data = csv_helper.load_data_coordinates('ec2_cpu_utilization_5f5533')
        self.assertTrue(len(data['timestamp'])>0)
        self.assertTrue(len(data['data'])>0)

    def test_load_data_coordinates_invalid_dataset(self):
        data = csv_helper.load_data_coordinates('invalid_dataset_name')
        self.assertTrue(len(data['timestamp'])==0) #should return empty dataframe
        self.assertTrue(len(data['data'])==0)

    # TEST WRITE DATA
    def test_write_to_csv(self):
        data = ['test_data', 'test_data']
        csv_helper.write_to_csv('test/test_resource/test_write.csv', data,'w')
        with open('test/test_resource/test_write.csv','r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                self.assertEqual('test_data', row[0])


if __name__ == '__main__':
    unittest.main()