import sqlite3
import os

database_prefix = 'database_scripts/'
database_name = 'detection_db'
schema_file = 'database_scripts/schema.sql'
db_file = database_prefix + database_name


class database_helper:

    def does_database_exist(filename):
        return os.path.exists(filename)

    def create_database():
        db_file = database_prefix + database_name
        print('Starting creation')
        
        if database_helper.does_database_exist(db_file):
            print('Database already exists. Exiting...')
        
        with open(schema_file, 'r') as rf:
            # Read the schema from the file
            schema = rf.read()
        
        with sqlite3.connect(db_file) as conn:
            print('Created the connection!')
            # Execute the SQL query to create the table
            conn.executescript(schema)
            print('Created the Table! Now inserting')
            conn.executescript("""
                            insert into detection (detection_id, detector_name, dataset_name, fn_count, accuracy, precision, recall, f1)
                            values
                            (1, 'moving_average', 'speed_data', 2, 90.0, 50.0, 50.0, 50.0),
                            (2, 'moving_average', 'speed_data', 2, 90.0, 50.0, 50.0, 50.0),
                            (3, 'moving_average', 'speed_data', 2, 90.0, 50.0, 50.0, 50.0);
                            """)
            conn.executescript("""
                            insert into true_positives (tp_pk, detection_id, true_positive_datetime)
                            values
                            (1, 1, '2018-01-20'),
                            (2, 1, '2020-09-12'),
                            (3, 1, '2022-03-02');
                            """)
            print('Inserted values into the table!')
        print('Closed the connection!')

    def get_data_from_database(table_name):
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("select * from " + table_name)
            for row in cursor.fetchall():
                print(row)