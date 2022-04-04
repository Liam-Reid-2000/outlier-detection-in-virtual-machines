import json

class config_utlilities:

    def get_config(requested_config, config_file_name):
        f = open('resources/'+ config_file_name +'.json',)
        data = json.load(f) 
        requested_config_list = []
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