import sqlite3
import os

DATABASE_PREFIX = 'database_scripts/'
DATABASE_NAME = 'detection_db'
SCHEMA_FILE = 'database_scripts/schema.sql'
db_file = DATABASE_PREFIX + DATABASE_NAME


class database_helper:

    def does_database_exist(filename):
        return os.path.exists(filename)


    def create_database():
        if database_helper.does_database_exist(db_file):
            print('Database already exists. Returning...')
            return
        
        with open(SCHEMA_FILE, 'r') as rf:
            # Read the schema from the file
            schema = rf.read()
        
        with sqlite3.connect(db_file) as conn:
            print('Created the connection!')
            # Execute the SQL query to create the table
            conn.executescript(schema)
            print('Created the Tables!')
        print('Closed the connection!')


    def execute_query(query):
        with sqlite3.connect(db_file) as conn:
            #print('Created the connection!')
            cursor = conn.cursor()
            cursor.execute(query)
            rows = []
            for row in cursor.fetchall():
                rows.append(row)
            return rows


    def get_primary_key_of_added_row():
        primary_key_added_row = database_helper.execute_query("Select detection_id FROM detection ORDER BY detection_id DESC LIMIT 1")
        return(primary_key_added_row[0][0])


    def does_data_exist(detector_name, dataset_name):
        returned_data = database_helper.execute_query("SELECT * FROM DETECTION WHERE detector_name == \'" + detector_name + "\' AND dataset_name == \'" + dataset_name + "\';")
        if len(returned_data) > 0:
            return True
        return False


    def get_primary_keys_of_generated_data(detector_name, dataset_name):
        keys = []
        rows = database_helper.execute_query("SELECT * FROM DETECTION WHERE detector_name == \'" + detector_name + "\' AND dataset_name == \'" + dataset_name + "\';")
        for row in rows:
            keys.append(row[0])
        return keys


    def delete_data(detector_name, dataset_name):
        keys = database_helper.get_primary_keys_of_generated_data(detector_name, dataset_name)
        for key in keys:
            database_helper.execute_query("DELETE FROM detection WHERE detection_id == \'" + str(key) + "\';")
            database_helper.execute_query("DELETE FROM true_positives WHERE detection_id == \'" + str(key) + "\';")
            database_helper.execute_query("DELETE FROM false_positives WHERE detection_id == \'" + str(key) + "\';")
            database_helper.execute_query("DELETE FROM false_negatives WHERE detection_id == \'" + str(key) + "\';")

    
    def save_generated_data(detection_data):
        detector_name = detection_data[0]
        dataset_name = detection_data[1]
        true_positives = detection_data[2]
        false_positives = detection_data[3]
        false_negatives = detection_data[4]
        true_negative_count = detection_data[5][0]
        dataset_size = detection_data[6][0]
        detection_time = detection_data[7]

        # Delete previous detection data if exists
        if database_helper.does_data_exist(detector_name, dataset_name):
            database_helper.delete_data(detector_name, dataset_name)

        database_helper.execute_query('INSERT INTO DETECTION (detector_name, dataset_name, tn_count, data_size, detection_time) VALUES ' 
            + '(\''+ detector_name +'\', '
            + '\''+ dataset_name +'\', '
            + str(true_negative_count) + ', '
            + str(dataset_size) + ', '
            + str(detection_time) + ');')

        detection_key = database_helper.get_primary_key_of_added_row()
        for true_poitive in true_positives:
            database_helper.execute_query('INSERT INTO TRUE_POSITIVES (detection_id, true_positive_datetime) VALUES (' 
                + str(detection_key) + ', \'' + str(true_poitive) + '\');')
        for false_positive in false_positives:
            database_helper.execute_query('INSERT INTO FALSE_POSITIVES (detection_id, false_positive_datetime) VALUES (' 
                + str(detection_key) + ', \'' + str(false_positive) + '\');')
        for false_negative in false_negatives:
            database_helper.execute_query('INSERT INTO FALSE_NEGATIVES (detection_id, false_negative_datetime) VALUES (' 
                + str(detection_key) + ', \'' + str(false_negative) + '\');')


    def load_generated_data_from_database(detector_name, dataset_name):
        returned_detection_data = database_helper.execute_query('SELECT * FROM DETECTION WHERE detector_name == \'' + detector_name + '\' AND dataset_name == \'' + dataset_name + '\';')
        if (len(returned_detection_data) == 0):
            print('Error: Could not load data from database, data could not be found')
            return []
        returned_detection_data = returned_detection_data[0]
        key = returned_detection_data[0]
        true_negative_count = returned_detection_data[3]
        dataset_size = returned_detection_data[4]
        detection_time = returned_detection_data[5]

        true_positives = []
        for true_positive_row in database_helper.execute_query('SELECT * FROM TRUE_POSITIVES WHERE detection_id == ' + str(key)):
            true_positives.append(true_positive_row[2])
        false_positives = []
        for false_positive_row in database_helper.execute_query('SELECT * FROM FALSE_POSITIVES WHERE detection_id == ' + str(key)):
            false_positives.append(false_positive_row[2])
        false_negatives = []
        for false_negative_row in database_helper.execute_query('SELECT * FROM FALSE_NEGATIVES WHERE detection_id == ' + str(key)):
            false_negatives.append(false_negative_row[2])

        detection_data = []
        detection_data.append(detector_name)
        detection_data.append(dataset_name)
        detection_data.append(true_positives)
        detection_data.append(false_positives)
        detection_data.append(false_negatives)
        detection_data.append([true_negative_count])
        detection_data.append([dataset_size])
        detection_data.append(detection_time)

        return detection_data

    
    def store_real_time_outlier_in_database(session_name, outlier_datetime, outlier_data):
        rows_returned = database_helper.execute_query('SELECT * FROM real_time_detection WHERE real_time_session_name == \'' + session_name + '\'')
        key = 0
        if len(rows_returned)>0:
            key = rows_returned[0][0]
        else:
            database_helper.execute_query('INSERT INTO real_time_detection (real_time_session_name) VALUES (\'' + session_name + '\');')
            key = database_helper.execute_query("Select real_time_session_id FROM real_time_detection ORDER BY real_time_session_id DESC LIMIT 1")[0][0]
        print('Attempting to execute query')
        print('INSERT INTO real_time_outliers (real_time_session_id, outlier_datetime, outlier_data) VALUES (' +
                str(key) + ', \'' + str(outlier_datetime) + '\', ' + str(outlier_data) + ');')
        database_helper.execute_query('INSERT INTO real_time_outliers (real_time_session_id, outlier_datetime, outlier_data) VALUES (' +
                str(key) + ', \'' + str(outlier_datetime) + '\', ' + str(outlier_data) + ');')

    
    def get_real_time_detections_for_session(session_name):
        key = database_helper.execute_query('Select real_time_session_id FROM real_time_detection WHERE real_time_session_name == \'' + session_name + '\' ORDER BY real_time_session_id DESC LIMIT 1')
        if len(key)!=0:
            if len(key[0])!=0:
                return database_helper.execute_query('SELECT * FROM real_time_outliers WHERE real_time_session_id == ' + str(key[0][0]))
        return []

    def reset_real_time_session_data():
        database_helper.execute_query('DELETE FROM real_time_detection')
        database_helper.execute_query('DELETE FROM real_time_outliers')
