import csv
import pandas as pd
from datetime import datetime

def get_data_for_test(requested_data):
        with open('test/test_resource/' + requested_data +'.csv','r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            points_x = []
            points_y = []
            for row in lines:
                try:
                    points_y.append(float(row[1]))
                    points_x.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    print("Error accessing data for resource")
            return pd.DataFrame({'timestamp':points_x,'data':points_y})