import unittest
from database_scripts.database_helper import database_helper

class database_test(unittest.TestCase):

    def add_detection_data(self):
        detection_data = []
        detection_data.append('test_detector')
        detection_data.append('test_dataset')
        detection_data.append([('2015-09-11 16:44:00'), ('2015-09-15 14:34:00'), ('2015-09-16 17:10:00')])
        detection_data.append([('2015-09-14 17:10:00'), ('2015-09-15 14:29:00'), ('2015-09-16 13:59:00'), ('2015-09-16 14:09:00'), ('2015-09-16 14:50:00'), ('2015-09-16 14:55:00'), ('2015-09-16 15:00:00'), ('2015-09-16 15:05:00'), ('2015-09-16 16:50:00'), ('2015-09-16 16:55:00'), ('2015-09-16 17:30:00')])
        detection_data.append(['2015-09-16 14:14:00'])
        detection_data.append([1113])
        detection_data.append([1127])
        detection_data.append(0.05880439)
        database_helper.save_generated_data(detection_data)

    @classmethod
    def setUpClass(cls):
        detection_data = []
        detection_data.append('test_detector')
        detection_data.append('test_dataset')
        detection_data.append([('2015-09-11 16:44:00'), ('2015-09-15 14:34:00'), ('2015-09-16 17:10:00')])
        detection_data.append([('2015-09-14 17:10:00'), ('2015-09-15 14:29:00'), ('2015-09-16 13:59:00'), ('2015-09-16 14:09:00'), ('2015-09-16 14:50:00'), ('2015-09-16 14:55:00'), ('2015-09-16 15:00:00'), ('2015-09-16 15:05:00'), ('2015-09-16 16:50:00'), ('2015-09-16 16:55:00'), ('2015-09-16 17:30:00')])
        detection_data.append(['2015-09-16 14:14:00'])
        detection_data.append([1113])
        detection_data.append([1127])
        detection_data.append(0.05880439)
        database_helper.save_generated_data(detection_data)

    def delete_row_added(self):
        database_helper.delete_data('test_detector', 'test_dataset')

    # TEST CAN CREATE AND CONNECT TO DATABASE
    def test_can_connect_to_database(self):
        database_helper.create_database()

    # TEST DOES DATABASE EXIST
    def test_does_database_exist_valid_name(self):
        self.assertTrue(database_helper.does_database_exist('database_scripts/detection_db'))

    def test_does_database_exist_invalid_name(self):
        self.assertFalse(database_helper.does_database_exist('database_scripts/invalid_db'))


    # TEST SAVE GENERATED DATA
    def test_save_generated_data(self):
        self.add_detection_data()
        # Check if data added
        rows_returned = database_helper.execute_query("SELECT * FROM DETECTION WHERE detector_name == \'test_detector\' AND dataset_name == \'test_dataset\';")
        self.assertEqual(1, len(rows_returned))
        # Try to add duplicate row to check if previous record deleted
        self.add_detection_data()
        rows_returned = database_helper.execute_query("SELECT * FROM DETECTION WHERE detector_name == \'test_detector\' AND dataset_name == \'test_dataset\';")
        self.assertEqual(1, len(rows_returned))

    
    # TEST LOAD GENERATED DATA FROM DATABASE
    def test_load_generated_data_from_database(self):
        detection_data = database_helper.load_generated_data_from_database('test_detector', 'test_dataset')
        self.assertEqual('test_detector', detection_data[0])
        self.assertEqual('test_dataset', detection_data[1])
    
    def test_load_generated_data_from_database_non_exisitng_data(self):
        detection_data = database_helper.load_generated_data_from_database('non_existing', 'non_existing')
        self.assertEqual(0, len(detection_data))

    
    # TEST GET PRIMARY KEY OF ADDED ROW
    def test_get_primary_key_of_added_row(self):
        key = database_helper.get_primary_key_of_added_row()
        self.assertIsNotNone(key)

    
    # TEST DOES DATA EXIST
    def test_does_data_exist(self):
        self.assertTrue(database_helper.does_data_exist('test_detector', 'test_dataset'))

    def test_does_data_exist_non_exisitng_data(self):
        self.assertFalse(database_helper.does_data_exist('does_not_exist', 'does_not_exist'))

    # TEST GET PRIMARY KEYS OF GENERATED DATA
    def test_get_primary_keys_of_generated_data(self):
        keys = database_helper.get_primary_keys_of_generated_data('test_detector', 'test_dataset')
        self.assertTrue(len(keys) > 0)

    def test_get_primary_keys_of_generated_data_wrong_keys(self):
        keys = database_helper.get_primary_keys_of_generated_data('does_not_exist', 'does_not_exist')
        self.assertTrue(len(keys) == 0)

    
    # TEST EXECUTE QUERY
    def test_execute_query(self):
        returned_rows =  database_helper.execute_query("SELECT * FROM DETECTION WHERE detector_name == \'test_detector\' AND dataset_name == \'test_dataset\';")
        self.assertTrue(len(returned_rows) > 0)

if __name__ == '__main__':
    unittest.main()