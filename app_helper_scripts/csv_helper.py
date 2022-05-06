import csv
from datetime import datetime
import pandas as pd
from os.path import exists
import logging

logging.basicConfig(filename="app_logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class csv_helper:
    """Methods to aid in accessing csv files"""

    def write_to_csv(path, data, action):
        file = open(path,action,newline='')
        writer = csv.writer(file)
        writer.writerow(data)
        file.close()

    def load_data_coordinates(dataset_name):
        """Loads data coordinates and resturns them as dataframe"""
        path_to_data = 'resources/' + dataset_name + '.csv'
        if (exists(path_to_data) == False):
            path_to_data = 'resources/cloud_resource_data/'+dataset_name+'.csv'
        if (exists(path_to_data) == False):
            logger.error('Error: data could not be found')
            return pd.DataFrame({'timestamp':[],'data':[]})
        with open(path_to_data,'r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            points_x = []
            points_y = []
            for row in lines:
                try:
                    points_y.append(float(row[1]))
                    points_x.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    logger.error("Error accessing data for request: " + dataset_name)
            return pd.DataFrame({'timestamp':points_x,'data':points_y}) 