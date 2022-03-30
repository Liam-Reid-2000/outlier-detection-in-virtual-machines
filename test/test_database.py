#database_helper.create_database()

#detector = "moving_median"
#data = "speed_7578"

#get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))

#print('finito')

#print('detection')
#for row in database_helper.execute_query("select * from detection"):    
#    print(row)

#print('tp')
#for row in database_helper.execute_query("select * from true_positives"):    
#    print(row)

#print('fp')
#for row in database_helper.execute_query("select * from false_positives"):    
#    print(row)

#print('fn')
#for row in database_helper.execute_query("select * from false_negatives"):    
#    print(row)



import unittest

from database_scripts.database_helper import database_helper

class database_test(unittest.TestCase):

    def test_can_connect_to_database(self):
        database_helper.create_database()


if __name__ == '__main__':
    unittest.main()