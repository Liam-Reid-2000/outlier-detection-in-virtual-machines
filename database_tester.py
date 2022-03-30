from app_helper_scripts.app_helper import get_detection_data_known_outliers, get_detector_threshold, get_outlier_ref, is_data_generated, load_generated_data_from_database
from database_scripts.database_helper import database_helper

database_helper.create_database()

detector = "moving_median"
data = "speed_7578"

get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))

print('finito')

print('detection')
for row in database_helper.execute_query("select * from detection"):    
    print(row)

print('tp')
for row in database_helper.execute_query("select * from true_positives"):    
    print(row)

print('fp')
for row in database_helper.execute_query("select * from false_positives"):    
    print(row)

print('fn')
for row in database_helper.execute_query("select * from false_negatives"):    
    print(row)


print('loading data')
load_generated_data_from_database(detector, data)

print (is_data_generated('liam', 'reid'))