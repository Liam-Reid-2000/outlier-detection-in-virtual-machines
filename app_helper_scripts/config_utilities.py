import json
from os import path

class config_utlilities:

    def does_path_exist(path_name):
        return path.exists(path_name)


    def get_config(requested_config, config_file_name):
        path_name = 'resources/'+ config_file_name +'.json'
        if (config_utlilities.does_path_exist(path_name) == False):
            print('Could not find requested JSON')
            return []
        f = open(path_name)
        data = json.load(f) 
        requested_config_list = []
        if (requested_config not in data):
            print('Could not find requested config in JSON')
            return []
        for i in data[requested_config]:
            requested_config_list.append(i)
        # Closing file
        f.close()
        return requested_config_list



    def get_true_outliers(ref):
        f = open('resources/dataset_config.json',)
        data = json.load(f)
        for i in data['available_datasets']:
            if (i[0] ==ref):
                f.close()
                return i[1]
        for i in data['available_datasets_cloud_resource_data']:
            if (i[0] ==ref):
                f.close()
                return i[1]
        f.close()