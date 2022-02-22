import pandas as pd
from pycaret.anomaly import *

def detect_outliers_with_pycaret(model, data_coordinates):
    points_x = data_coordinates['timestamp']
    points_y = data_coordinates['data']

    data = pd.DataFrame({'timestamp': points_x,
                    'data': points_y})
    data.set_index('timestamp', drop=True, inplace=True)
    data['day'] = [i.day for i in data.index]
    data['day_name'] = [i.day_name() for i in data.index]
    data['day_of_year'] = [i.dayofyear for i in data.index]
    data['week_of_year'] = [i.weekofyear for i in data.index]
    data['hour'] = [i.hour for i in data.index] # only use this for speed data, commetn rest
    data['is_weekday'] = [i.isoweekday() for i in data.index]
    data.head()

    s = setup(data, session_id = 123, silent = True)
    myModel = create_model(model, fraction = 0.05)#, fraction = outlierCount/len(points_x))

    myModel_results = assign_model(myModel)
    myModel_results.head()
    myModel_results[myModel_results['Anomaly'] == 1].head()
    outlier_dates = myModel_results[myModel_results['Anomaly'] == 1].index
    y_values = [myModel_results.loc[i]['data'] for i in outlier_dates]

    outliers = pd.DataFrame({'timestamp': outlier_dates,
                    'data': y_values})

    return outliers