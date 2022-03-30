from app_helper_scripts.app_helper import get_detection_data_known_outliers, get_detector_threshold, get_outlier_ref
from database_scripts.database_helper import database_helper

#database_helper.create_database()
#database_helper.get_data_from_database('detection')

#database_helper.execute_query("select * from detection")

detector = "moving_average"
data = "speed_7578"

get_detection_data_known_outliers(detector, data, get_outlier_ref(data), get_detector_threshold(detector))

print('finito')

database_helper.execute_query("select * from detection")
latest_row_id_tuple = database_helper.execute_query_return_first_row("Select detection_id FROM detection ORDER BY detection_id DESC LIMIT 1")
print(latest_row_id_tuple[0])