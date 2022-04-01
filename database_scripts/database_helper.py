import sqlite3
import os

database_prefix = 'database_scripts/'
database_name = 'detection_db'
schema_file = 'database_scripts/schema.sql'
db_file = database_prefix + database_name


class database_helper:

    def does_database_exist(filename):
        return os.path.exists(filename)

    def create_db_if_not_exists(db_name):
        if (database_helper.does_database_exist(db_name) == False):
            database_helper.create_database()

    def create_database():
        if database_helper.does_database_exist(db_file):
            print('Database already exists. Returning...')
            return
        
        with open(schema_file, 'r') as rf:
            # Read the schema from the file
            schema = rf.read()
        
        with sqlite3.connect(db_file) as conn:
            print('Created the connection!')
            # Execute the SQL query to create the table
            conn.executescript(schema)
            print('Created the Tables!')
        print('Closed the connection!')

    def get_data_from_table(table_name):
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("select * from " + table_name)
            for row in cursor.fetchall():
                print(row)

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
